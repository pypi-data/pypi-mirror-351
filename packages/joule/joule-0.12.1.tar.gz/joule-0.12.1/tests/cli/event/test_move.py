import warnings
from click.testing import CliRunner
from ..fake_joule import FakeJoule, FakeJouleTestCase
from joule.cli import main

warnings.simplefilter('always')


class TestStreamMove(FakeJouleTestCase):

    def test_stream_move(self):
        server = FakeJoule()
        self.start_server(server)
        runner = CliRunner()
        result = runner.invoke(main, ['event', 'move', '/folder/src', '/folder/dest'])
        self.assertCliSuccess(result)
        (path, destination) = self.msgs.get()
        self.assertEqual(path, '/folder/src')
        self.stop_server()

    def test_when_stream_does_not_exist(self):
        server = FakeJoule()
        server.response = "stream does not exist"
        server.http_code = 404
        server.stub_stream_move = True
        self.start_server(server)
        runner = CliRunner()
        result = runner.invoke(main, ['event', 'move', '/bad/path', '/folder/dest'])
        self.assertIn("Error", result.output)
        self.stop_server()

    def test_when_server_returns_error_code(self):
        server = FakeJoule()
        server.response = "test error"
        server.http_code = 500
        server.stub_stream_move = True
        self.start_server(server)
        runner = CliRunner()
        result = runner.invoke(main, ['event', 'move', '/folder/src', '/folder/dest'])
        self.assertIn('500', result.output)
        self.assertIn("test error", result.output)
        self.assertEqual(result.exit_code, 1)
        self.stop_server()
