""" From gpt-academic repo. https://github.com/binary-husky/gpt_academic
"""
# import alpha_init_test # 用于修正路径到项目根目录，请勿删除

from teamwork_mcp.academic_tools.pubmed_source import PubmedTool as Tool

fn = Tool().__call__
args = Tool(query="COVID-19", limit=3, sort_by="date")  # 使用更具体的医学相关查询，并按日期排序
result = fn(args)
print(result) 