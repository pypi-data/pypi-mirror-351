import alpha_init_test # 用于修正路径到项目根目录，请勿删除

from teamwork_mcp.rfft_tools.code_execution import CodeExecutionTool as Tool

fn = Tool().__call__
args = Tool(code=
"""
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
    
result = factorial(3)
print(result)
"""
)
result = fn(args)
print(result)


