from abc import ABC, abstractmethod
import asyncio
from functools import wraps
from typing import Callable, Dict
import unittest
from pizza_client.config import LLMClientConfig, LLMClientConfigInput
from pizza_client.logger import Logger
from openai import OpenAI
from enum import Enum
from .exceptions import ConnectionError, InternalConnectionError
from pizza_client.logger import LogLevels
from pydantic import BaseModel, Field

class ConnectionStatus(Enum):
    CONNECTED = 1
    DISCONNECTED = 2
    CONNECTING = 3
    DISCONNECTING = 4
    FAILED = 5

class QueryInput(BaseModel):
    query: str = Field(...,min_length=10, title="The query to be sent to the LLM")

class LLMClient(ABC):
    _connectionStatus = ConnectionStatus.DISCONNECTED
    _config = None
    _connection_attempt = None
    _logger = None
    error_fallbacks : Dict[Exception, Callable[[], None]] = {}
    _last_connection_result = None

    def handle_exception(self, func,  e : Exception):
        self._logger.error("Error in %s: %s", func.__name__, e)
        if e.__class__ in self.error_fallbacks:
            self.error_fallbacks[e.__class__]()
        else:
            self._logger.error("Error in %s: %s", func.__name__, e)
        return None
    
    def error_handler(func : Callable):
        """Decorator to handle errors in LLM client methods."""
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    return self.handle_exception(func, e) 
                
            return wrapper
        else:
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    return self.handle_exception(func, e)
            return wrapper
    
    def __init__(self, config : LLMClientConfigInput):
        self._loop = asyncio.get_event_loop()
        self._config = LLMClientConfig(config)
        log_level = config['log_level'] if 'log_level' in config else LogLevels.INFO
        self._logger = Logger(log_level)
        return
    
    @abstractmethod
    def configure(self, config : LLMClientConfigInput):
        return

    @abstractmethod
    @error_handler
    async def query_llm(self, query : QueryInput):
        return

    # --- CONNECTION MANAGER (should be moved into a class later) ---

    # The correct way to do this is to use a state machine, create state transitions, and create a single method to handle the async state transitions
    @error_handler
    async def connect(self):
        self._logger.debug("Initiating connection")
        match self._connectionStatus:
            case ConnectionStatus.CONNECTING:
                self._logger.debug("Already connecting")
            case ConnectionStatus.DISCONNECTED:
                self._logger.debug("Disconnected, initiating connection")
                self._connectionStatus = ConnectionStatus.CONNECTING
                self._handle_connection_attempt()
            case ConnectionStatus.DISCONNECTING:
                await self._await_disconnection()
                self._connectionStatus = ConnectionStatus.CONNECTING
                self._handle_connection_attempt()
        # Is this the best way to handle this?
        await self._await_connection()
        self._logger.debug("finished connection event")
        return
    
    @error_handler
    async def disconnect(self):
        self._logger.debug("Initiating disconnection, current status: " + str(self._connectionStatus))
        match self._connectionStatus:
            case ConnectionStatus.CONNECTED:
                self._connectionStatus = ConnectionStatus.DISCONNECTING
                await self._disconnect()
                self._connectionStatus = ConnectionStatus.DISCONNECTED
            case ConnectionStatus.CONNECTING:
                await self._await_connection()
                self._connectionStatus = ConnectionStatus.DISCONNECTING
                await self._disconnect()
                self._connectionStatus = ConnectionStatus.DISCONNECTED
        return

    async def _wait_for_connection_status(self, status):
        while self._connectionStatus != status and self._connectionStatus != ConnectionStatus.FAILED:
            await asyncio.sleep(self._config['polling_interval'])
        return
    
    async def _await_connection(self):
        return await self._wait_for_connection_status(ConnectionStatus.CONNECTED)
    
    async def _await_disconnection(self):
        return await self._wait_for_connection_status(ConnectionStatus.DISCONNECTED)
    
    # We should add connection retries later
    def _handle_connection_attempt(self):
        self._logger.debug("Initiating connection attempt")
        if self._connection_attempt == None:
            self._logger.debug("No connection attempt in progress, initiating")
            self._connection_attempt = self._loop.create_task(self._connect())
            self._connection_attempt.add_done_callback(self._handle_connection_result)
        else:
            self._logger.debug("Connection attempt already in progress")
        return

    def _handle_connection_result(self, future : asyncio.Future):
        self._logger.debug("connection result received:" , future)
        if future.exception() != None:
            self._connection_attempt = None
            self._connectionStatus = ConnectionStatus.FAILED
            self._logger.error("Error connecting to the service" ,future.exception())
        else:
            self._connection_attempt = None
            self._connectionStatus = ConnectionStatus.CONNECTED
            self._logger.info("Connected to the service")
        return

    @abstractmethod   
    @error_handler
    async def _connect(self):
        return
    
    @abstractmethod
    async def _disconnect(self):
        return
    
    # --- END CONNECTION MANAGER ---

    

class OpenAIMockClient(LLMClient):

    def __init__(self, config):
        super().__init__(config)
        # This is a mock implementation
        return
    
    async def _connect(self):
        # This is a mock implementation
        self._logger.info("Connecting to OpenAI")
        await asyncio.sleep(1)
        self._logger.info("Connected to OpenAI")
        return

    async def _disconnect(self):
        # This is a mock implementation
        self._logger.info("Disconnecting from OpenAI")
        await asyncio.sleep(1)
        self._logger.info("Disconnected from OpenAI")
        return

    def configure(self, config):
        self._logger.debug("Configuring OpenAI client")
        self._config = config
        return
    
    async def query_llm(self, query):
        self._logger.debug("Querying OpenAI with: " + str(query))
        return "This is a mock response, based on the query: " + str(query)
    
class AnthropicMockClient(LLMClient):
    
    def __init__(self, config):
        super().__init__(config)
        # This is a mock implementation
        return
    
    async def _connect(self):
        # This is a mock implementation
        self._logger.info("Connecting to Anthropic")
        await asyncio.sleep(1)
        self._logger.info("Connected to Anthropic")
        return

    async def _disconnect(self):
        # This is a mock implementation
        self._logger.info("Disconnecting from Anthropic")
        await asyncio.sleep(1)
        self._logger.info("Disconnected from Anthropic")
        return

    def configure(self, config):
        self._logger.debug("Configuring Anthropic client")
        self._config = config
        return
    
    async def query_llm(self, query):
        self._logger.debug("Querying Anthropic with: " + str(query))
        return "This is a mock response, based on the query: " + str(query)



def critical_error():
    print("Critical unhandled error")
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