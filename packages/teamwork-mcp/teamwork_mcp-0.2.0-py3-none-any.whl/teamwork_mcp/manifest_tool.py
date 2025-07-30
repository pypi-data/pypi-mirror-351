import json
from teamwork_mcp.rfft_tools.code_execution import CodeExecutionTool
from teamwork_mcp.rfft_tools.firecraw_search import FirecrawlInternetSearch
from teamwork_mcp.rfft_tools.search_api_qwen import GoogleInternetSearch
from teamwork_mcp.rfft_tools.web_scrape import GetWebPageContent
from teamwork_mcp.academic_tools.arxiv_source import ArxivTool
from teamwork_mcp.academic_tools.pubmed_source import PubmedTool
from teamwork_mcp.rfft_tools.search_financial_mxc import FinancialMarketNewsSearch
from teamwork_mcp.rfft_tools.real_chrome_browser import RealChromeBrowserUse
from textwrap import dedent, indent

def make_tool_collection(*cls_list):
    return {cls: cls.__call__ for cls in cls_list}

# tool_manifest = [CodeExecutionTool, FirecrawlInternetSearch, GoogleInternetSearch, GetWebPageContent, ArxivTool, PubmedTool, FinancialMarketNewsSearch]
tool_manifest = [CodeExecutionTool, RealChromeBrowserUse]
# tool_manifest = [CodeExecutionTool, GetWebPageContent, RealChromeBrowserUse]
tool_manifest_collection = make_tool_collection(*tool_manifest)
raw_mcp_tool_manifest_collection = []

def tool_manifest_prompt():
    tools_formatted = ""
    for i, tool in enumerate(tool_manifest_collection.keys()):
        reduced_schema = tool.model_json_schema()
        if "title" in reduced_schema: reduced_schema.pop("title")
        if "type" in reduced_schema: reduced_schema.pop("type")
        schema_str = json.dumps(reduced_schema, ensure_ascii=False)
        tools_formatted += f"工具{i+1} {tool().tool_name} ({tool.model_fields['tool_name'].description}) \n"
        tools_formatted += f"工具{i+1} 调用schema {schema_str} \n"
        tools_formatted += f"---\n"
    print(tools_formatted)
    return tools_formatted


def all_tool_manifest_prompt(mcp_list_tool_result, print_formatted=True):
    tools_formatted = ""
    for i, tool in enumerate(mcp_list_tool_result.tools):
        reduced_schema = tool.inputSchema
        tools_formatted += f"工具{i+1} {tool.name} ({tool.description}) \n"
        tools_formatted += f"工具{i+1} 调用schema {reduced_schema} \n"
        tools_formatted += f"---\n"
    if print_formatted: print(tools_formatted)
    return tools_formatted
