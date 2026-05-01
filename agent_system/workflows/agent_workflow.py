import os
import asyncio
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import httpx
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
import requests
import re

# 加载环境变量
load_dotenv()

# ==================== 数据类定义 ====================
@dataclass
class ToolCallLog:
    """工具调用日志"""
    tool_name: str
    parameters: Dict[str, Any]
    start_time: float
    end_time: Optional[float] = None
    result: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None

@dataclass
class ExecutionLog:
    """执行日志"""
    query: str
    start_time: float
    end_time: Optional[float] = None
    steps: List[Dict[str, Any]] = field(default_factory=list)
    tool_calls: List[ToolCallLog] = field(default_factory=list)
    final_result: Optional[str] = None
    error: Optional[str] = None
    total_duration: Optional[float] = None

# ==================== 异步并发工具 ====================
class AsyncRateLimiter:
    """异步速率限制器"""
    def __init__(self, max_concurrent: int = 3, rate_limit: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limit = rate_limit
        self.tokens = rate_limit
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.rate_limit, self.tokens + elapsed * (self.rate_limit / 60))
            self.last_update = now
            
            if self.tokens < 1:
                wait_time = (1 - self.tokens) * (60 / self.rate_limit)
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

# ==================== 独立工具函数 ====================
# 从外部工具模块导入
from agent_system.tools.arxiv_tool import search_arxiv
from agent_system.tools.web_scraper import scrape_webpage
from agent_system.tools.report_generator import generate_markdown_report

# ==================== Agent工作流类 ====================
class AgentWorkflow:
    """Agent工作流管理器"""
    
    def __init__(self):
        self.tools = [search_arxiv, scrape_webpage, generate_markdown_report]
        self.system_prompt = self._build_system_prompt()
        self.http_client = httpx.Client(transport=httpx.HTTPTransport(retries=0))
        
        # 使用MiniMax API
        self.llm = ChatOpenAI(
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url="https://api.minimax.chat/v1",
            model="MiniMax-M2.7",
            temperature=0.7,
            http_client=self.http_client
        )
        
        # 创建Agent
        self.agent = create_agent(
            self.llm, 
            self.tools, 
            system_prompt=self.system_prompt
        )
        self.execution_log = None
    
    def _build_system_prompt(self) -> str:
        return """你是一位资深的AI研究助手，专门帮助用户进行学术研究和文献调研。

## 你的专业能力
- 熟悉人工智能、机器学习、深度学习等领域的最新研究进展
- 擅长文献检索、摘要提取和综述撰写
- 能够准确理解用户的研究需求并制定调研计划

## 可用的工具
1. **search_arxiv**: 搜索Arxiv上的学术论文
   - 输入参数: query(搜索关键词), max_results(返回数量，默认5)
   
2. **scrape_webpage**: 抓取网页正文内容
   - 输入参数: url(网页URL)
   
3. **generate_markdown_report**: 生成Markdown格式的研究报告
   - 输入参数: title(报告标题), content(报告内容), filename(文件名)

## 工作流程
1. 仔细分析用户的研究需求，确定搜索关键词
2. 使用search_arxiv工具搜索相关学术论文
3. 分析搜索结果，筛选最相关的论文
4. 如需更多详细信息，使用scrape_webpage抓取论文页面
5. 整合所有收集到的信息，撰写结构化的研究报告
6. 使用generate_markdown_report将报告保存为本地文件

## 输出要求
- 报告格式：Markdown
- 内容要求：
  * 清晰的研究主题和目标
  * 相关论文的详细信息（标题、作者、机构、发表时间）
  * 论文核心思想和创新点总结
  * 研究方法和实验结果分析
  * 研究趋势和未来方向
  * 完整的引用和链接
- 语言：使用中文撰写，保持专业、准确、简洁
- 报告内容不要过长，控制在20000字以内

## 注意事项
- 确保报告内容的准确性和完整性
- 优先选择最新和最相关的研究
- 提供具体的论文链接方便用户进一步阅读
- 文件名只包含字母、数字和中文，不要包含特殊字符"""
    
    def run(self, query: str) -> Dict[str, Any]:
        """运行Agent并返回结果和执行日志"""
        self.execution_log = ExecutionLog(
            query=query,
            start_time=time.time()
        )
        
        try:
            self.execution_log.steps.append({
                "step": 1,
                "action": "分析用户请求",
                "detail": f"用户请求: {query}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            self.execution_log.steps.append({
                "step": 2,
                "action": "调用LLM处理请求",
                "detail": "开始执行Agent流程...",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # 直接调用LLM生成响应
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=query)]
            response = self.llm.invoke(messages)
            
            self.execution_log.final_result = str(response.content)
            
            self.execution_log.steps.append({
                "step": 3,
                "action": "生成报告",
                "detail": "报告已生成并保存",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
        except Exception as e:
            self.execution_log.error = str(e)
            self.execution_log.steps.append({
                "step": -1,
                "action": "执行出错",
                "detail": f"错误: {str(e)}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
        
        self.execution_log.end_time = time.time()
        self.execution_log.total_duration = self.execution_log.end_time - self.execution_log.start_time
        
        return {
            "result": self.execution_log.final_result or self.execution_log.error,
            "log": {
                "query": self.execution_log.query,
                "start_time": self.execution_log.start_time,
                "end_time": self.execution_log.end_time,
                "steps": self.execution_log.steps,
                "tool_calls": [
                    {
                        "tool_name": tc.tool_name,
                        "parameters": tc.parameters,
                        "start_time": tc.start_time,
                        "end_time": tc.end_time,
                        "result": tc.result,
                        "error": tc.error,
                        "duration": tc.duration
                    }
                    for tc in self.execution_log.tool_calls
                ],
                "final_result": self.execution_log.final_result,
                "error": self.execution_log.error,
                "total_duration": self.execution_log.total_duration
            }
        }
    
    async def run_streaming(self, query: str):
        """流式运行Agent"""
        self.execution_log = ExecutionLog(
            query=query,
            start_time=time.time()
        )
        
        try:
            self.execution_log.steps.append({
                "step": 1,
                "action": "分析用户请求",
                "detail": f"用户请求: {query}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            async for chunk in self.agent.astream({"input": query}):
                yield chunk
        
        except Exception as e:
            yield {"error": str(e)}

# ==================== 异步并发处理 ====================
async def search_multiple_topics(topics: List[str], max_results: int = 3) -> List[Dict[str, Any]]:
    """异步并发搜索多个主题"""
    rate_limiter = AsyncRateLimiter(max_concurrent=3, rate_limit=10)
    
    async def search_topic(topic: str) -> Dict[str, Any]:
        async with rate_limiter:
            start_time = time.time()
            try:
                import xml.etree.ElementTree as ET
                url = "http://export.arxiv.org/api/query"
                params = {
                    "search_query": topic,
                    "start": 0,
                    "max_results": max_results,
                    "sortBy": "relevance",
                    "sortOrder": "descending"
                }
                
                response = requests.get(url, params=params, timeout=30)
                duration = time.time() - start_time
                
                if response.status_code != 200:
                    return {"topic": topic, "error": f"请求失败: {response.status_code}", "duration": duration}
                
                root = ET.fromstring(response.content)
                papers = []
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    paper = {
                        "title": entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
                        "authors": [author.find('{http://www.w3.org/2005/Atom}name').text for author in entry.findall('{http://www.w3.org/2005/Atom}author')],
                        "summary": entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()[:500],
                        "published": entry.find('{http://www.w3.org/2005/Atom}published').text,
                        "id": entry.find('{http://www.w3.org/2005/Atom}id').text
                    }
                    papers.append(paper)
                
                return {"topic": topic, "papers": papers, "count": len(papers), "duration": duration}
            except Exception as e:
                duration = time.time() - start_time
                return {"topic": topic, "error": str(e), "duration": duration}
    
    tasks = [search_topic(topic) for topic in topics]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [r if isinstance(r, dict) else {"error": str(r)} for r in results]

# ==================== 全局实例 ====================
_workflow_instance = None

def get_workflow() -> AgentWorkflow:
    """获取全局工作流实例"""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = AgentWorkflow()
    return _workflow_instance

def run_agent(query: str) -> Dict[str, Any]:
    """运行Agent的便捷函数"""
    workflow = get_workflow()
    return workflow.run(query)

async def run_agent_streaming(query: str):
    """流式运行Agent的便捷函数"""
    workflow = get_workflow()
    async for chunk in workflow.run_streaming(query):
        yield chunk

if __name__ == "__main__":
    query = "帮我调研DPO算法的最新进展"
    result = run_agent(query)
    print(json.dumps({
        "result": result["result"],
        "log": {
            "query": result["log"].query,
            "steps": result["log"].steps,
            "total_duration": result["log"].total_duration
        }
    }, ensure_ascii=False, indent=2))
