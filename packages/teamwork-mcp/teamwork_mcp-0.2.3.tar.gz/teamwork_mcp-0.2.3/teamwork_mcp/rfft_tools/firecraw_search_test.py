import alpha_init_test # 用于修正路径到项目根目录，请勿删除

from teamwork_mcp.rfft_tools.firecraw_search import FirecrawlInternetSearch as Tool

fn = Tool().__call__
args = Tool(keyword="美国独立时间")
result = fn(args)
print(result)