# Teamwork Model Context Protocol

>
> 不能远程调用的MCP 和 不能支撑团队协作的MCP，都是不完整的。
>

本项目封装**极简**MCP的SSE远程调用接口，并集成多个团队的工具集合以供参考。Features：

- 本项目用于快速迭代内部工具和训练内部算法模型。
- 适合快速技术验证。
- 项目中所有工具单元都添加了测试，可一键运行。
- 作为MCP工具推理模型训练基础库开发。

## I. 安装
- 使用uv或者直接使用pip都可以
    ```bash
    uv venv
    uv pip install -e .
    ```

## II. 如何测试

### 1【本地】简单测试一个回声 server-client
- 服务端
    ```bash
    # server
    from teamwork_mcp import FastMCP, launch_mcp_server_forever
    fastmcp = FastMCP("echo")
    @fastmcp.tool()
    async def echo(state: str) -> str:
        return state
    launch_mcp_server_forever(fastmcp=fastmcp, host="0.0.0.0", port=8080)
    ```
- 客户端
    ```python
    # client
    from teamwork_mcp import SyncedMcpClient
    client = SyncedMcpClient(server_url="http://0.0.0.0:8080/sse")
    result = client.list_tools(); print(result)
    result = client.call_tool("echo", {"state": "ABC"}); print(result)
    ```

### 2【本地】为当前库中所有工具建立mcp server

- 服务端
    ```bash
    # server
    from teamwork_mcp import launch_manifest_mcp_server_forever
    launch_manifest_mcp_server_forever()
    ```

### 3【多机 IP + 端口】远程一个阿里云上的 mcp server

- 云服务端
    ```bash
    # server: 47.243.19.78 记得设置安全组
    from teamwork_mcp import launch_manifest_mcp_server_forever
    launch_manifest_mcp_server_forever(port=33333)
    ```

- 客户端
    ```python
    # 客户端
    from teamwork_mcp import SyncedMcpClient
    client = SyncedMcpClient(server_url="http://xxxxxx:33333/sse")
    result = client.list_tools(); print(result)
    result = client.call_tool("echo", {"state": "ABC"}); print(result)
    ```



## III. 如何添加工具

>
> 目前有两种工具封装格式： 
> 一种是pydantic封装，再由qingxu的接口自动转化为mcp的工具，例如 `teamwork_mcp/rfft_tools/firecraw_search.py`（推荐）。 
> 另外一种是原生的mcp封装，见 `teamwork_mcp/dummy_tools/echo.py`。 
> 任选一种采纳。 
>


1. 把工具放在 `${project_dir}/teamwork_mcp/${contributor}_tools` 下。
2. 请写单元测试，命名为 工具名 + _test.py，例如：
    ```
    teamwork_mcp/rfft_tools/code_execution_test.py
    teamwork_mcp/rfft_tools/code_execution.py
    teamwork_mcp/rfft_tools/firecraw_search_test.py
    teamwork_mcp/rfft_tools/firecraw_search.py
    teamwork_mcp/rfft_tools/search_api_qwen_test.py
    teamwork_mcp/rfft_tools/search_api_qwen.py
    teamwork_mcp/rfft_tools/web_scrape_test.py
    teamwork_mcp/rfft_tools/web_scrape.py
    ```
    **提交前请对测试文件进行调试，请确保 `xxxx_test.py` 测试文件能够一键运行**，环境变量建议内嵌到`_test.py`测试代码中。
3. 修改 `${project_dir}/teamwork_mcp/manifest_tool.py` 的 `raw_mcp_tool_manifest_collection` 数组。
4. 运行`launch_server_all_tool_test.py`和`launch_client_test.py`测试。


# Todo

- [] 实现同时接入多个server的高层client



<!-- 
# Upload to PyPI

rm -rf build
rm -rf dist
python -m build
twine upload dist/*
-->