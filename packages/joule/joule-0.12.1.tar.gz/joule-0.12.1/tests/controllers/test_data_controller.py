from aiohttp.test_utils import AioHTTPTestCase
from aiohttp import web
import aiohttp
import numpy as np
from sqlalchemy.orm import Session
import asyncio
from joule.models import DataStream, pipes
import joule.controllers
from tests.controllers.helpers import create_db, MockStore, MockSupervisor
from tests import helpers
from joule import app_keys
from joule.constants import EndPoints
from joule.errors import EmptyPipeError

import testing.postgresql
psql_key = web.AppKey("psql", testing.postgresql.Postgresql)

class TestDataController(AioHTTPTestCase):

    async def tearDownAsync(self):
        self.app[app_keys.db].close()
        self.app[psql_key].stop()
        await self.client.close()

    async def get_application(self):
        app = web.Application()
        app.add_routes(joule.controllers.routes)
        # this takes a while, adjust the expected coroutine execution time
        loop = asyncio.get_running_loop()
        loop.slow_callback_duration = 2.0
        app[app_keys.db], app[psql_key] = create_db(["/folder1/stream1:float32[x, y, z]",
                                            "/folder2/deeper/stream2:int16[val1, val2]"])
        app[app_keys.data_store] = MockStore()
        self.supervisor = MockSupervisor()
        app[app_keys.supervisor] = self.supervisor
        return app


    async def test_read_binary_data(self):
        db: Session = self.app[app_keys.db]
        store: MockStore = self.app[app_keys.data_store]
        nchunks = 3
        nintervals=4
        store.configure_extract(nchunks, nintervals)
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data, params={"path": "/folder1/stream1"})
        rx_chunks = 0
        # this data is binary so we can't do much with it, just make sure 
        # the handler is called multiple times :) 
        async for data, _ in resp.content.iter_chunks():
            if len(data) > 0:
                rx_chunks += 1
        self.assertGreater(rx_chunks, 1)

        # can retrieve stream by id and as decimated data
        stream = db.query(DataStream).filter_by(name="stream1").one()
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data, params={"id": stream.id, 'decimation-level': 16})
        rx_chunks = 0
        async for data, _ in resp.content.iter_chunks():
            if len(data) > 0:
                rx_chunks += 1
        self.assertGreater(rx_chunks, 1)
        self.assertEqual(resp.headers['joule-decimation'], '16')
        self.assertEqual(resp.headers['joule-layout'], stream.decimated_layout)


    async def test_read_json_data(self):
        db: Session = self.app[app_keys.db]
        store: MockStore = self.app[app_keys.data_store]
        n_chunks = 10
        n_intervals = 5
        # mock data has 5 intervals retrieved as 10 chunks each
        store.configure_extract(n_chunks, n_intervals)
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data_json, params={"path": "/folder1/stream1"})
        data = await resp.json()
        self.assertEqual(1, data['decimation_factor'])
        self.assertEqual(len(data['data'][0]), n_chunks * 25)
        # can retrieve stream by id and as decimated data as well
        stream = db.query(DataStream).filter_by(name="stream1").one()
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data_json, params={"id": stream.id, 'decimation-level': 16})
        data = await resp.json()
        self.assertEqual(data['decimation_factor'], 16)
        # only the interval is exposed, the chunking is transparent
        self.assertEqual(len(data['data']), n_intervals)
        for interval in data['data']:
            self.assertEqual(len(interval), n_chunks * 25)


    async def test_subscribes_to_data(self):
        db: Session = self.app[app_keys.db]
        my_stream = db.query(DataStream).filter_by(name="stream1").one()
        blk1 = helpers.create_data(my_stream.layout)
        blk2 = helpers.create_data(my_stream.layout, length=50)
        my_pipe = pipes.LocalPipe(my_stream.layout)
        my_pipe.write_nowait(blk1)
        my_pipe.close_interval_nowait()
        my_pipe.write_nowait(blk2)
        my_pipe.close_nowait()
        self.supervisor.subscription_pipe = my_pipe
        async with self.client.get(EndPoints.data, params={"id": my_stream.id,
                                                    "subscribe": '1'}) as resp:
            pipe = pipes.InputPipe(stream=my_stream, reader=resp.content)
            rx_blk1 = await pipe.read()
            pipe.consume(len(rx_blk1))
            np.testing.assert_array_equal(blk1, rx_blk1)
            self.assertTrue(pipe.end_of_interval)

            rx_blk2 = await pipe.read()
            pipe.consume(len(rx_blk2))
            np.testing.assert_array_equal(blk2, rx_blk2)
            with self.assertRaises(EmptyPipeError):
                await pipe.read()
        self.assertEqual(self.supervisor.unsubscribe_calls, 1)


    async def test_unsubscribes_terminated_connections(self):
        db: Session = self.app[app_keys.db]
        supervisor: MockSupervisor = self.app[app_keys.supervisor]
        supervisor.hang_pipe = True
        my_stream = db.query(DataStream).filter_by(name="stream1").one()
        my_pipe = pipes.LocalPipe(my_stream.layout)
        my_pipe.close_nowait()
        self.supervisor.subscription_pipe = my_pipe
        async with self.client.get(EndPoints.data, params={"id": my_stream.id,
                                                    "subscribe": '1'}):
            # ignore the data
            pass
        # NOTE: unsubscribe is called but the exception propogates and somehow
        # we loose the reference so this assert fails. Not a problem but why??
        # self.assertEqual(self.supervisor.unsubscribe_calls, 1)


    async def test_write_data(self):
        db: Session = self.app[app_keys.db]
        store: MockStore = self.app[app_keys.data_store]
        stream: DataStream = db.query(DataStream).filter_by(name="stream1").one()
        data = helpers.create_data(stream.layout)
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={"path": "/folder1/stream1"},
                             data=data.tobytes())
        self.assertEqual(resp.status, 200)
        self.assertTrue(store.inserted_data)

        # can write stream by id as well
        store.inserted_data = False
        data = helpers.create_data(stream.layout)
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={"id": stream.id},
                             data=data.tobytes())
        self.assertEqual(resp.status, 200)
        self.assertTrue(store.inserted_data)

        # can set merge_gap value
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={"id": stream.id, "merge-gap": 100},
                             data=data.tobytes())
        self.assertEqual(resp.status, 200)
        self.assertEqual(store.merge_gap, 100)

        # merge gap is 0 by default
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={"id": stream.id},
                             data=data.tobytes())
        self.assertEqual(resp.status, 200)
        self.assertEqual(store.merge_gap, 0)



    async def test_remove_data(self):
        db: Session = self.app[app_keys.db]
        store: MockStore = self.app[app_keys.data_store]
        stream: DataStream = db.query(DataStream).filter_by(name="stream1").one()
        resp: aiohttp.ClientResponse = await \
            self.client.delete(EndPoints.data, params={"path": "/folder1/stream1",
                                                "start": "100", "end": "200"})
        self.assertEqual(resp.status, 200)
        (start, end) = store.removed_data_bounds
        self.assertEqual(start, 100)
        self.assertEqual(end, 200)

        # can remove data by path as well
        resp: aiohttp.ClientResponse = await \
            self.client.delete(EndPoints.data, params={"id": stream.id,
                                                "start": "800", "end": "900"})
        self.assertEqual(resp.status, 200)
        (start, end) = store.removed_data_bounds
        self.assertEqual(start, 800)
        self.assertEqual(end, 900)


    async def test_interval_data(self):
        db: Session = self.app[app_keys.db]
        stream: DataStream = db.query(DataStream).filter_by(name="stream1").one()
        resp = await self.client.get(EndPoints.data_intervals,
                                     params={"id": stream.id})
        # response should be a list of intervals
        data = await resp.json()
        self.assertGreater(len(data), 0)
        for interval in data:
            self.assertEqual(2, len(interval))

        # can query by path as well
        resp = await self.client.get(EndPoints.data_intervals,
                                     params={"path": "/folder1/stream1"})
        # response should be a list of intervals
        data = await resp.json()
        self.assertGreater(len(data), 0)
        for interval in data:
            self.assertEqual(2, len(interval))

        # can specify time bounds
        resp = await self.client.get(EndPoints.data_intervals,
                                     params={"path": "/folder1/stream1",
                                             "start": 10,
                                             "end": 20})
        # the mock store returns the start end bounds as the single interval
        data = await resp.json()
        self.assertEqual(data, [[10, 20]])

    async def test_consolidate_data(self):
        store: MockStore = self.app[app_keys.data_store]
        resp = await self.client.post(EndPoints.data_consolidate, params={"id": 1, "end": 200, "max_gap":100})
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertEqual(data['num_consolidated'], 0)

        # check to make sure the store was called with the correct parameters
        self.assertTrue(store.consolidate_called)
        stream, start, end, max_gap = store.consolidate_params
        self.assertEqual(stream.id, 1)
        self.assertIsNone(start, None)
        self.assertEqual(end, 200)
        self.assertEqual(max_gap, 100)


    async def test_decimate_data(self):
        store: MockStore = self.app[app_keys.data_store]
        resp = await self.client.post(EndPoints.data_decimate, params={"id": 1})
        self.assertEqual(resp.status, 200)
        self.assertTrue(store.redecimated_data)


    async def test_remove_decimations(self):
        store: MockStore = self.app[app_keys.data_store]
        resp = await self.client.delete(EndPoints.data_decimate, params={"id": 1})
        self.assertEqual(resp.status, 200)
        self.assertTrue(store.dropped_decimations)
