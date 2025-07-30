import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
import os

class GitHubAPIClient:
    """GitHub API 客户端实现"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化GitHub API客户端
        
        Args:
            api_key: GitHub Personal Access Token
        """
        self.api_key = api_key or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Python-GitHub-API-Client/1.0",
        }
        if self.api_key:
            self.headers["Authorization"] = f"token {self.api_key}"

    async def search_repositories(
        self,
        query: str,
        sort_by: str = "stars",
        order: str = "desc",
        limit: int = 30
    ) -> List[Dict]:
        """搜索GitHub仓库
        
        Args:
            query: 搜索关键词
            sort_by: 排序字段 (stars, forks, updated)
            order: 排序顺序 (asc, desc)
            limit: 返回结果数量限制
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            params = {
                "q": query,
                "sort": sort_by,
                "order": order,
                "per_page": min(limit, 100)
            }
            
            async with session.get(
                f"{self.base_url}/search/repositories",
                params=params
            ) as response:
                if response.status != 200:
                    print(f"API请求失败: HTTP {response.status}")
                    print(f"响应内容: {await response.text()}")
                    return []
                
                data = await response.json()
                return data.get("items", [])

    async def get_repository_details(self, owner: str, repo: str) -> Optional[Dict]:
        """获取仓库详细信息"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}"
            ) as response:
                if response.status != 200:
                    print(f"获取仓库信息失败: HTTP {response.status}")
                    return None
                return await response.json()

    async def get_repository_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        limit: int = 30
    ) -> List[Dict]:
        """获取仓库的issue列表"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            params = {
                "state": state,
                "per_page": min(limit, 100)
            }
            
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                params=params
            ) as response:
                if response.status != 200:
                    print(f"获取issues失败: HTTP {response.status}")
                    return []
                return await response.json()

    async def get_repository_contents(
        self,
        owner: str,
        repo: str,
        path: str = ""
    ) -> Optional[Dict]:
        """获取仓库文件或目录内容"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            ) as response:
                if response.status != 200:
                    print(f"获取仓库内容失败: HTTP {response.status}")
                    return None
                return await response.json()

    async def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                f"{self.base_url}/users/{username}"
            ) as response:
                if response.status != 200:
                    print(f"获取用户信息失败: HTTP {response.status}")
                    return None
                return await response.json()

async def example_usage(keyword, programming_language='python'):
    """GitHubAPIClient使用示例"""
    # 创建客户端实例
    github = GitHubAPIClient()
    buffer = ""
    try:
        # 示例1：搜索仓库
        buffer += ("\n===  ===\n")
        repos = await github.search_repositories(
            query=f"{keyword} language:{programming_language}",
            sort_by="stars",
            limit=3
        )
        
        for i, repo in enumerate(repos, 1):
            buffer += (f"\n--- 仓库 {i} ---\n")
            buffer += (f"名称: {repo['full_name']}\n")
            buffer += (f"描述: {repo['description']}\n")
            buffer += (f"Stars: {repo['stargazers_count']}\n")
            buffer += (f"Forks: {repo['forks_count']}\n")
            buffer += (f"URL: {repo['html_url']}\n")

            # 示例2：获取特定仓库详情
            if repo:
                buffer += ("\n===  ===\n")
                owner, repo_name = repo['full_name'].split('/')
                repo_details = await github.get_repository_details(owner, repo_name)
                if repo_details:
                    buffer += (f"仓库名称: {repo_details['name']}\n")
                    buffer += (f"创建时间: {repo_details['created_at']}\n")
                    buffer += (f"最后更新: {repo_details['updated_at']}\n")
                    buffer += (f"主要语言: {repo_details['language']}\n")


                # 示例4：获取仓库内容
                buffer += ("\n===  ===\n")
                contents = await github.get_repository_contents(owner, repo_name)
                if isinstance(contents, list):
                    buffer += ("\n仓库文件列表:\n")
                    for item in contents:
                        buffer += (f"- {item['name']} ({item['type']})\n")

                # 示例5：获取用户信息
                buffer += ("\n===  ===\n")
                user_info = await github.get_user_info(owner)
                if user_info:
                    buffer += (f"用户名: {user_info['login']}\n")
                    buffer += (f"Name: {user_info.get('name', 'N/A')}\n")
                    buffer += (f"Bio: {user_info.get('bio', 'N/A')}\n")
                    buffer += (f"公开仓库数: {user_info['public_repos']}\n")
                    buffer += (f"Followers: {user_info['followers']}\n")
        return buffer
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())

def basic_github_search(keyword, programming_language):
    import asyncio
    result = asyncio.run(example_usage(keyword, programming_language)) 
    return result



from pydantic import BaseModel, Field
from typing import Optional
from teamwork_mcp.base_tool import BaseTool, cache_to_file
from pprint import pprint
from teamwork_mcp.rfft_tools.alpha_markdown import clean_markdown


class GithubSearchTool(BaseTool):
    tool_name: Optional[str] = Field("GithubSearchTool", description="给定网址url，获取网页内容")
    keyword: str = Field("", description="Github关键词")
    programming_language: str = Field("", description="编程语言如 python javascript 等")

    @staticmethod
    def __call__(tool_name_and_param: "GithubSearchTool")->str:
        return basic_github_search(tool_name_and_param.keyword, tool_name_and_param.programming_language)


