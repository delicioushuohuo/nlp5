import streamlit as st
import asyncio
import time
import os
import json

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide"
)

st.title("AI Research Assistant")
st.subheader("基于云端API的Agent工具系统")

# 用户输入
user_query = st.text_input(
    "请输入您的研究需求:",
    placeholder="例如：帮我调研2026年关于DPO算法的最新进展"
)

if st.button("开始调研"):
    if user_query:
        # 创建标签页用于展示不同内容
        tab1, tab2 = st.tabs(["🔍 执行过程", "📄 最终报告"])
        
        with tab1:
            # 执行过程展示容器
            process_container = st.container()
            with process_container:
                st.info("🚀 正在启动Agent工作流...")
                
                # 创建步骤展示区域
                steps_placeholder = st.empty()
                steps_html = """
                <div style="background-color: #f0f2f6; border-radius: 10px; padding: 20px; margin: 10px 0;">
                    <h4 style="color: #1f77b4; margin-bottom: 15px;">📋 Agent思考链路 (Chain-of-Thought)</h4>
                """
                steps_placeholder.markdown(steps_html, unsafe_allow_html=True)
                
                # 步骤容器
                steps_container = st.container()
        
        # 运行智能体
        start_time = time.time()
        
        try:
            from agent_system.workflows.agent_workflow import run_agent
            
            # 执行Agent
            result = run_agent(user_query)
            
            # 解析执行日志
            execution_log = result.get("log", {})
            steps = execution_log.get("steps", [])
            total_duration = execution_log.get("total_duration", 0)
            
            with tab1:
                # 显示完整执行日志
                st.markdown("### 📊 执行摘要")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总耗时", f"{total_duration:.2f}秒")
                with col2:
                    st.metric("执行步骤", len(steps))
                with col3:
                    status = "✅ 成功" if not execution_log.get("error") else "❌ 失败"
                    st.metric("执行状态", status)
                
                # 展示执行步骤
                st.markdown("### 🔄 详细执行步骤")
                
                for i, step in enumerate(steps):
                    step_num = step.get("step", i+1)
                    action = step.get("action", "")
                    detail = step.get("detail", "")
                    timestamp = step.get("timestamp", "")
                    
                    if step_num > 0:
                        with st.expander(f"步骤 {step_num}: {action} ⏱️ {timestamp}", expanded=True):
                            st.markdown(f"**动作**: {action}")
                            st.markdown(f"**详情**: {detail}")
                            
                            # 如果有工具调用信息
                            if "tool" in step:
                                tool_info = step["tool"]
                                st.markdown(f"**调用工具**: {tool_info.get('name', 'N/A')}")
                                st.markdown(f"**参数**: {json.dumps(tool_info.get('parameters', {}), ensure_ascii=False)}")
                                st.markdown(f"**耗时**: {tool_info.get('duration', 'N/A')}秒")
                    else:
                        with st.expander(f"❌ 出错: {action}", expanded=True):
                            st.markdown(f"**错误**: {detail}")
                
                # 显示原始日志JSON（可选）
                with st.expander("📜 原始执行日志"):
                    st.json(execution_log)
            
            with tab2:
                # 显示最终结果
                if execution_log.get("error"):
                    st.error(f"执行出错: {execution_log['error']}")
                else:
                    final_result = execution_log.get("final_result", "无结果")
                    st.markdown(final_result)
                    
                    # 显示报告文件
                    reports_dir = os.path.join(os.path.dirname(__file__), "agent_system", "reports")
                    if os.path.exists(reports_dir):
                        report_files = sorted([f for f in os.listdir(reports_dir) if f.endswith(".md")], 
                                            key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), 
                                            reverse=True)
                        if report_files:
                            st.markdown("---")
                            st.markdown("### 📁 生成的报告文件")
                            for report_file in report_files[:5]:
                                report_path = os.path.join(reports_dir, report_file)
                                st.markdown(f"- [{report_file}](file://{report_path})")
            
            # 总体耗时
            end_time = time.time()
            execution_time = end_time - start_time
            
            with tab1:
                st.success(f"🎉 调研完成！总耗时: {execution_time:.2f}秒")
                        
        except Exception as e:
            with tab1:
                st.error(f"执行出错: {str(e)}")
                import traceback
                with st.expander("查看错误详情"):
                    st.code(traceback.format_exc())
    else:
        st.warning("请输入调研需求")

# 项目说明
st.sidebar.title("项目说明")
st.sidebar.markdown("""
**AI Research Assistant** 是一个基于云端API的Agent工具系统，能够：

1. **自主规划**：根据用户需求，自动规划调研步骤
2. **工具调用**：调用Arxiv搜索、网页抓取等工具获取信息
3. **报告生成**：将收集到的信息整合成结构化报告
4. **过程透明**：展示智能体的思考链路和执行过程

**支持的工具**：
- Arxiv论文检索：获取最新的学术论文
- 网页抓取：提取网页正文内容
- 报告生成：生成Markdown格式的报告

**技术特性**：
- 异步并发请求加速多文献处理
- API限流与重试机制
- 长文本上下文截断处理

**使用示例**：
- "帮我调研2026年关于DPO算法的最新进展"
- "收集最近关于大语言模型对齐技术的研究"
- "调研多模态大模型的最新应用"
""")
