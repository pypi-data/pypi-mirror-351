import alpha_init_test # 用于修正路径到项目根目录，请勿删除

from teamwork_mcp.rfft_tools.web_scrape import GetWebPageContent as Tool

fn = Tool().__call__
args = Tool(url="http://opinion.people.com.cn/n1/2025/0318/c1003-40440881.html")
result = fn(args)
print(result)


