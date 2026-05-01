# AI Research Assistant

基于 MiniMax-M2.7 API 的智能学术研究助手，支持文献检索、报告生成、图片创作。

## 功能特性

### 研究助手
- 📚 ArXiv 论文搜索
- 🌐 网页内容抓取
- 📄 Markdown 报告生成

### 图片生成
- 🎨 Text-to-Image 图片生成
- ✏️ 图片局部编辑/重绘

### 预设主题
- DPO 算法最新进展
- LLM 对齐技术
- 多模态大模型
- RLHF 强化学习

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

## 环境配置

在 `.env` 文件中配置 API 密钥：

```
MINIMAX_API_KEY=your_api_key_here
```

## 项目结构

```
.
├── app.py                      # Streamlit 主应用
├── agent_system/
│   ├── tools/                  # 工具模块
│   │   ├── arxiv_tool.py       # ArXiv 搜索
│   │   ├── web_scraper.py      # 网页抓取
│   │   ├── report_generator.py # 报告生成
│   │   └── image_generation.py # 图片生成
│   ├── workflows/              # Agent 工作流
│   │   └── agent_workflow.py
│   └── reports/                # 生成的报告
└── images/                    # 生成的图片
```

## API 模型

- **文本模型**: MiniMax-M2.7
- **图像模型**: MiniMax Image-01

## 技术栈

- Python 3.8+
- Streamlit
- LangChain
- httpx