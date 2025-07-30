
from pydantic import BaseModel, Field
from teamwork_mcp.base_tool import BaseTool, cache_to_file
from teamwork_mcp.rfft_tools.alpha_markdown import clean_markdown
import requests


class GoogleInternetSearch(BaseTool):
    tool_name: str = Field("GoogleInternetSearch", description="通过Google搜索网页")
    keyword: str = Field("", description="搜索网页，例如 “刘慈欣作品” “俄乌谈判进展” 。")

    @staticmethod
    def __call__(tool_name_and_param: "GoogleInternetSearch")->str:
        @cache_to_file()
        def google_search(query: str):
            import pprint
            base_url = "http://xxxxxxxxxxxx/"
            headers = {
                "Host": "pre-nlp-cn-hangzhou.aliyuncs.com",
                "Authorization": "Bearer lm-xxxxxxxxxxxxxxxxxxx",
                "Content-Type": "application/json"
            }
            json_dict = {
                "scene": "dolphin_search_google_mayi_mcp",
                "uq": query,
                "debug": False,
                "fields": [],
                "page": 1,
                "rows": 10,
                "customConfigInfo": {
                    "readpage": True,
                }
            }
            response = requests.post(base_url, headers=headers, json=json_dict)
            consider_top_n = 2
            result_docs = response.json()['data']['docs'][:consider_top_n]
            scrape_result = []
            for i, entry in enumerate(result_docs):
                try: scrape_result += [f"[{i}] {entry['title']} ({entry['url']})\n-------\n{clean_markdown(entry['web_main_body'])}"]
                except: scrape_result += [f"[{i}] {entry['title']} ({entry['url']})\n-------\n"]
            return '\n\n'.join(scrape_result)
        return google_search(query = tool_name_and_param.keyword)

