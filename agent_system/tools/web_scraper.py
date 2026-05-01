import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

@tool
def scrape_webpage(url: str) -> str:
    """
    抓取网页正文内容
    
    Args:
        url: 网页URL
    
    Returns:
        网页正文内容
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # 移除脚本和样式
        for script in soup(['script', 'style']):
            script.decompose()
        
        # 提取正文
        text = soup.get_text(separator='\n', strip=True)
        
        # 清理文本
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split(','))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # 限制返回文本长度
        max_length = 3000
        if len(text) > max_length:
            text = text[:max_length] + '... [文本过长，已截断]'
        
        return text
    except Exception as e:
        return f"抓取失败: {str(e)}"
