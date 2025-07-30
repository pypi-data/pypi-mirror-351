
from pydantic import BaseModel, Field
from teamwork_mcp.base_tool import BaseTool, cache_to_file
from teamwork_mcp.rfft_tools.alpha_markdown import clean_markdown
from teamwork_mcp.async_utils import execute_with_retry
from textwrap import dedent
import json

def find_free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return int(s.getsockname()[1])

def real_chrome_browser_search(query: str):
    from browser_use import BrowserConfig
    from langchain_openai import ChatOpenAI
    from browser_use import Agent, Browser
    from browser_use.browser.browser import ProxySettings
    from browser_use.browser.context import BrowserContext, BrowserContextConfig
    from best_logger import sprintf_nested_structure
    from pydantic import SecretStr
    import os
    import asyncio
    api_key = os.getenv("DASHSCOPE_API_KEY")
    os.environ["DISPLAY"] = ":1"
    llm=ChatOpenAI(base_url='https://dashscope.aliyuncs.com/compatible-mode/v1', model='qwen-max', api_key=SecretStr(api_key))
    # port = find_free_port()
    # Basic configuration
    config = BrowserConfig(
        headless=False,
        disable_security=False,
        browser_binary_path="/usr/bin/google-chrome-stable",
        # chrome_remote_debugging_port = port,
        extra_browser_args=[
            "--user-data-dir=remote-debug-profile",
        ],
        new_context_config=BrowserContextConfig(
            window_width = 1000,
            window_height = 2000,
            no_viewport = False,
        ),
        # extra_browser_args=[
        #     "--user-data-dir=/home/fuqingxu/teamwork_mcp/xxxx/.config/browseruse/profiles/default"
        # ]
        # proxy=ProxySettings(server="http://8.211.147.173:42313")
    )

    browser = Browser(config=config)
    additional_prompt = dedent(f"""
    要求：
    - 默认使用简体中文，如果问题是英文，则使用英文。
    - 不得访问CSDN、百度知道等低质量网站。
    - 禁止停滞在搜索引擎页面进行任务，必须点开相关网站。
    - 在搜索引擎页面搜索时:
        - 需要首先思考搜索关键词，将关键词按照当前task的相关性降序排列，最后只取前两个关键词。
        - 每个关键词长度不超过5个字或者5个英文单词。
        - 禁止使用OR、AND、NOT等逻辑运算符。
    - 禁止使用必须安装客户端、付费、注册账户才能获取完整内容的网站。遇到类似的网站后，立即退出，更换其他方案。""")
    # " # "关键词之间相互解耦，解除关键词之间的复杂逻辑关联。
    agent = Agent(
        browser=browser,
        task=query + additional_prompt,
        llm=llm,
        enable_memory=False,
        use_vision=False,
    )
    async def main():
        result = await agent.run(max_steps=16)
        return result
    result_raw = asyncio.run(main())
    result = result_raw.model_dump()
    for d in result['history']:
        metadata = d.pop('metadata', None)
        screenshot = d['state'].pop('screenshot', None)
        if len(d['state']['url']) > 100:
            url = d['state'].pop('url', None)
        tabs = d['state'].pop('tabs', None)
        url = d['page_meta'].pop('url', None)
        for d_result in d['result']:
            if isinstance(d_result, dict):
                d_result.pop('is_done', None)
                d_result.pop('success', None)
                d_result.pop('include_in_memory', None)
        interacted_element = d['state'].pop('interacted_element', None)
    only_preseve_last_n = 1
    format_struct = result['history'][-only_preseve_last_n:]
    str_result = sprintf_nested_structure(format_struct, 0)
    os.system("source /home/fuqingxu/.bashrc && killer chrome")
    return str_result




class RealChromeBrowserUse(BaseTool):
    tool_name: str = Field("RealChromeBrowserUse", description="通过真正的Chrome浏览器搜索网页，效率略低，但更稳定，可以访问更广泛的网站。")
    task: str = Field("", description="一句话，描述一个明确的子任务。例如：'获取2024年5月1日阿里巴巴集团控股有限公司的收盘价'。")

    @staticmethod
    def __call__(tool_name_and_param: "RealChromeBrowserUse")->str:
        # return tool_name_and_param.task
        if tool_name_and_param.task == "":
            return "请提供一个有效的搜索关键词。"
        return execute_with_retry(real_chrome_browser_search, query = tool_name_and_param.task)