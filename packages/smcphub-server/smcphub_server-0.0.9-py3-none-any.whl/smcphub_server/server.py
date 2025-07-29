from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from httpx import AsyncClient, HTTPError
import time
import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class SmcphubServer:
    def __init__(self):
        self.services = []
        self.tools = []
        self.endpoint = 'https://www.smcphub.com'
        if os.getenv('APP_ENV', 'production') == 'dev':
            self.endpoint = 'http://localhost:5002'

    def getAuthHeaders(self):
        api_key = os.getenv('SMCPHUB_API_KEY', '')
        return {
            'x-api-key': api_key,
            'x-timestamp': str(int(time.time() * 1000)),
        }

    async def init(self):
        await self.loadAvailableServers()
        await self.serve();

    async def loadAvailableServers(self):
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    self.endpoint + "/mcp/service/list",
                    follow_redirects=True,
                    headers={"Content-Type": "application/json", **self.getAuthHeaders()},
                    timeout=30,
                )
            except HTTPError as e:
                raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to load services: {e!r}"))
        
            if response.status_code >= 400:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to load servers - status code {response.status_code}",
                ))

            services = response.json() or []
        
        # check if length is larger than 0
        if len(services) > 0:
            self.services = services
            print(self.services)
            for service in services:
                serviceTools = service['tools']
                for serviceTool in serviceTools:
                    self.tools.append(Tool(
                        name=serviceTool['name'],
                        description=serviceTool['description'],
                        inputSchema=serviceTool['input_schema'],
                    ));

    def getService(self, name):
        """Returns the service with the given name
        """
        for service in self.services:
            tools = service['tools']
            for tool in tools:
                if tool['name'] == name:
                    return service

        return None

    async def callLocalTool(self, service, name, args):
        """Calls the local tool with the given name and arguments
        """
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        from contextlib import AsyncExitStack

        dev_lang = service['dev_lang'] or 'python'
        package_name = service['package_name'] or ''
        settings = service['settings'] or {}
        parameters = service['parameters'] or []
        
        command = "uvx"
        commandArgs = [package_name]
        env = {**os.environ, **settings}
        if dev_lang == 'js':
            command = "npx"
            commandArgs = ['-y', package_name]

        # Merge parameters with commandArgs
        commandArgs.extend(parameters)

        server_params = StdioServerParameters(
            command=command,
            args=commandArgs,
            env=env,
        )
        
        exit_stack = AsyncExitStack()
        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await exit_stack.enter_async_context(ClientSession(stdio, write))
        # if failed to initialize, it will be always suspended here, so need to check the command and commandArgs carefully
        await session.initialize()

        result = await session.call_tool(name=name, arguments=args)

        await exit_stack.aclose()

        return result.content

    async def callTool(self, name, args):
        """Calls the tool with the given name and arguments

        Args:
            name (str): The name of the tool to call
            args (dict): The arguments to pass to the tool
        """
        service = self.getService(name)
        if service is None:
            return []

        service_id = service['id'] or 0
        exec_env = service['exec_env'] or 'remote'

        if exec_env == 'local':
            items = await self.callLocalTool(service, name, args)
        else:
            async with AsyncClient() as client:
                try:
                    response = await client.post(
                        self.endpoint + "/mcp/tool/call",
                        follow_redirects=True,
                        headers={"Content-Type": "application/json", **self.getAuthHeaders()},
                        timeout=30,
                        json={'service_id': service_id, 'name': name, 'args': args }
                    )
                except HTTPError as e:
                    raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to load services: {e!r}"))
            
                if response.status_code >= 400:
                    raise McpError(ErrorData(
                        code=INTERNAL_ERROR,
                        message=f"Failed to load servers - status code {response.status_code}",
                    ))

                items = response.json()['data'] or []

        return items

    async def serve(self) -> None:
        """Run the Smcphub MCP server.

        Args:
            None
        """
        server = Server("smcphub-server")
        
        @server.list_tools()
        async def list_tools() -> list[Tool]:
            return self.tools

        @server.list_prompts()
        async def list_prompts() -> list[Prompt]:
            return [
                
            ]

        @server.call_tool()
        async def call_tool(name, arguments: dict) -> list[TextContent]:
            textContents = await self.callTool(name=name, args=arguments)
            return textContents

        options = server.create_initialization_options()
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, options, raise_exceptions=True)