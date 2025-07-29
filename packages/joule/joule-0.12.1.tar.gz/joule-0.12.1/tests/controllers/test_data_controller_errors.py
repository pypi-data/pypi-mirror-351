from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
import aiohttp
from sqlalchemy.orm import Session
import asyncio
from joule.models import DataStream
import joule.controllers
from tests.controllers.helpers import create_db, MockStore, MockSupervisor
from tests import helpers
from joule import app_keys
from joule.constants import EndPoints

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


    async def test_read_requires_path_or_id(self):
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data, params={})
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('path' in await resp.text())


    async def test_read_errors_on_invalid_stream(self):
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data, params={'path': '/no/stream'})
        self.assertEqual(resp.status, 404)
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data, params={'id': '404'})
        self.assertEqual(resp.status, 404)


    async def test_read_errors_on_no_data(self):
        store: MockStore = self.app[app_keys.data_store]
        store.configure_extract(0, no_data=True)
        params = {'path': '/folder1/stream1', 'decimation-level': 64}
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('no data' in await resp.text())


    async def test_read_errors_on_decimation_failure(self):
        store: MockStore = self.app[app_keys.data_store]
        store.configure_extract(10, decimation_error=True)
        params = {'path': '/folder1/stream1', 'decimation-level': 64}
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('decimated' in await resp.text())


    async def test_read_errors_on_datastore_error(self):
        store: MockStore = self.app[app_keys.data_store]
        store.configure_extract(10, data_error=True)
        params = {'path': '/folder1/stream1', 'decimation-level': 64}
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('error' in await resp.text())


    async def test_read_params_must_be_valid(self):
        params = dict(path='/folder1/stream1')
        # start must be an int
        params['start'] = 'bad'
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('start' in await resp.text())
        # end must be an int
        params['start'] = 100
        params['end'] = '200.5'
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('end' in await resp.text())
        # start must be before end
        params['end'] = 50
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('end' in await resp.text())
        self.assertTrue('start' in await resp.text())
        params['end'] = 200
        # max rows must be an int > 0
        params['max-rows'] = -4
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('max-rows' in await resp.text())
        params['max-rows'] = 100
        # decimation-level must be >= 0
        params['decimation-level'] = -50
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('decimation-level' in await resp.text())
        params['decimation-level'] = 20


    async def test_subscribe_requires_path_or_id(self):
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data, params={'subscribe': '1'})
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('path' in await resp.text())


    async def test_subscribe_errors_on_invalid_stream(self):
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data, params={'path': '/no/stream', 'subscribe': '1'})
        self.assertEqual(resp.status, 404)
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data, params={'id': '404', 'subscribe': '1'})
        self.assertEqual(resp.status, 404)


    async def test_subscribe_errors_on_unproduced_stream(self):
        self.supervisor.raise_error = True
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data, params={'path': '/folder1/stream1', 'subscribe': '1'})
        self.assertEqual(resp.status, 400)


    async def test_subscribe_does_not_support_json(self):
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data_json, params={'path': '/folder1/stream1', 'subscribe': '1'})
        self.assertEqual(resp.status, 400)


    async def test_write_requires_path_or_id(self):
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={})
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('path' in await resp.text())


    async def test_write_errors_on_invalid_stream(self):
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={'path': '/no/stream'})
        self.assertEqual(resp.status, 404)
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={'id': '404'})
        self.assertEqual(resp.status, 404)

    async def test_write_errors_on_merge_gap(self):
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={'path': '/folder1/stream1', 'merge-gap':'not valid'})
        self.assertEqual(resp.status, 400)
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={'path': '/folder1/stream1', 'merge-gap':-5})
        self.assertEqual(resp.status, 400)
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={'path': '/folder1/stream1', 'merge-gap':8.6})
        self.assertEqual(resp.status, 400)

    async def test_remove_requires_path_or_id(self):
        resp: aiohttp.ClientResponse = await \
            self.client.delete(EndPoints.data, params={})
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('path' in await resp.text())


    async def test_remove_errors_on_invalid_stream(self):
        resp: aiohttp.ClientResponse = await \
            self.client.delete(EndPoints.data, params={'path': '/no/stream'})
        self.assertEqual(resp.status, 404)
        resp: aiohttp.ClientResponse = await \
            self.client.delete(EndPoints.data, params={'id': '404'})
        self.assertEqual(resp.status, 404)


    async def test_remove_bounds_must_be_valid(self):
        params = dict(path='/folder1/stream1')
        # start must be an int
        params['start'] = 'bad'
        resp: aiohttp.ClientResponse = await self.client.delete(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('start' in await resp.text())
        # end must be an int
        params['start'] = 100
        params['end'] = '200.5'
        resp: aiohttp.ClientResponse = await self.client.delete(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('end' in await resp.text())
        # start must be before end
        params['end'] = 50
        resp: aiohttp.ClientResponse = await self.client.delete(EndPoints.data, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('end' in await resp.text())
        self.assertTrue('start' in await resp.text())
        params['end'] = 200


    async def test_intervals_requires_path_or_id(self):
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data_intervals, params={})
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('path' in await resp.text())


    async def test_intervals_errors_on_bad_stream(self):
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data_intervals, params={'path': '/no/stream'})
        self.assertEqual(resp.status, 404)
        resp: aiohttp.ClientResponse = await \
            self.client.get(EndPoints.data_intervals, params={'id': '404'})
        self.assertEqual(resp.status, 404)


    async def test_interval_bounds_must_be_valid(self):
        params = dict(path='/folder1/stream1')
        # start must be an int
        params['start'] = 'bad'
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data_intervals, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('start' in await resp.text())
        # end must be an int
        params['start'] = 100
        params['end'] = '200.5'
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data_intervals, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('end' in await resp.text())
        # start must be before end
        params['end'] = 50
        resp: aiohttp.ClientResponse = await self.client.get(EndPoints.data_intervals, params=params)
        self.assertNotEqual(resp.status, 200)
        self.assertTrue('end' in await resp.text())
        self.assertTrue('start' in await resp.text())
        params['end'] = 200


    async def test_invalid_writes_propagates_data_error(self):
        db: Session = self.app[app_keys.db]
        store: MockStore = self.app[app_keys.data_store]
        store.raise_data_error = True
        stream: DataStream = db.query(DataStream).filter_by(name="stream1").one()
        data = helpers.create_data(stream.layout)
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data, params={"path": "/folder1/stream1"},
                             data=data.tobytes())
        self.assertEqual(resp.status, 400)
        self.assertIn('test error', await resp.text())

    async def test_cannot_use_decimation_tools_without_backend_support(self):
        store: MockStore = self.app[app_keys.data_store]
        store.supports_decimation_management = False
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data_decimate, params={"path": "/folder1/stream1"})
        self.assertEqual(resp.status, 400)
        self.assertIn('support', await resp.text())
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data_consolidate, params={"path": "/folder1/stream1"})
        self.assertEqual(resp.status, 400)
        self.assertIn('support', await resp.text())
        resp: aiohttp.ClientResponse = await \
            self.client.delete(EndPoints.data_decimate, params={"path": "/folder1/stream1"})
        self.assertEqual(resp.status, 400)
        self.assertIn('support', await resp.text())

    async def test_data_stream_consolidation(self):
        store: MockStore = self.app[app_keys.data_store]
        store.supports_consolidation = True
        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data_consolidate, params={"path": "/folder1/stream1"})
        self.assertEqual(resp.status, 400)
        self.assertIn('max_gap', await resp.text())

        resp: aiohttp.ClientResponse = await \
            self.client.post(EndPoints.data_consolidate, params={"path": "/folder1/stream1", "max_gap": -2})
        self.assertEqual(resp.status, 400)
        self.assertIn('max_gap', await resp.text())