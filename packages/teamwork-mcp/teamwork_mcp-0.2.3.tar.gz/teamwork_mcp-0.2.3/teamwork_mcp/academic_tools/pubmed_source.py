""" From gpt-academic repo. https://github.com/binary-husky/gpt_academic
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union
from teamwork_mcp.base_tool import BaseTool, cache_to_file
from pprint import pprint
import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from urllib.parse import quote
import json
from tqdm import tqdm
import random

class PaperMetadata(BaseModel):
    """论文元数据类"""
    title: str
    authors: List[str]
    abstract: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citations: Optional[int] = None
    venue: Optional[str] = None
    institutions: List[str] = []
    venue_type: Optional[str] = None
    venue_name: Optional[str] = None
    venue_info: Optional[Dict] = None

class PubmedSource:
    """PubMed API实现"""
    
    # 定义API密钥列表
    API_KEYS = [
        "key_96d571a7d476ac73739547f8"

    ]
    
    def __init__(self, api_key: str = None):
        """初始化"""
        self.api_key = api_key or random.choice(self.API_KEYS)
        self._initialize()
        
    def _initialize(self) -> None:
        """初始化基础URL和请求头"""
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.headers = {
            "User-Agent": "Mozilla/5.0 PubMedDataSource/1.0",
            "Accept": "application/json"
        }
        
    async def _make_request(self, url: str) -> Optional[str]:
        """发送HTTP请求"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"请求失败: {response.status}")
                        return None
        except Exception as e:
            print(f"请求发生错误: {str(e)}")
            return None
            
    async def search(
        self,
        query: str,
        limit: int = 100,
        sort_by: str = "relevance",
        start_year: int = None
    ) -> List[PaperMetadata]:
        """搜索论文"""
        try:
            if start_year:
                query = f"{query} AND {start_year}:3000[dp]"
                
            search_url = (
                f"{self.base_url}/esearch.fcgi?"
                f"db=pubmed&term={quote(query)}&retmax={limit}"
                f"&usehistory=y&api_key={self.api_key}"
            )
            
            if sort_by == "date":
                search_url += "&sort=date"
                
            response = await self._make_request(search_url)
            if not response:
                return []
                
            root = ET.fromstring(response)
            id_list = root.findall(".//Id")
            pmids = [id_elem.text for id_elem in id_list]
            
            if not pmids:
                return []
                
            papers = []
            batch_size = 50
            for i in range(0, len(pmids), batch_size):
                batch = pmids[i:i + batch_size]
                batch_papers = await self._fetch_papers_batch(batch)
                papers.extend(batch_papers)
                
            return papers
            
        except Exception as e:
            print(f"搜索论文时发生错误: {str(e)}")
            return []
            
    async def _fetch_papers_batch(self, pmids: List[str]) -> List[PaperMetadata]:
        """批量获取论文详情"""
        try:
            fetch_url = (
                f"{self.base_url}/efetch.fcgi?"
                f"db=pubmed&id={','.join(pmids)}"
                f"&retmode=xml&api_key={self.api_key}"
            )
            
            response = await self._make_request(fetch_url)
            if not response:
                return []
                
            root = ET.fromstring(response)
            articles = root.findall(".//PubmedArticle")
            
            return [self._parse_article(article) for article in articles]
            
        except Exception as e:
            print(f"获取论文批次时发生错误: {str(e)}")
            return []
            
    def _parse_article(self, article: ET.Element) -> PaperMetadata:
        """解析PubMed文章XML"""
        try:
            pmid = article.find(".//PMID").text
            article_meta = article.find(".//Article")
            
            title = article_meta.find(".//ArticleTitle")
            title = title.text if title is not None else ""
            
            authors = []
            author_list = article_meta.findall(".//Author")
            for author in author_list:
                last_name = author.find("LastName")
                fore_name = author.find("ForeName")
                if last_name is not None and fore_name is not None:
                    authors.append(f"{fore_name.text} {last_name.text}")
                elif last_name is not None:
                    authors.append(last_name.text)
                    
            abstract = article_meta.find(".//Abstract/AbstractText")
            abstract = abstract.text if abstract is not None else ""
            
            pub_date = article_meta.find(".//PubDate/Year")
            year = int(pub_date.text) if pub_date is not None else None
            
            doi = article.find(".//ELocationID[@EIdType='doi']")
            doi = doi.text if doi is not None else None
            
            journal = article_meta.find(".//Journal")
            if journal is not None:
                journal_title = journal.find(".//Title")
                venue = journal_title.text if journal_title is not None else None
                
                venue_info = {
                    'issn': journal.findtext(".//ISSN"),
                    'volume': journal.findtext(".//Volume"),
                    'issue': journal.findtext(".//Issue"),
                    'pub_date': journal.findtext(".//PubDate/MedlineDate") or 
                               f"{journal.findtext('.//PubDate/Year', '')}-{journal.findtext('.//PubDate/Month', '')}"
                }
            else:
                venue = None
                venue_info = {}
                
            institutions = []
            affiliations = article_meta.findall(".//Affiliation")
            for affiliation in affiliations:
                if affiliation is not None and affiliation.text:
                    institutions.append(affiliation.text)
                    
            return PaperMetadata(
                title=title,
                authors=authors,
                abstract=abstract,
                year=year,
                doi=doi,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
                citations=None,
                venue=venue,
                institutions=institutions,
                venue_type="journal",
                venue_name=venue,
                venue_info=venue_info
            )
            
        except Exception as e:
            print(f"解析文章时发生错误: {str(e)}")
            return None

def basic_pubmed_search(query: str, limit: int = 10, sort_by: str = None):
    """基础pubmed搜索函数"""
    import asyncio
    pubmed_source = PubmedSource()
    result = asyncio.run(pubmed_source.search(
        query=query,
        limit=limit,
        sort_by=sort_by
    ))
    
    buffer = ""
    for i, paper in enumerate(result, 1):
        buffer += f"\n--- 论文 {i} ---\n"
        buffer += f"标题: {paper.title}\n"
        buffer += f"作者: {', '.join(paper.authors)}\n"
        buffer += f"发表年份: {paper.year}\n"
        buffer += f"DOI: {paper.doi}\n"
        buffer += f"URL: {paper.url}\n"
        if paper.abstract:
            buffer += f"\n摘要:\n{paper.abstract}\n"
        buffer += f"发表venue: {paper.venue}\n"
        if paper.institutions:
            buffer += f"机构: {', '.join(paper.institutions)}\n"
    
    return buffer

class PubmedTool(BaseTool):
    tool_name: Optional[str] = Field("PubmedTool", description="搜索PubMed论文")
    query: str = Field("", description="搜索查询词")
    limit: int = Field(10, description="返回结果数量限制")
    sort_by: Optional[str] = Field(None, description="排序方式：relevance, date")

    @staticmethod
    def __call__(tool_name_and_param: "PubmedTool") -> str:
        return basic_pubmed_search(
            query=tool_name_and_param.query,
            limit=tool_name_and_param.limit,
            sort_by=tool_name_and_param.sort_by
        ) 