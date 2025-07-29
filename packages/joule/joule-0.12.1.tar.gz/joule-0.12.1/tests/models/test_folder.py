
from tests import helpers
from datetime import datetime, timezone
from joule.services import parse_pipe_config
from joule.models import DataStream, folder, Folder, EventStream
from joule.errors import ConfigurationError


class TestFolder(helpers.DbTestCase):

    def test_get_stream_path(self):
        # create a stream and then find it again
        stream = parse_pipe_config.run("/very/long/path/to/stream:float32[x]", self.db)
        path = folder.get_stream_path(stream)
        self.assertEqual("/very/long/path/to/stream", path)

        # stream outside the database has no path
        stream = DataStream(name="all alone")
        self.assertIsNone(folder.get_stream_path(stream))

        # remote streams are [node] /path/to/stream
        stream = DataStream(name="remote_stream")
        stream.set_remote("remote_node", "/path/to/stream")
        path = folder.get_stream_path(stream)
        self.assertEqual("[remote_node] /path/to/stream", path)

    def test_find_or_create(self):
        folder.find("/new/folder/path", self.db, create=True)
        self.assertEqual(self.db.query(Folder).count(), 4)
        # trailing slash raises an error
        with self.assertRaisesRegex(ConfigurationError, 'invalid path'):
            folder.find("/new/folder/path/", self.db, create=True)
        # does not create folder if create flag is false
        result = folder.find("/new/different/path", self.db)
        self.assertIsNone(result)
        self.assertEqual(self.db.query(Folder).count(), 4)
        # raises error if the requested stream_type is not valid
        with self.assertRaisesRegex(ValueError, 'type'):
            folder.find_stream_by_path("/new/folder/path", self.db, stream_type="invalid")

    def test_updates_attributes(self):
        my_folder = folder.find("/new/folder/path", self.db, create=True)
        my_folder.update_attributes({"name": "new name", "description": "new description"})
        self.assertEqual(my_folder.name, "new name")
        self.assertEqual(my_folder.description, "new description")
        # validates name attribute
        for name in ["invalid/name", "", None]:
            with self.assertRaises(ConfigurationError):
                my_folder.update_attributes({"name": name})


    def test_contains_streams(self):
        my_folder = folder.find("/new/folder/path", self.db, create=True)
        my_folder.data_streams = [helpers.create_stream("stream1", "int16_2")]
        self.db.add(my_folder)
        self.db.commit()
        f = folder.find("/new", self.db)
        self.assertTrue(f.contains_streams())
        self.assertTrue(my_folder.contains_streams())

        my_folder = folder.find("/events/new/folder/path", self.db, create=True)
        my_folder.event_streams = [EventStream(name="event_stream1", updated_at=datetime.now(timezone.utc))]
        self.db.add(my_folder)
        self.db.commit()
        f = folder.find("/events", self.db)
        self.assertTrue(f.contains_streams())
        self.assertTrue(my_folder.contains_streams())

        empty_folder = folder.find("/empty/new/folder", self.db, create=True)
        self.db.add(empty_folder)
        self.db.commit()
        f = folder.find("/empty", self.db)
        self.assertFalse(f.contains_streams())
        self.assertFalse(empty_folder.contains_streams())

    def test_locked(self):
        my_folder = folder.find("/new/folder/path", self.db, create=True)
        my_stream = helpers.create_stream("stream1", "int16_2")
        my_stream.is_configured = True
        my_stream.folder = my_folder
        self.db.add(my_stream)
        self.db.commit()
        f = folder.find("/new", self.db)
        self.assertTrue(f.locked)
        self.assertTrue(my_folder.locked)

        my_stream.is_configured = False
        self.db.commit()
        self.assertFalse(f.locked)
        self.assertFalse(my_folder.locked)

        empty_folder = folder.find("/empty/new/folder", self.db, create=True)
        self.db.add(empty_folder)
        self.db.commit()
        f = folder.find("/empty", self.db)
        self.assertFalse(f.locked)
        self.assertFalse(empty_folder.locked)




