""" From gpt-academic repo. https://github.com/binary-husky/gpt_academic
"""
# import alpha_init_test # 用于修正路径到项目根目录，请勿删除

from teamwork_mcp.academic_tools.arxiv_source import ArxivTool as Tool

fn = Tool().__call__
args = Tool(query="machine learning", limit=3, sort_by="lastUpdatedDate", sort_order="descending")
result = fn(args)
print(result) 