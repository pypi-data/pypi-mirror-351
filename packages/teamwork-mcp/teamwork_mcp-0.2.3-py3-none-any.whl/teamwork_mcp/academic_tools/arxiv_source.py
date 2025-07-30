""" From gpt-academic repo. https://github.com/binary-husky/gpt_academic
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union, Literal
from teamwork_mcp.base_tool import BaseTool, cache_to_file
from pprint import pprint
from datetime import datetime
from urllib.request import urlretrieve
import feedparser
import arxiv
import os
from tqdm import tqdm

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

class ArxivSource:
    """arXiv API实现"""

    CATEGORIES = {
        # 物理学
        "Physics": {
            "astro-ph": "天体物理学",
            "cond-mat": "凝聚态物理",
            "gr-qc": "广义相对论与量子宇宙学",
            "hep-ex": "高能物理实验",
            "hep-lat": "格点场论",
            "hep-ph": "高能物理理论",
            "hep-th": "高能物理理论",
            "math-ph": "数学物理",
            "nlin": "非线性科学",
            "nucl-ex": "核实验",
            "nucl-th": "核理论",
            "physics": "物理学",
            "quant-ph": "量子物理",
        },

        # 数学
        "Mathematics": {
            "math.AG": "代数几何",
            "math.AT": "代数拓扑",
            "math.AP": "分析与偏微分方程",
            "math.CT": "范畴论",
            "math.CA": "复分析",
            "math.CO": "组合数学",
            "math.AC": "交换代数",
            "math.CV": "复变函数",
            "math.DG": "微分几何",
            "math.DS": "动力系统",
            "math.FA": "泛函分析",
            "math.GM": "一般数学",
            "math.GN": "一般拓扑",
            "math.GT": "几何拓扑",
            "math.GR": "群论",
            "math.HO": "数学史与数学概述",
            "math.IT": "信息论",
            "math.KT": "K理论与同调",
            "math.LO": "逻辑",
            "math.MP": "数学物理",
            "math.MG": "度量几何",
            "math.NT": "数论",
            "math.NA": "数值分析",
            "math.OA": "算子代数",
            "math.OC": "最优化与控制",
            "math.PR": "概率论",
            "math.QA": "量子代数",
            "math.RT": "表示论",
            "math.RA": "环与代数",
            "math.SP": "谱理论",
            "math.ST": "统计理论",
            "math.SG": "辛几何",
        },

        # 计算机科学
        "Computer Science": {
            "cs.AI": "人工智能",
            "cs.CL": "计算语言学",
            "cs.CC": "计算复杂性",
            "cs.CE": "计算工程",
            "cs.CG": "计算几何",
            "cs.GT": "计算机博弈论",
            "cs.CV": "计算机视觉",
            "cs.CY": "计算机与社会",
            "cs.CR": "密码学与安全",
            "cs.DS": "数据结构与算法",
            "cs.DB": "数据库",
            "cs.DL": "数字图书馆",
            "cs.DM": "离散数学",
            "cs.DC": "分布式计算",
            "cs.ET": "新兴技术",
            "cs.FL": "形式语言与自动机理论",
            "cs.GL": "一般文献",
            "cs.GR": "图形学",
            "cs.AR": "硬件架构",
            "cs.HC": "人机交互",
            "cs.IR": "信息检索",
            "cs.IT": "信息论",
            "cs.LG": "机器学习",
            "cs.LO": "逻辑与计算机",
            "cs.MS": "数学软件",
            "cs.MA": "多智能体系统",
            "cs.MM": "多媒体",
            "cs.NI": "网络与互联网架构",
            "cs.NE": "神经与进化计算",
            "cs.NA": "数值分析",
            "cs.OS": "操作系统",
            "cs.OH": "其他计算机科学",
            "cs.PF": "性能评估",
            "cs.PL": "编程语言",
            "cs.RO": "机器人学",
            "cs.SI": "社会与信息网络",
            "cs.SE": "软件工程",
            "cs.SD": "声音",
            "cs.SC": "符号计算",
            "cs.SY": "系统与控制",
        },

        # 定量生物学
        "Quantitative Biology": {
            "q-bio.BM": "生物分子",
            "q-bio.CB": "细胞行为",
            "q-bio.GN": "基因组学",
            "q-bio.MN": "分子网络",
            "q-bio.NC": "神经计算",
            "q-bio.OT": "其他",
            "q-bio.PE": "群体与进化",
            "q-bio.QM": "定量方法",
            "q-bio.SC": "亚细胞过程",
            "q-bio.TO": "组织与器官",
        },

        # 定量金融
        "Quantitative Finance": {
            "q-fin.CP": "计算金融",
            "q-fin.EC": "经济学",
            "q-fin.GN": "一般金融",
            "q-fin.MF": "数学金融",
            "q-fin.PM": "投资组合管理",
            "q-fin.PR": "定价理论",
            "q-fin.RM": "风险管理",
            "q-fin.ST": "统计金融",
            "q-fin.TR": "交易与市场微观结构",
        },

        # 统计学
        "Statistics": {
            "stat.AP": "应用统计",
            "stat.CO": "计算统计",
            "stat.ML": "机器学习",
            "stat.ME": "方法论",
            "stat.OT": "其他统计",
            "stat.TH": "统计理论",
        },

        # 电气工程与系统科学
        "Electrical Engineering and Systems Science": {
            "eess.AS": "音频与语音处理",
            "eess.IV": "图像与视频处理",
            "eess.SP": "信号处理",
            "eess.SY": "系统与控制",
        },

        # 经济学
        "Economics": {
            "econ.EM": "计量经济学",
            "econ.GN": "一般经济学",
            "econ.TH": "理论经济学",
        }
    }

    def __init__(self):
        """初始化"""
        self._initialize()
        self.sort_options = {
            'relevance': arxiv.SortCriterion.Relevance,
            'lastUpdatedDate': arxiv.SortCriterion.LastUpdatedDate,
            'submittedDate': arxiv.SortCriterion.SubmittedDate,
        }
        
        self.sort_order_options = {
            'ascending': arxiv.SortOrder.Ascending,
            'descending': arxiv.SortOrder.Descending
        }
        
        self.default_sort = 'lastUpdatedDate'
        self.default_order = 'descending'
        
    def _initialize(self) -> None:
        """初始化客户端，设置默认参数"""
        self.client = arxiv.Client()

    async def search(
        self,
        query: str,
        limit: int = 10,
        sort_by: str = None,
        sort_order: str = None,
        start_year: int = None
    ) -> List[PaperMetadata]:
        """搜索论文"""
        try:
            if not sort_by or sort_by not in self.sort_options:
                sort_by = self.default_sort
                
            if not sort_order or sort_order not in self.sort_order_options:
                sort_order = self.default_order
                
            if start_year:
                query = f"{query} AND submittedDate:[{start_year}0101 TO 99991231]"
            
            search = arxiv.Search(
                query=query,
                max_results=limit,
                sort_by=self.sort_options[sort_by],
                sort_order=self.sort_order_options[sort_order]
            )
            
            results = list(self.client.results(search))
            return [self._parse_paper_data(result) for result in results]
        except Exception as e:
            print(f"搜索论文时发生错误: {str(e)}")
            return []

    async def search_by_id(self, paper_id: Union[str, List[str]]) -> List[PaperMetadata]:
        """按ID搜索论文"""
        if isinstance(paper_id, str):
            paper_id = [paper_id]
            
        search = arxiv.Search(
            id_list=paper_id,
            max_results=len(paper_id)
        )
        results = list(self.client.results(search))
        return [self._parse_paper_data(result) for result in results]

    async def search_by_category(
        self, 
        category: str, 
        limit: int = 100,
        sort_by: str = 'relevance',
        sort_order: str = 'descending',
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按类别搜索论文"""
        query = f"cat:{category}"
        
        if start_year:
            query = f"{query} AND submittedDate:[{start_year}0101 TO 99991231]"
        
        return await self.search(
            query=query,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )

    async def search_by_authors(
        self, 
        authors: List[str], 
        limit: int = 100,
        sort_by: str = 'relevance',
        start_year: int = None
    ) -> List[PaperMetadata]:
        """按作者搜索论文"""
        query = " AND ".join([f"au:\"{author}\"" for author in authors])
        
        if start_year:
            query = f"{query} AND submittedDate:[{start_year}0101 TO 99991231]"
        
        return await self.search(
            query=query,
            limit=limit,
            sort_by=sort_by
        )

    async def search_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        limit: int = 100,
        sort_by: str = 'submittedDate',
        sort_order: str = 'descending'
    ) -> List[PaperMetadata]:
        """按日期范围搜索论文"""
        query = f"submittedDate:[{start_date.strftime('%Y%m%d')} TO {end_date.strftime('%Y%m%d')}]"
        return await self.search(
            query, 
            limit=limit, 
            sort_by=sort_by, 
            sort_order=sort_order
        )

    async def download_pdf(self, paper_id: str, dirpath: str = "./", filename: str = "") -> str:
        """下载论文PDF"""
        papers = await self.search_by_id(paper_id)
        if not papers:
            raise ValueError(f"未找到ID为 {paper_id} 的论文")
        paper = papers[0]
        
        if not filename:
            safe_title = "".join(c if c.isalnum() else "_" for c in paper.title)
            filename = f"{paper_id}_{safe_title}.pdf"
            
        filepath = os.path.join(dirpath, filename)
        urlretrieve(paper.url, filepath)
        return filepath

    async def download_source(self, paper_id: str, dirpath: str = "./", filename: str = "") -> str:
        """下载论文源文件（通常是LaTeX源码）"""
        papers = await self.search_by_id(paper_id)
        if not papers:
            raise ValueError(f"未找到ID为 {paper_id} 的论文")
        paper = papers[0]
        
        if not filename:
            safe_title = "".join(c if c.isalnum() else "_" for c in paper.title)
            filename = f"{paper_id}_{safe_title}.tar.gz"
            
        filepath = os.path.join(dirpath, filename)
        source_url = paper.url.replace("/pdf/", "/src/")
        urlretrieve(source_url, filepath)
        return filepath

    async def get_paper_details(self, paper_id: str) -> Optional[PaperMetadata]:
        """获取论文详情"""
        try:
            if "arxiv.org" in paper_id:
                paper_id = paper_id.split("/")[-1]
            elif paper_id.startswith("10.48550/arXiv."):
                paper_id = paper_id.split(".")[-1]
                
            papers = await self.search_by_id(paper_id)
            return papers[0] if papers else None
        except Exception as e:
            print(f"获取论文详情时发生错误: {str(e)}")
            return None

    def _parse_paper_data(self, result: arxiv.Result) -> PaperMetadata:
        """解析arXiv API返回的数据"""
        primary_category = result.primary_category
        categories = result.categories
        
        venue_info = {
            'primary_category': primary_category,
            'categories': categories,
            'comments': getattr(result, 'comment', None),
            'journal_ref': getattr(result, 'journal_ref', None)
        }
        
        return PaperMetadata(
            title=result.title,
            authors=[author.name for author in result.authors],
            abstract=result.summary,
            year=result.published.year,
            doi=result.entry_id,
            url=result.pdf_url,
            citations=None,
            venue=f"arXiv:{primary_category}",
            institutions=[],
            venue_type='preprint',
            venue_name='arXiv',
            venue_info=venue_info
        )

    async def get_latest_papers(
        self, 
        category: str, 
        debug: bool = False,
        batch_size: int = 50
    ) -> List[PaperMetadata]:
        """获取指定类别的最新论文"""
        try:
            category = category.lower().replace(' ', '+')
            feed_url = f"https://rss.arxiv.org/rss/{category}"
            print(f"正在获取RSS feed: {feed_url}")
            
            feed = feedparser.parse(feed_url)
            
            if hasattr(feed, 'status') and feed.status != 200:
                raise ValueError(f"获取RSS feed失败，状态码: {feed.status}")
                
            if not feed.entries:
                print(f"警告：未在feed中找到任何条目")
                print(f"Feed标题: {feed.feed.title if hasattr(feed, 'feed') else '无标题'}")
                raise ValueError(f"无效的arXiv类别或未找到论文: {category}")
                
            if debug:
                search = arxiv.Search(
                    query=f'cat:{category}',
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending,
                    max_results=5
                )
                results = list(self.client.results(search))
                return [self._parse_paper_data(result) for result in results]
            
            paper_ids = []
            for entry in feed.entries:
                try:
                    link = entry.link or entry.id
                    arxiv_id = link.split('/')[-1].replace('.pdf', '')
                    if arxiv_id:
                        paper_ids.append(arxiv_id)
                except Exception as e:
                    print(f"警告：处理条目时出错: {str(e)}")
                    continue
                
            if not paper_ids:
                print("未能从feed中提取到任何论文ID")
                return []
                
            print(f"成功提取到 {len(paper_ids)} 个论文ID")
                
            papers = []
            with tqdm(total=len(paper_ids), desc="获取arXiv论文") as pbar:
                for i in range(0, len(paper_ids), batch_size):
                    batch_ids = paper_ids[i:i + batch_size]
                    search = arxiv.Search(
                        id_list=batch_ids,
                        max_results=len(batch_ids)
                    )
                    batch_results = list(self.client.results(search))
                    papers.extend([self._parse_paper_data(result) for result in batch_results])
                    pbar.update(len(batch_results))
                    
            return papers
            
        except Exception as e:
            print(f"获取最新论文时发生错误: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

def basic_arxiv_search(query: str, limit: int = 10, sort_by: str = None, sort_order: str = None):
    """基础arxiv搜索函数"""
    import asyncio
    arxiv_source = ArxivSource()
    result = asyncio.run(arxiv_source.search(
        query=query,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    ))
    
    buffer = ""
    for i, paper in enumerate(result, 1):
        buffer += f"\n--- 论文 {i} ---\n"
        buffer += f"标题: {paper.title}\n"
        buffer += f"作者: {', '.join(paper.authors)}\n"
        buffer += f"发表年份: {paper.year}\n"
        buffer += f"arXiv ID: {paper.doi}\n"
        buffer += f"PDF URL: {paper.url}\n"
        if paper.abstract:
            buffer += f"\n摘要:\n{paper.abstract}\n"
        buffer += f"发表venue: {paper.venue}\n"
    
    return buffer

class ArxivTool(BaseTool):
    tool_name: Optional[str] = Field("ArxivTool", description="搜索arXiv论文")
    query: str = Field("", description="搜索查询词")
    limit: int = Field(10, description="返回结果数量限制")
    sort_by: Optional[str] = Field(None, description="排序方式：relevance, lastUpdatedDate, submittedDate")
    sort_order: Optional[str] = Field(None, description="排序顺序：ascending, descending")

    @staticmethod
    def __call__(tool_name_and_param: "ArxivTool") -> str:
        return basic_arxiv_search(
            query=tool_name_and_param.query,
            limit=tool_name_and_param.limit,
            sort_by=tool_name_and_param.sort_by,
            sort_order=tool_name_and_param.sort_order
        ) 