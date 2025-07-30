from teamwork_mcp.base_tool import BaseTool, cache_to_file
from pydantic import BaseModel, Field
from textwrap import dedent, indent

import asyncio



def remote_function_wrapper(func):
    def wrapper(*args, **kwargs):
        from rfft_utils.websocket_client import RemoteFunctionClient
        client_id = "Y"  # 固定的client ID
        client = RemoteFunctionClient(client_id, server_url="ws://xxxxxxxxxxxxxxxxxxx:9090")

        async def run_client():
            print("connect")
            await client.connect()  # 首先建立连接
            target_client_id = "Z"
            print("remote_call")
            await client.remote_call(target_client_id, func, *args, **kwargs)
            print("get_result")
            result = await client.listen()
            return result

        return asyncio.run(run_client())

    return wrapper





class FinancialMarketNewsSearch(BaseModel):
    tool_name: str = Field("FinancialMarketNewsSearch", description="通过关键词搜索经济相关新闻")
    keyword: str = Field("", description="搜索关键词，例如“新能源市场热点”。")

    @staticmethod
    def __call__(tool_name_and_param: "FinancialMarketNewsSearch")->str:
        @cache_to_file()
        def ant_search(query: str):
            @remote_function_wrapper
            def get_supply(query):
                import requests
                url = 'https://xxxxxxxxxxxxxx/service_run'
                headers = {'Content-Type': 'application/json'}
                data = {
                    "service_id": "xxxxxxxxxxxxxxxxxxxxxxxx",
                    "params": {
                        "input": query,
                        "user_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                        "history": [
                        ]
                    }
                }
                import json
                response = requests.post(url, headers=headers, json=data)
                output_str = str(response.json()['result'])
                try:
                    return json.loads(output_str)['output']['recall_result']['supply_to_str_result']
                except:
                    return "供给获取失败，尝试更换关键词。"

            res = get_supply(query)
            # prompt = dedent("""
            # 请抽取并总结结果中与搜索请求相关的内容，删除搜索结果中与搜索请求无关的内容，达到精炼文本长度的目标。注意：抽取过程中注意解释搜索结果和搜索请求({query})的逻辑关系。
            # 【搜索请求】{query}
            # 【搜索结果】{search_result}
            # """).format(query=query, search_result=res)
            # heavy_llm = OpenaiLLM(model="QwQ", temperature=0, top_k=1, max_tokens=8192)
            # output = LLMHandle().get_llm("Qwen32B").simple_chat(prompt)
            return str(res)
        return ant_search(query = tool_name_and_param.keyword)

