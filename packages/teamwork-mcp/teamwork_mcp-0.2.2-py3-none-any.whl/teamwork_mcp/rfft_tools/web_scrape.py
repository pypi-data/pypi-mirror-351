



from pydantic import BaseModel, Field
from typing import Optional
from teamwork_mcp.base_tool import BaseTool, cache_to_file
from firecrawl.firecrawl import FirecrawlApp # pip install firecrawl-py
from pprint import pprint
from teamwork_mcp.rfft_tools.alpha_markdown import clean_markdown


class GetWebPageContent(BaseTool):
    tool_name: Optional[str] = Field("GetWebPageContent", description="provide a valid url, and get web content in markdown format")
    url: str = Field("", description="a valid web url")

    @staticmethod
    def __call__(tool_name_and_param: "GetWebPageContent")->str:
        @cache_to_file()
        def scrape(url: str):
            app = FirecrawlApp(api_url="http://127.0.0.1:43002", api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            # Scrape a website: https://docs.firecrawl.dev/api-reference/endpoint/scrape
            scrape_status = app.scrape_url(url, formats = ['markdown'])
            return clean_markdown(scrape_status.markdown)
        return scrape(url = tool_name_and_param.url)




