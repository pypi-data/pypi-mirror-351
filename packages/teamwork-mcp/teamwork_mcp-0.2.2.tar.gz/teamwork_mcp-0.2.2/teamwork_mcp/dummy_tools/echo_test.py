import alpha_init_test # 用于修正路径到项目根目录，请勿删除
from teamwork_mcp.dummy_tools.echo import echo

import asyncio
result = asyncio.run(echo("hello world"))
print(result)