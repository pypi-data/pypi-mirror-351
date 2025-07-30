import alpha_init_test # 用于修正路径到项目根目录，请勿删除

from teamwork_mcp.rfft_tools.real_chrome_browser import RealChromeBrowserUse as Tool

fn = Tool().__call__
args = Tool(keyword="what is the close price of Alibaba Group Holding Limited (BABA) on 2025-5-12?")
result = fn(args)
print(result)

