import requests
import xml.etree.ElementTree as ET
from langchain_core.tools import tool

@tool
def search_arxiv(query: str, max_results: int = 5) -> str:
    """
    搜索Arxiv上的学术论文
    
    Args:
        query: 搜索关键词
        max_results: 返回的最大结果数（默认5）
    
    Returns:
        包含论文信息的列表
    """
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return f"请求失败: {response.status_code}"
    
    # 解析XML响应
    root = ET.fromstring(response.content)
    
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        paper = {
            "title": entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
            "authors": [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')],
            "summary": entry.find('{http://www.w3.org/2005/Atom}summary').text.strip(),
            "published": entry.find('{http://www.w3.org/2005/Atom}published').text,
            "id": entry.find('{http://www.w3.org/2005/Atom}id').text
        }
        papers.append(paper)
    
    return str(papers)
