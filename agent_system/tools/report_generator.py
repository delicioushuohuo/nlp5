import os
from langchain_core.tools import tool

@tool
def generate_markdown_report(title: str, content: str, filename: str) -> str:
    """
    生成Markdown格式的报告
    
    Args:
        title: 报告标题
        content: 报告内容
        filename: 保存的文件名（不含扩展名）
    
    Returns:
        保存的文件路径
    """
    # 确保reports目录存在
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # 构建完整的文件路径
    file_path = os.path.join(reports_dir, f"{filename}.md")
    
    # 生成Markdown内容
    markdown_content = f"# {title}\n\n{content}"
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return file_path
