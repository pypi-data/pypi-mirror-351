from firecrawl.firecrawl import FirecrawlApp, SearchParams, ScrapeParams, DeepResearchParams # pip install firecrawl-py
from teamwork_mcp.rfft_tools.alpha_markdown import clean_markdown

from pydantic import BaseModel, Field
from teamwork_mcp.base_tool import BaseTool, cache_to_file
from teamwork_mcp.rfft_tools.alpha_markdown import clean_markdown


class FirecrawlInternetSearch(BaseTool):
    tool_name: str = Field("FirecrawlInternetSearch", description="通过Firecrawl引擎搜索网页并获取检索到的网页的内容。速度快但效果不稳定，建议首先尝试，如果效果不理想再切换其他工具。")
    keyword: str = Field("", description="搜索网页的一组关键词，例如 “刘慈欣作品” “俄乌谈判进展” 。要求：需要首先思考搜索关键词，将关键词按照当前task的相关性降序排列，最后只取前两个关键词。每个关键词长度不超过5个字或者5个英文单词。禁止使用OR、AND、NOT等逻辑运算符。")

    @staticmethod
    def __call__(tool_name_and_param: "FirecrawlInternetSearch")->str:
        def firecrawl_search(query: str):
            app = FirecrawlApp(api_url="http://127.0.0.1:43002", api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            scrape_status = app.search(query, timeout=10000, scrape_options=ScrapeParams(formats=['markdown']))
            scrape_result = []

            for i, entry in enumerate(scrape_status.data):
                try:
                    if 'markdown' in entry:
                        main_content = entry['markdown']
                    else:
                        main_content = entry['description']
                    main_content = clean_markdown(main_content)
                    scrape_result += [f"[{i}] {entry['title']} ({entry['url']})\n-------\n{main_content}"]
                except Exception as e:
                    continue

            return scrape_result, scrape_status

        scrape_result, scrape_status = firecrawl_search(query = tool_name_and_param.keyword)
        return '\n\n'.join(scrape_result)
