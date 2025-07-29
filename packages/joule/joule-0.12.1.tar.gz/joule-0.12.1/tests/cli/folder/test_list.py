from click.testing import CliRunner
import os
import logging

import warnings
from tests.cli.fake_joule import FakeJoule, FakeJouleTestCase
from joule.cli import main


FOLDER_LIST = os.path.join(os.path.dirname(__file__), 'folders.json')
warnings.simplefilter('always')
aio_log = logging.getLogger('aiohttp.access')
aio_log.setLevel(logging.WARNING)


class TestFolderList(FakeJouleTestCase):

    def test_lists_folders(self):
        server = FakeJoule()
        with open(FOLDER_LIST, 'r') as f:
            server.response = f.read()
        self.start_server(server)
        runner = CliRunner()
        result = runner.invoke(main, ['folder', 'list'])
        self.assertEqual(result.exit_code, 0)
        output = result.output
        # make sure the folders are listed
        for folder in ['basic', 'aux', 'event', 'sensors']:
            self.assertIn(folder, output)
        # make sure the data streams are listed
        for stream in ['Accel', 'Encoder', 'Gyro']:
            self.assertIn(stream, output)
        # make sure the event streams are listed
        for stream in ['events0', 'events1', 'events2']:
            self.assertIn(stream, output)
        # should  check for layout strings
        self.assertNotIn("float32_3", output)
        self.stop_server()

    def test_lists_streams_with_options(self):
        server = FakeJoule()
        with open(FOLDER_LIST, 'r') as f:
            server.response = f.read()
        self.start_server(server)
        runner = CliRunner()
        result = runner.invoke(main, ['folder', 'list', '-s', '-l'])
        self.assertEqual(result.exit_code, 0)
        output = result.output
        # check for the augmented legend
        self.assertIn("configured", output)
        # check for layout strings
        self.assertIn("float32_3", output)
        self.stop_server()

    def test_when_server_returns_invalid_data(self):
        server = FakeJoule()
        server.response = "notjson"
        self.start_server(server)
        runner = CliRunner()
        result = runner.invoke(main, ['folder', 'list'])
        self.assertIn('Error', result.output)
        self.assertEqual(result.exit_code, 1)
        self.stop_server()

    def test_when_server_returns_error_code(self):
        server = FakeJoule()
        error_msg = "test error"
        error_code = 500
        server.response = error_msg
        server.http_code = error_code
        self.start_server(server)
        runner = CliRunner()
        result = runner.invoke(main, ['folder', 'list'])
        self.assertIn('%d' % error_code, result.output)
        self.assertIn(error_msg, result.output)
        self.assertEqual(result.exit_code, 1)
        self.stop_server()
