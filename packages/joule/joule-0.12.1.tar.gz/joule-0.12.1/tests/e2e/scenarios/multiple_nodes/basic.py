import unittest

import joule.api
import subprocess
from joule import api
import asyncio

class TestBasicAPI(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.node1 = api.get_node("node1.joule")
        followers = await self.node1.follower_list()
        self.assertEqual(len(followers), 1)
        self.node2 = followers[0]
        # add the root user as a follower to node2.joule
        user = await self.node2.master_add("user", "cli")
        # follower uses built-in HTTP server on port 8080
        proc = await asyncio.create_subprocess_shell(f"coverage run --rcfile=/joule/.coveragerc -m joule.cli node add node2.joule http://node2.joule:8080 {user.key}")
        await proc.communicate()
        """
        node1.joule:
        /main/folder/added:int32[x]
        node2.joule:
        /main/folder/base:int32[x]
        """

    async def asyncTearDown(self):
        await self.node2.master_delete("user", "cli")
        await self.node1.close()
        await self.node2.close()

    async def test_retrieves_streams(self):
        logs = await self.node1.module_logs("Remote")
        self.assertGreater(len(logs), 0)
        self.assertIn("starting module", logs[0])
        added_stream = await self.node1.data_stream_get("/main/folder/added")
        base_stream = await self.node2.data_stream_get("/main/folder/base")
        # make sure added_stream has data
        added_data = await self.node1.data_subscribe(added_stream)
        base_data = await self.node2.data_subscribe(base_stream)
        base_block = await base_data.read()
        added_block = await added_data.read()
        # align the time stamps
        diff = base_block['timestamp'][0] - added_block['timestamp'][0]
        print("the diff is %d" % diff)
        await added_data.close()
        await base_data.close()

    async def test_copies_events(self):
        events = []
        for i in range(1000, 2000, 100):
            events.append(joule.api.Event(start_time=i, end_time=i + 50,
                                          content={'name': f"Event{i}"}))
        event_stream = joule.api.EventStream("TestEvents")
        event_stream = await self.node1.event_stream_create(event_stream, "/eventstreams")
        await self.node1.event_stream_write(event_stream, events)
        cmd = "coverage run --rcfile=/joule/.coveragerc -m joule.cli event copy /eventstreams/TestEvents /eventstreams/TestEventsCopy -d node2.joule"
        proc = await asyncio.create_subprocess_shell(cmd)
        await proc.communicate()
        copied_events = await self.node2.event_stream_read_list("/eventstreams/TestEventsCopy")
        self.assertListEqual(events, copied_events)
