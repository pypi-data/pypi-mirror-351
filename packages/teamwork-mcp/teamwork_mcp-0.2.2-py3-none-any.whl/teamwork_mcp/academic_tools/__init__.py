# teamwork_mcp/synced_mcp_client.py
import asyncio
import pickle
import atexit
import logging
from multiprocessing import Process, Queue
from typing import Any, Tuple, Dict
from loguru import logger
from mcp.server.fastmcp import FastMCP

from teamwork_mcp.mcp_sse_server import launch_mcp_server_forever
from teamwork_mcp.manifest_tool_server import launch_manifest_mcp_server_forever

class SyncedMcpClient(Process):
    """
    A synchronous MCP client that runs the AsyncMCPClient in a separate process
    and communicates with it using multiprocessing Queues and pickle.
    """

    def __init__(self, server_url: str = None):
        super().__init__()
        # turn off logging from the logger of 'httpx'
        httpx_logger = logging.getLogger("httpx")
        httpx_logger.setLevel(logging.WARNING)

        self.server_url = server_url
        self.request_queue = Queue()
        self.response_queue = Queue()
        self.is_running = False
        self.daemon = True
        atexit.register(self.cleanup)

        # begin new process
        self.is_running = True
        self.start()

    def run(self):
        """
        The main process function that runs the AsyncMCPClient in a separate process.
        """
        asyncio.run(self._run_async_client())

    async def _run_async_client(self):
        """
        Runs the AsyncMCPClient and handles communication with the main process.
        """
        from teamwork_mcp.mcp_sse_client import AsyncMCPClient

        client = AsyncMCPClient()
        await client.connect_to_sse_server(server_url=self.server_url)

        try:
            while self.is_running:
                if not self.request_queue.empty():
                    request = self.request_queue.get()
                    if request == 'terminate':
                        break
                    try:
                        func_name, args, kwargs = pickle.loads(request)
                        func = getattr(client, func_name)
                        result = await func(*args, **kwargs)
                        self.response_queue.put(pickle.dumps(('success', result)))
                    except Exception as e:
                        self.response_queue.put(pickle.dumps(('error', str(e))))
                        raise RuntimeError(f"Error in function {func_name}: {str(e)}")
                await asyncio.sleep(0.01)

        except Exception as e:
            logger.exception(e)
            self.response_queue.put(pickle.dumps(('error', f"Client initialization error: {str(e)}")))

        finally:
            await client.cleanup()

    def _send_request(self, func_name: str, args: Tuple = (), kwargs: Dict = None) -> Any:
        """
        Sends a request to the async process and waits for the response.
        """
        if kwargs is None:
            kwargs = {}
        self.request_queue.put(pickle.dumps((func_name, args, kwargs)))
        response = self.response_queue.get(timeout=1200)
        status, result = pickle.loads(response)
        if status == 'error':
            raise Exception(result)
        return result

    def call_tool(self, tool_name: str, tool_args: Dict = None) -> Any:
        """
        Calls a tool synchronously by sending a request to the async process.
        """
        return self._send_request('call_tool', args=(tool_name,), kwargs={'tool_args': tool_args})

    def get_prompt(self, name: str, arguments: dict[str, str] | None = None) -> Any:
        """
        Calls a tool synchronously by sending a request to the async process.
        """
        return self._send_request('get_prompt', args=(), kwargs={'name': name, 'arguments': arguments})

    def read_resource(self, uri) -> Any:
        """
        Calls a tool synchronously by sending a request to the async process.
        """
        return self._send_request('read_resource', args=(), kwargs={'uri': uri})

    def list_resources(self) -> Any:
        return self._send_request('list_resources', args=(), kwargs={})

    def list_prompts(self) -> Any:
        return self._send_request('list_prompts', args=(), kwargs={})

    def list_tools(self) -> Any:
        """
        Lists all available tools synchronously.
        """
        return self._send_request('list_tools', args=(), kwargs={})

    def process_query(self, query: str) -> Any:
        """
        Processes a query synchronously.
        """
        return self._send_request('process_query', args=(query,))


    def cleanup(self):
        """
        Cleans up resources and terminates the process.
        """
        if self.is_running:
            self.is_running = False
            self.request_queue.put('terminate')
            self.join(timeout=100)
            if self.is_alive():
                self.terminate()

# def synced_main():
#     import time
#     client = SyncedMcpClient(server_url="http://0.0.0.0:8080/sse")
#     client.start()
#     result = client.call_tool("get_alerts", {"state": "CA"})
#     print(result)
#     time.sleep(5)


# if __name__ == "__main__":
#     synced_main()