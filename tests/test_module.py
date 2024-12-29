import asyncio
from typing import Callable, Dict
import unittest
from pizza_client import LLMClient, LogLevels, ConnectionStatus, OpenAIMockClient

class TestAbstractLLMClient(unittest.TestCase):

    def setUp(self):
        config = {"log_level": LogLevels.DEBUG, 'polling_interval': 0.1}
        self.client = OpenAIMockClient(config)
        self.loop = asyncio.get_event_loop()

    def test_initial_connection_status(self):
        print("initial connection status ",self.client._connectionStatus)
        self.assertEqual(self.client._connectionStatus, ConnectionStatus.DISCONNECTED)

    def test_connect(self):
        async def run_test():
            await self.client.connect()
            self.assertEqual(self.client._connectionStatus, ConnectionStatus.CONNECTED)
        self.loop.run_until_complete(run_test())

    def test_disconnect(self):
        async def run_test():
            await self.client.connect()
            await self.client.disconnect()
            self.assertEqual(self.client._connectionStatus, ConnectionStatus.DISCONNECTED)
        self.loop.run_until_complete(run_test())

    def test_query_llm(self):
        async def run_test():
            await self.client.connect()
            response = await self.client.query_llm("Hello, world!")
            self.assertEqual(response, "This is a mock response, based on the query: Hello, world!")
        self.loop.run_until_complete(run_test())

def critical_error():
    print("Mocking unhandled error")
    raise TestErrorHandling("This is a test exception")

class TestErrorHandling(Exception):
    pass


class FailingClient(OpenAIMockClient):
        error_fallbacks : Dict[Exception, Callable[[], None]] = {
            Exception: critical_error
        }

        @LLMClient.error_handler
        async def _connect(self):
            raise Exception("This is a test exception")

class TestErrorHandler(unittest.TestCase):


    def setUp(self):
        config = {"log_level": LogLevels.DEBUG, 'polling_interval': 0.1}
        self.client = FailingClient(config)
        self.loop = asyncio.get_event_loop()

    def test_error_handler(self):
        async def run_test():
            with self.assertRaises(TestErrorHandling):
                await self.client._connect()
        self.loop.run_until_complete(run_test())

if __name__ == '__main__':
    suite = unittest.TestLoader().discover('tests')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("\nSummary:")
    print(f"Ran {result.testsRun} tests")
    print(f"Failures: {len(result.failures)}")
    for test, err in result.failures:
        print(f"FAIL: {test}")
        print(err)
    print(f"Errors: {len(result.errors)}")
    for test, err in result.errors:
        print(f"ERROR: {test}")
        print(err)
    print(f"Skipped: {len(result.skipped)}")
    for test, reason in result.skipped:
        print(f"SKIP: {test} - {reason}")
    print(f"Expected Failures: {len(result.expectedFailures)}")
    for test, err in result.expectedFailures:
        print(f"EXPECTED FAILURE: {test}")
        print(err)
    print(f"Unexpected Successes: {len(result.unexpectedSuccesses)}")
    for test in result.unexpectedSuccesses:
        print(f"UNEXPECTED SUCCESS: {test}")