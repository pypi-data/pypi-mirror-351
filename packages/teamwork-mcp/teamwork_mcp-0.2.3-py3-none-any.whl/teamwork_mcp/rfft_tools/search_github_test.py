import alpha_init_test # 用于修正路径到项目根目录，请勿删除

from teamwork_mcp.rfft_tools.search_github import GithubSearchTool as Tool

fn = Tool().__call__
args = Tool(keyword="ocr", programming_language="python")
result = fn(args)
print(result)


