import alpha_init_test # 用于修正路径到项目根目录，请勿删除

from teamwork_mcp.rfft_tools.search_financial_mxc import FinancialMarketNewsSearch as Tool

fn = Tool().__call__
args = Tool(keyword="俄乌战争")
result = fn(args)
print(result)