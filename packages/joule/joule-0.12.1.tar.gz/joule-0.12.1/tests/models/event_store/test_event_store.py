import unittest
import testing.postgresql
import asyncpg
import random
import tempfile
import shutil
import os
import sys
import asyncio

from joule.models.data_store.event_store import EventStore, StreamInfo
from joule.models.event_stream import EventStream
from joule.utilities.time import human_to_timestamp as h2ts
from joule.utilities.time import timestamp_to_human as ts2h

SQL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'joule', 'sql')


class TestEventStore(unittest.IsolatedAsyncioTestCase):
    use_default_loop = False
    forbid_get_event_loop = True

    async def asyncSetUp(self):
        # set up the psql database
        self.psql_dir = tempfile.TemporaryDirectory()
        # run this asynchronously to avoid blocking the event loop
        def start_postgresql_instance():
            return testing.postgresql.Postgresql(base_dir=self.psql_dir.name)
        self.postgresql = await asyncio.to_thread(start_postgresql_instance)
        await asyncio.to_thread(self.postgresql.stop)

        # now that the directory structure is created, customize the *.conf file
        src = os.path.join(os.path.dirname(__file__), "postgresql.conf")
        dest = os.path.join(self.psql_dir.name, "data", "postgresql.conf")
        shutil.copyfile(src, dest)
        # restart the database
        self.postgresql = await asyncio.to_thread(start_postgresql_instance)

        self.db_url = self.postgresql.url()
        conn: asyncpg.Connection = await asyncpg.connect(self.db_url)
        await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE ")
        await conn.execute("CREATE USER joule_module")
        # load custom functions
        for file in os.listdir(SQL_DIR):
            file_path = os.path.join(SQL_DIR, file)
            with open(file_path, 'r') as f:
                await conn.execute(f.read())
        await conn.close()

    async def asyncTearDown(self):
        await asyncio.to_thread(self.postgresql.stop)
        self.psql_dir.cleanup()

    async def test_runner(self):
        tests = [self._test_histogram,
                 self._test_basic_upsert_extract_remove,
                 self._test_time_bound_queries,
                 self._test_remove_bound_queries,
                 self._test_json_queries,
                 self._test_limit_queries,
                 self._test_info,
                 self._test_count
                 ]
        for test in tests:
            conn: asyncpg.Connection = await asyncpg.connect(self.db_url)
            await conn.execute("DROP SCHEMA IF EXISTS data CASCADE")
            await conn.execute("CREATE SCHEMA data")
            await conn.execute("GRANT ALL ON SCHEMA data TO public")

            self.store = EventStore(self.db_url)
            await self.store.initialize()
            await conn.close()
            await test()
            # simulate the nose2 test output
            sys.stdout.write('o')
            await self.store.close()
            sys.stdout.flush()

    async def _test_info(self):
        streams = []
        for i in range(20):
            event_stream = EventStream(id=i, name=f'test_stream{i}')
            await self.store.create(event_stream)
            streams.append(event_stream)
            if i % 2 == 0:  # only half the streams have events
                events = [{'start_time': j * 100,
                           'end_time': j * 100 + 10,
                           'content': {'title': "Event%d" % j,
                                       'stream': event_stream.name}
                           } for j in range(i * 1000, i * 1000 + 20 + i)]
            else:
                events = []
            await self.store.upsert(event_stream, events)

        def _expected_info(stream_ids):
            results = {}
            for x in stream_ids:
                if x % 2 != 0:
                    results[x] = StreamInfo(None, None, 0, 0, 0)
                else:
                    start = x * 1000 * 100
                    end = (x * 1000 + 20 + x - 1) * 100 + 10
                    results[x] = StreamInfo(start, end, 20 + x, end - start, 0)
            return results

        # info from one stream
        stream_info = await self.store.info([streams[4]])
        self.assertDictEqual(stream_info, _expected_info([4]))
        # info about multiple streams
        stream_info = await self.store.info(streams[:2])
        self.assertDictEqual(stream_info, _expected_info([0, 1]))
        # info about a lot of streams (trigger bulk select)
        stream_info = await self.store.info(streams[1:-1])
        ids = [s.id for s in streams[1:-1]]
        self.assertDictEqual(stream_info, _expected_info(ids))

    async def _test_count(self):
        event_stream = EventStream(id=1, name='test_stream')
        await self.store.create(event_stream)
        # create 20 events, 5 with a tag of A and 15 with a tag of B
        events = [{'start_time': i * 100,
                   'end_time': i * 100 + 10,
                   'content': {'title': "Event%d" % i,
                               'stream': event_stream.name,
                               'tag': 'A' if(i < 5) else 'B'}
                   } for i in range(20)]
        await self.store.upsert(event_stream, events)
        # basic count operation
        count = await self.store.count(event_stream)
        self.assertEqual(count, 20)
        # count operation with filter to only return 'A' events
        count = await self.store.count(event_stream, json_filter=[[['tag', 'is', 'A']]])
        self.assertEqual(count, 5)
        # count operation with time bounds to only return events between 1005 and  < 1500
        count = await self.store.count(event_stream, start=1005, end=1500, include_on_going_events=False)
        self.assertEqual(count, 4)
        # includes on going events gets the event at 1000
        count = await self.store.count(event_stream, start=1005, end=1500, include_on_going_events=True)
        self.assertEqual(count, 5)


    async def _test_histogram(self):
        def _count_events(items):
            acc = 0
            for item in items:
                acc += item['content']['count']
            return acc

        # generate 200 events with start times between Aug 1 and Aug 2 2021
        #[h2ts("2021-08-01T00:00:00"), h2ts("2021-08-02T00:00:00")]
        # use microsecond timestamp to improve execution speed (avoid asyncio warning)
        bounds1 = [1627790400000000, 1627876800000000]
        times = [random.randint(bounds1[0], bounds1[1]) for _ in range(200)]
        event_stream = EventStream(id=1, name='test_stream')
        await self.store.create(event_stream)
        events1 = [{'start_time': ts,
                    'end_time': ts + random.randint(int(10e6), int(100e6)),
                    'content': {'block': 1}} for ts in times]
        # generate 150 events with start times between Aug 3 and Aug 4 2021
        #[h2ts("2021-08-03T00:00:00"), h2ts("2021-08-04T00:00:00")] ^-- see above note
        bounds2 = [1627963200000000, 1628049600000000]
        times = [random.randint(bounds2[0], bounds2[1]) for _ in range(150)]
        events2 = [{'start_time': ts,
                    'end_time': ts + random.randint(int(10e6), int(100e6)),
                    'content': {'block': 2}} for ts in times]
        await self.store.upsert(event_stream, events1 + events2)
        # now get the histogram for the whole range
        hist = await self.store.histogram(event_stream)
        self.assertEqual(_count_events(hist), len(events1 + events2))
        # get the histogram for block 1 by time
        hist = await self.store.histogram(event_stream, end=bounds1[1], nbuckets=50)
        self.assertEqual(_count_events(hist), len(events1))
        # expect the right number of buckets
        self.assertEqual(len(hist), 50)
        # get the histogram for block 2 by time
        hist = await self.store.histogram(event_stream, start=bounds2[0], nbuckets=150)
        self.assertEqual(_count_events(hist), len(events2))
        # expect the right number of buckets
        self.assertEqual(len(hist), 150)
        # get the histogram for block 2 by time, but specify both bounds
        hist = await self.store.histogram(event_stream, start=bounds2[0], end=bounds2[1], nbuckets=150)
        self.assertEqual(_count_events(hist), len(events2))
        # expect the right number of buckets
        self.assertEqual(len(hist), 150)
        # get the histogram for block 1 by JSON filter
        hist = await self.store.histogram(event_stream, json_filter=[[['block', 'eq', 1]]])
        self.assertEqual(_count_events(hist), len(events1))
        # expect the right number of buckets
        self.assertEqual(len(hist), 100)
        # retrieving the earlier block and the later JSON filter should return no records
        hist = await self.store.histogram(event_stream, json_filter=[[['block', 'eq', 2]]],
                                          end=bounds1[1])
        self.assertEqual(_count_events(hist), 0)
        # expect the right number of buckets
        self.assertEqual(len(hist), 100)

    async def _test_basic_upsert_extract_remove(self):
        event_stream1 = EventStream(id=1, name='test_stream1')
        await self.store.create(event_stream1)
        events1 = [{'start_time': i * 100,
                    'end_time': i * 100 + 10,
                    'content': {'title': "Event%d" % i,
                                'stream': event_stream1.name}
                    } for i in range(20)]
        await self.store.upsert(event_stream1, events1)
        event_stream2 = EventStream(id=2, name='test_stream2')
        await self.store.create(event_stream2)
        events2 = [{'start_time': (i * 100) + 3,
                    'end_time': (i * 100) + 13,
                    'content': {'title': "Event%d" % i,
                                'stream': event_stream2.name}
                    } for i in range(20)]
        await self.store.upsert(event_stream2, events2)
        # now try to read them back
        rx_events = await self.store.extract(event_stream1)
        # they should match but now have an id field
        ids = set([e["id"] for e in rx_events])
        self.assertEqual(len(ids), len(events1))
        # update the first event
        rx_events[0]['content']['title'] = 'updated'
        rx2_events = await self.store.upsert(event_stream1, rx_events)
        rx3_events = await self.store.extract(event_stream1)
        self.assertListEqual(rx_events, rx2_events)
        self.assertListEqual(rx2_events, rx3_events)
        # ...the two event streams are independent
        rx_events = await self.store.extract(event_stream2)
        # they should match but now have an id field (which is not included in the equality test)
        # the received events will also have an event_stream_id field
        # so we put this field into events2 for comparison
        for e in events2:
            e['event_stream_id']=event_stream2.id
        self.assertListEqual(events2, rx_events)
        # now remove them
        await self.store.remove(event_stream1)
        rx_events = await self.store.extract(event_stream1)
        self.assertListEqual(rx_events, [])
        # ...the two event streams are independent
        rx_events = await self.store.extract(event_stream2)
        self.assertListEqual(events2, rx_events)

    async def _test_time_bound_queries(self):
        event_stream1 = EventStream(id=1, name='test_stream1')
        await self.store.create(event_stream1)
        early_events = [{'start_time': i * 100,
                         'end_time': i * 100 + 10,
                         'event_stream_id': event_stream1.id,
                         'content': {'title': "Event%d" % i,
                                     'stream': event_stream1.name}
                         } for i in range(20)]
        mid_events = [{'start_time': i * 100,
                       'end_time': i * 100 + 10,
                       'event_stream_id': event_stream1.id,
                       'content': {'title': "Event%d" % i,
                                   'stream': event_stream1.name}
                       } for i in range(30, 40)]
        late_events = [{'start_time': i * 100,
                        'end_time': i * 100 + 10,
                        'event_stream_id': event_stream1.id,
                        'content': {'title': "Event%d" % i,
                                    'stream': event_stream1.name}
                        } for i in range(50, 60)]
        await self.store.upsert(event_stream1, early_events + mid_events + late_events)

        # now try to read them back
        rx_events = await self.store.extract(event_stream1, start=3000, end=4500)
        self.assertListEqual(rx_events, mid_events)
        rx_events = await self.store.extract(event_stream1, end=4500)
        self.assertListEqual(rx_events, early_events + mid_events)
        rx_events = await self.store.extract(event_stream1, start=3000)
        self.assertListEqual(rx_events, mid_events + late_events)

        # now try offset timebounds to verify include_ongoing_events
        rx_events = await self.store.extract(event_stream1, start=3010, end=4500, include_on_going_events=False)
        self.assertListEqual(rx_events, mid_events[1:]) # skips first event
        rx_events = await self.store.extract(event_stream1, start=3010, end=4500, include_on_going_events=True)
        self.assertListEqual(rx_events, mid_events) # includes first event


        # now try limited queries
        rx_events = await self.store.extract(event_stream1, start=3000, limit=10)
        self.assertListEqual(rx_events, mid_events[:10])
        rx_events = await self.store.extract(event_stream1, end=4500, limit=10)
        self.assertListEqual(rx_events, mid_events[-10:])

    async def _test_remove_bound_queries(self):
        event_stream1 = EventStream(id=20, name='test_stream1')
        await self.store.create(event_stream1)

        early_events = [{'start_time': i * 100,
                         'end_time': i * 100 + 10,
                         'event_stream_id': event_stream1.id,
                         'content': {'title': "Event%d" % i,
                                     'stream': event_stream1.name}
                         } for i in range(20)]
        mid_events = [{'start_time': i * 100,
                       'end_time': i * 100 + 10,
                       'event_stream_id': event_stream1.id,
                       'content': {'title': "Event%d" % i,
                                   'stream': event_stream1.name}
                       } for i in range(30, 40)]
        late_events = [{'start_time': i * 100,
                        'end_time': i * 100 + 10,
                        'event_stream_id': event_stream1.id,
                        'content': {'title': "Event%d" % i,
                                    'stream': event_stream1.name}
                        } for i in range(50, 60)]
        await self.store.upsert(event_stream1, early_events + mid_events + late_events)

        # remove the middle
        await self.store.remove(event_stream1, start=3000, end=4500)
        rx_events = await self.store.extract(event_stream1)
        self.assertListEqual(rx_events, early_events + late_events)
        # remove the beginning
        await self.store.remove(event_stream1, end=3000)
        rx_events = await self.store.extract(event_stream1)
        self.assertListEqual(rx_events, late_events)
        # remove the end
        await self.store.remove(event_stream1, start=4500)
        rx_events = await self.store.extract(event_stream1)
        self.assertListEqual(rx_events, [])

    async def _test_json_queries(self):
        event_stream1 = EventStream(id=20, name='test_stream1')
        await self.store.create(event_stream1)

        early_events = [{'start_time': i * 100,
                         'end_time': i * 100 + 10,
                         'event_stream_id': event_stream1.id,
                         'content': {'title': "Event%d" % i,
                                     'type': 'early',
                                     'stream': event_stream1.name}
                         } for i in range(20)]
        mid_events = [{'start_time': i * 100,
                       'end_time': i * 100 + 10,
                       'event_stream_id': event_stream1.id,
                       'content': {'title': "Event%d" % i,
                                   'type': 'middle',
                                   'stream': event_stream1.name}
                       } for i in range(30, 40)]
        late_events = [{'start_time': i * 100,
                        'end_time': i * 100 + 10,
                        'event_stream_id': event_stream1.id,
                        'content': {'title': "Event%d" % i,
                                    'stream': event_stream1.name}
                        } for i in range(50, 60)]
        await self.store.upsert(event_stream1, early_events + mid_events + late_events)

        middle_events = await self.store.extract(event_stream1, json_filter=[[['type', 'is', 'middle']]])
        self.assertListEqual(mid_events, middle_events)
        specific_event = await self.store.extract(event_stream1, json_filter=[[['type', 'is', 'middle'],
                                                                               ['title', 'is', 'Event30']]])
        self.assertEqual(mid_events[0], specific_event[0])

    async def _test_limit_queries(self):
        event_stream1 = EventStream(id=20, name='test_stream1')
        await self.store.create(event_stream1)

        events = [{'start_time': i * 100,
                   'end_time': i * 100 + 10,
                   'event_stream_id': event_stream1.id,
                   'content': {'title': "Event%d" % i,
                               'type': 'early',
                               'stream': event_stream1.name}
                   } for i in range(20)]
        await self.store.upsert(event_stream1, events)

        first_events = await self.store.extract(event_stream1, limit=5)
        self.assertListEqual(events[:5], first_events)

# from https://stackoverflow.com/questions/5844672/delete-an-element-from-a-dictionary
# def _remove_id(events):
#    return [{i: e[i] for i in e if i != 'id'} for e in events]
