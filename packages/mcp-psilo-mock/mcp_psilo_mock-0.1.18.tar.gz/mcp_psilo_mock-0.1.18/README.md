# MCP for PSILO


There are 3 main folders:
- mcp_psilo_in_progress/
    - Code being developed (in progress)
        - `client_sse.py`, `client_stdio.py`, `server_sse.py` all work
        - `client_http.py`, `server_http.py` does not work
- mcp_psilo_mock/
    - This code is published in PyPI: https://pypi.org/project/mcp-psilo-mock/
        - `server_stdio.py` contains the key get_psilo_data function
        - `server_stdio2.py` contains is an extra stdio_server used to test connecting to multiple MCP servers with Claude desktop
- test_code/
    - `test_right_package.py` Contains scripts to run the servers and clients in the two above folders
        - `test_right_package.py` is used to determine where mcp_psilo_mock is coming from (from this repo or from the published package) [this was cerated to assist when deploying the package]
    - `test_run_sse_client.py` is not importing the sse_client package from mcp; an alternative must be found
    - `test_run_sse_server.py`, `test_run_stdio_client.py`, `test_run_stdio_server.py`, and `test_run_stdio_client.py` all work




-----------
Archived notes


server_stdio.py and client_stdio.py both work with standard input/output. However, the client runs the server as a subprocess. 


We need the server to run independently (and connect via something like http). server_http.py and client_http.py are attempts to have it work, but connection through http doesn't work with the current mcp library.

The issues with running http are found below:
1. FastMCP has no .app or .asgi_app() method
    * So you can’t do: uvicorn.run(mcp.app, ...)
    * This makes it incompatible with uvicorn in current form
2. FastMCP.run() only supports stdio, not network transport
3. fastapi_mcp not viable or missing
    * Either unavailable, misinstalled, or not meant for your current MCP version
4. HTTP-based tool exposure not built-in in your installed MCP version
    * You’d have to write a manual FastAPI wrapper (no real MCP involved)