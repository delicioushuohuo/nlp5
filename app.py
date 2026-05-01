import streamlit as st
import asyncio
import time
import os
import json
from datetime import datetime

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 初始化Session State ====================
if "history" not in st.session_state:
    st.session_state.history = []

if "current_result" not in st.session_state:
    st.session_state.current_result = None

if "theme" not in st.session_state:
    st.session_state.theme = "浅色"

# ==================== 辅助函数 ====================
def get_reports():
    """获取报告列表"""
    reports_dir = os.path.join(os.path.dirname(__file__), "agent_system", "reports")
    if not os.path.exists(reports_dir):
        return []
    return sorted(
        [f for f in os.listdir(reports_dir) if f.endswith(".md")],
        key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)),
        reverse=True
    )

def delete_report(filename):
    """删除报告"""
    reports_dir = os.path.join(os.path.dirname(__file__), "agent_system", "reports")
    path = os.path.join(reports_dir, filename)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

def load_report_content(filename):
    """读取报告内容"""
    reports_dir = os.path.join(os.path.dirname(__file__), "agent_system", "reports")
    path = os.path.join(reports_dir, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def render_markdown_with_code(content):
    """渲染带代码高亮的markdown"""
    st.markdown(content)

# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("⚙️ AI研究助手")
    st.markdown("---")

    # ----- 模型配置 -----
    st.markdown("### 🤖 模型配置")

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="控制输出的随机性。较低值更确定性，较高值更有创意。"
    )

    max_results = st.number_input(
        "最大搜索结果数",
        min_value=1,
        max_value=20,
        value=5,
        help="Arxiv搜索返回的最大论文数量"
    )

    st.markdown("---")

    # ----- 系统提示词 -----
    st.markdown("### 📝 系统提示词")

    with st.expander("自定义提示词", expanded=False):
        custom_system_prompt = st.text_area(
            "留空使用默认提示词",
            value="",
            height=120,
            placeholder="例如：你是一位专注AI安全的研究助手..."
        )
        use_custom = st.checkbox("启用自定义提示词")

    st.markdown("---")

    # ----- 外观设置 -----
    st.markdown("### 🎨 外观")

    theme_options = ["🌞 浅色", "🌙 深色"]
    theme_choice = st.radio("选择主题", theme_options, index=0 if st.session_state.theme == "浅色" else 1)

    if theme_choice == "🌙 深色":
        st.session_state.theme = "深色"
        st.markdown("""
        <style>
        .stApp { background-color: #1a1a2e; color: white; }
        .css-1d391kg { background-color: #1a1a2e; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.session_state.theme = "浅色"

    st.markdown("---")

    # ----- 执行历史 -----
    st.markdown("### 📜 执行历史")

    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-5:])):
            query_preview = item["query"][:25] + "..." if len(item["query"]) > 25 else item["query"]
            with st.expander(f"查询: {query_preview}", expanded=False):
                st.caption(f"⏱️ {item.get('duration', 0):.2f}秒")
                st.caption(f"📊 {len(item.get('steps', []))}步")
                if st.button("加载结果", key=f"load_{i}"):
                    st.session_state.current_result = item
                    st.rerun()
                if st.button("删除", key=f"del_hist_{i}"):
                    st.session_state.history.remove(item)
                    st.rerun()
    else:
        st.caption("暂无执行历史")

    st.markdown("---")

    # ----- 报告历史 -----
    st.markdown("### 📁 报告历史")

    reports = get_reports()
    if reports:
        for report in reports[:8]:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"📄 `{report[:40]}...`" if len(report) > 40 else f"📄 `{report}`")
            with col2:
                if st.button("🗑️", key=f"del_{report}"):
                    delete_report(report)
                    st.rerun()
            # 显示文件修改时间
            reports_dir = os.path.join(os.path.dirname(__file__), "agent_system", "reports")
            mtime = os.path.getmtime(os.path.join(reports_dir, report))
            st.caption(f"   {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')}")
    else:
        st.caption("暂无报告")

    st.markdown("---")

    # ----- 图片生成 -----
    st.markdown("### 🎨 图片生成")

    with st.expander("生成图片", expanded=False):
        img_prompt = st.text_area("图片描述", placeholder="描述你想要生成的图片...", key="img_prompt")
        img_col1, img_col2 = st.columns(2)
        with img_col1:
            img_size = st.selectbox("尺寸", ["512x512", "768x768", "1024x1024", "1536x1536"], index=2, key="img_size")
        with img_col2:
            img_style = st.selectbox("风格", ["natural", "vivid"], index=0, key="img_style")

        if st.button("🎨 生成图片", key="generate_img_btn", use_container_width=True):
            if img_prompt:
                with st.spinner("🎨 正在生成图片..."):
                    try:
                        from agent_system.tools.image_generation import generate_image
                        result = generate_image.invoke({
                            "prompt": img_prompt,
                            "size": img_size,
                            "style": img_style
                        })
                        st.session_state.last_image_result = result
                        st.rerun()
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
            else:
                st.warning("请输入图片描述")

    if "last_image_result" in st.session_state:
        st.markdown(f"✅ {st.session_state.last_image_result}")

    # ----- 图片历史 -----
    st.markdown("#### 📷 生成的图片")

    images_dir = os.path.join(os.path.dirname(__file__), "agent_system", "images")
    if os.path.exists(images_dir):
        image_files = sorted(
            [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))],
            key=lambda x: os.path.getmtime(os.path.join(images_dir, x)),
            reverse=True
        )
        if image_files:
            for img_file in image_files[:6]:
                img_path = os.path.join(images_dir, img_file)
                st.image(img_path, width=150, caption=img_file)
                with open(img_path, 'rb') as f:
                    img_bytes = f.read()
                st.download_button(
                    "下载",
                    data=img_bytes,
                    file_name=img_file,
                    mime="image/png",
                    key=f"dl_{img_file}"
                )
        else:
            st.caption("暂无生成的图片")
    else:
        st.caption("暂无生成的图片")

# ==================== 主界面 ====================
st.title("🔬 AI Research Assistant")
st.markdown("基于云端API的Agent工具系统 · 自动化学术研究助手")

# ----- 预设主题 -----
st.markdown("### ⚡ 快速开始")

presets = {
    "🔬 DPO算法最新进展": "帮我调研2026年关于DPO算法的最新进展",
    "🧠 LLM对齐技术": "收集最近关于大语言模型对齐技术的研究",
    "🎨 多模态大模型": "调研多模态大模型的最新应用",
    "📊 RLHF最新研究": "帮我调研RLHF强化学习最新研究进展"
}

cols = st.columns(4)
for col, (label, query) in zip(cols, presets.items()):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state.query_input = query
            st.rerun()

# 检查是否有预设查询
query_input = st.session_state.get("query_input", "")
st.markdown("---")

# ----- 输入区域 -----
st.markdown("### 🔍 开始调研")

user_query = st.text_input(
    "请输入您的研究需求",
    value=query_input,
    placeholder="例如：帮我调研2026年关于DPO算法的最新进展",
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 5])
with col1:
    run_button = st.button("🚀 开始调研", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ 清除", use_container_width=True)

if clear_button:
    st.session_state.query_input = ""
    st.session_state.current_result = None
    st.rerun()

# ----- 显示历史结果或当前结果 -----
if st.session_state.current_result and not run_button:
    result = st.session_state.current_result
    execution_log = result.get("log", {})
    steps = execution_log.get("steps", [])
    total_duration = execution_log.get("total_duration", 0)
    final_result = execution_log.get("final_result", "")
    error = execution_log.get("error")

    tab1, tab2 = st.tabs(["🔍 执行过程", "📄 最终报告"])

    with tab1:
        st.markdown("#### 📊 执行摘要")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总耗时", f"{total_duration:.2f}秒")
        with col2:
            st.metric("执行步骤", len(steps))
        with col3:
            status = "✅ 成功" if not error else "❌ 失败"
            st.metric("执行状态", status)

        st.markdown("#### 🔄 详细执行步骤")
        for i, step in enumerate(steps):
            step_num = step.get("step", i+1)
            action = step.get("action", "")
            detail = step.get("detail", "")
            timestamp = step.get("timestamp", "")

            if step_num > 0:
                with st.expander(f"步骤 {step_num}: {action} ⏱️ {timestamp}", expanded=i >= len(steps)-2):
                    st.markdown(f"**动作**: {action}")
                    st.markdown(f"**详情**: {detail}")
            else:
                with st.expander(f"❌ 出错: {action}", expanded=True):
                    st.markdown(f"**错误**: {detail}")

        with st.expander("📜 原始执行日志"):
            st.json(execution_log)

    with tab2:
        if error:
            st.error(f"执行出错: {error}")
        else:
            if final_result:
                st.markdown(final_result)
            else:
                st.info("无结果")

            reports = get_reports()
            if reports:
                st.markdown("---")
                st.markdown("#### 📁 生成的报告文件")
                for report in reports[:5]:
                    content = load_report_content(report)
                    if content:
                        with st.expander(f"📄 {report}", expanded=False):
                            st.markdown(content[:1000] + "..." if len(content) > 1000 else content)

# ----- 执行查询 -----
if run_button and user_query:
    start_time = time.time()

    # 创建标签页
    tab1, tab2 = st.tabs(["🔍 执行过程", "📄 最终报告"])

    with tab1:
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.info("🚀 正在初始化Agent工作流...")

    try:
        from agent_system.workflows.agent_workflow import run_agent

        # 确定使用的系统提示词
        system_prompt = custom_system_prompt if use_custom and custom_system_prompt else None

        # 更新进度
        with tab1:
            progress_bar.progress(20)
            status_text.info("🤔 Agent正在分析和规划...")

        with st.spinner("🤔 Agent正在思考中，请稍候..."):
            result = run_agent(
                query=user_query,
                temperature=temperature,
                max_results=max_results,
                system_prompt=system_prompt
            )

        execution_log = result.get("log", {})
        steps = execution_log.get("steps", [])
        total_duration = execution_log.get("total_duration", 0)
        final_result = execution_log.get("final_result", "")
        error = execution_log.get("error")

        # 保存到历史
        history_item = {
            "query": user_query,
            "result": result,
            "duration": total_duration,
            "steps": steps,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.history.append(history_item)

        # 更新进度
        with tab1:
            progress_bar.progress(80)
            status_text.success("✅ 处理完成！")

        end_time = time.time()
        execution_time = end_time - start_time

        with tab1:
            progress_bar.progress(100)

            st.markdown("#### 📊 执行摘要")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总耗时", f"{execution_time:.2f}秒")
            with col2:
                st.metric("执行步骤", len(steps))
            with col3:
                status = "✅ 成功" if not error else "❌ 失败"
                st.metric("执行状态", status)

            st.markdown("#### 🔄 详细执行步骤")
            for i, step in enumerate(steps):
                step_num = step.get("step", i+1)
                action = step.get("action", "")
                detail = step.get("detail", "")
                timestamp = step.get("timestamp", "")

                if step_num > 0:
                    with st.expander(f"步骤 {step_num}: {action} ⏱️ {timestamp}", expanded=i >= len(steps)-2):
                        st.markdown(f"**动作**: {action}")
                        st.markdown(f"**详情**: {detail}")
                else:
                    with st.expander(f"❌ 出错: {action}", expanded=True):
                        st.markdown(f"**错误**: {detail}")

            with st.expander("📜 原始执行日志"):
                st.json(execution_log)

            st.success(f"🎉 调研完成！总耗时: {execution_time:.2f}秒")

        with tab2:
            if error:
                st.error(f"执行出错: {error}")
                with st.expander("查看错误详情"):
                    import traceback
                    st.code(traceback.format_exc())
            else:
                if final_result:
                    st.markdown(final_result)
                else:
                    st.info("无结果生成")

                reports = get_reports()
                if reports:
                    st.markdown("---")
                    st.markdown("#### 📁 生成的报告文件")
                    for report in reports[:5]:
                        content = load_report_content(report)
                        if content:
                            with st.expander(f"📄 {report}", expanded=False):
                                st.markdown(content[:1000] + "..." if len(content) > 1000 else content)

                # 导出选项
                st.markdown("---")
                st.markdown("#### 📤 导出选项")
                col1, col2 = st.columns(2)
                with col1:
                    if final_result:
                        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Research Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; }} h2 {{ color: #555; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>{final_result}</body>
</html>"""
                        st.download_button(
                            "🌐 导出为HTML",
                            data=html_content.encode("utf-8"),
                            file_name="research_report.html",
                            mime="text/html",
                            use_container_width=True
                        )
                with col2:
                    if final_result:
                        st.download_button(
                            "📄 导出为Markdown",
                            data=final_result.encode("utf-8"),
                            file_name="research_report.md",
                            mime="text/markdown",
                            use_container_width=True
                        )

    except Exception as e:
        with tab1:
            progress_bar.progress(100)
            status_text.error("❌ 执行出错")
            st.error(f"执行出错: {str(e)}")
            import traceback
            with st.expander("查看错误详情"):
                st.code(traceback.format_exc())
        with tab2:
            st.error(f"执行出错: {str(e)}")

elif run_button and not user_query:
    st.warning("⚠️ 请输入研究需求")

# ==================== 页脚 ====================
st.markdown("---")
st.caption("AI Research Assistant · 基于MiniMax API构建 · v2.0")