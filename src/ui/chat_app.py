"""
Clawlize - 对话式工作流 UI (AI增强版)
使用模型生成对话内容
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from datetime import datetime

from src.workflow import Workflow, get_manager, WorkflowStatus, NodeType
from src.nodes import (
    InputCompanyNode,
    GetCompanyInfoNode,
    DownloadReportNode,
    ParsePDFNode,
    SearchNewsNode,
    ConfirmFocusNode,
    GenerateReportNode,
    ReviewReportNode,
    ExportReportNode
)


def create_due_diligence_workflow():
    """创建企业尽职调查工作流"""
    wf = Workflow(
        name="企业尽职调查",
        description="输入公司名称，获取工商信息、年报分析、舆情搜索，生成尽调报告"
    )
    
    wf.add_node(InputCompanyNode())
    wf.add_node(GetCompanyInfoNode())
    wf.add_node(DownloadReportNode())
    wf.add_node(ParsePDFNode())
    wf.add_node(SearchNewsNode())
    wf.add_node(ConfirmFocusNode())
    wf.add_node(GenerateReportNode())
    wf.add_node(ReviewReportNode())
    wf.add_node(ExportReportNode())
    
    return wf


def generate_ai_response(user_input, workflow, current_node):
    """
    生成AI回复
    这里可以接入真实的AI模型（如 OpenAI、Claude 等）
    目前使用规则模板
    """
    node_id = current_node.node_id
    
    # 根据节点生成回复
    if node_id == "input_company":
        return f"好的，正在查询 **{user_input}** 的信息，请稍候..."
    
    elif node_id == "confirm_focus":
        areas = user_input if isinstance(user_input, list) else [user_input]
        return f"收到！您关注的领域是：{', '.join(areas)}"
    
    elif node_id == "review_report":
        return f"好的，您的审核结果是：**{user_input}**"
    
    elif node_id == "get_company_info":
        # 检查是否需要用户补充
        if workflow.context.get("api_status") == "failed":
            company_name = workflow.context.get("company_name", "")
            return (f"抱歉，自动获取 **{company_name}** 的信息失败了。\n\n"
                   f"请提供以下信息：\n"
                   f"- 公司名称\n"
                   f"- 所在行业\n"
                   f"- 注册资本（可选）")
        
        info = workflow.context.get("company_info", {})
        if info:
            name = info.get("company_name", "")
            price = info.get("current_price", "")
            return f"✅ 找到公司信息！\n\n**{name}**\n当前价格: {price}"
        return "正在查询公司信息..."
    
    elif node_id == "download_report":
        if workflow.context.get("download_status") == "failed":
            return ("⚠️ PDF下载失败。\n\n"
                   "请提供：\n"
                   "- 年报PDF文件路径，或\n"
                   "- 直接提供财务数据")
        return "正在下载年报..."
    
    elif node_id == "parse_pdf":
        return "正在解析年报，提取财务指标..."
    
    elif node_id == "search_news":
        return "正在搜索相关舆情..."
    
    elif node_id == "generate_report":
        risk = workflow.context.get("risk_level", "")
        rec = workflow.context.get("recommendation", "")
        return f"📊 报告生成完成！\n\n**风险等级**: {risk}\n**建议**: {rec}"
    
    elif node_id == "export_report":
        path = workflow.context.get("export_path", "")
        return f"✅ 报告已导出到：{path}"
    
    return "处理中..."


def should_request_supplement(workflow, current_node):
    """检查是否需要用户补充信息"""
    node_id = current_node.node_id
    
    supplement_map = {
        "get_company_info": {
            "status_key": "api_status",
            "failed_value": "failed",
            "prompt": "请提供公司名称和行业信息"
        },
        "download_report": {
            "status_key": "download_status", 
            "failed_value": "failed",
            "prompt": "请提供年报PDF文件路径或财务数据"
        },
        "parse_pdf": {
            "status_key": "pdf_parsed",
            "failed_value": False,
            "prompt": "请确认或填写财务数据"
        },
        "search_news": {
            "status_key": "news_search_status",
            "failed_value": "failed",
            "prompt": "请提供您了解的相关舆情信息"
        }
    }
    
    if node_id in supplement_map:
        config = supplement_map[node_id]
        status = workflow.context.get(config["status_key"])
        if status == config["failed_value"]:
            return True, config["prompt"]
    
    return False, ""


def render_chat():
    """渲染聊天界面"""
    st.set_page_config(page_title="Clawlize - 对话式工作流", page_icon="💬", layout="wide")
    
    # 初始化
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "workflow" not in st.session_state:
        st.session_state.workflow = None
    
    if "waiting_supplement" not in st.session_state:
        st.session_state.waiting_supplement = False
    
    # 标题
    st.title("💬 Clawlize - 企业尽职调查")
    st.markdown("---")
    
    # 消息区域
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            render_message(msg["role"], msg["content"])
    
    # 输入区域
    st.markdown("---")
    
    if st.session_state.workflow is None:
        # 开始新工作流
        if st.button("🚀 开始企业尽职调查", type="primary"):
            wf = create_due_diligence_workflow()
            manager = get_manager()
            manager.workflows[wf.workflow_id] = wf
            st.session_state.workflow = wf
            st.session_state.messages.append({
                "role": "assistant",
                "content": "好的，让我们开始企业尽职调查！\n\n请告诉我您想调查的公司名称或股票代码，例如：\n- 贵州茅台\n- 600519"
            })
            st.rerun()
    
    else:
        wf = st.session_state.workflow
        current_node = wf.get_current_node()
        
        if not current_node:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🎉 企业尽职调查已完成！\n\n您可以点击下方按钮开始新的调查。"
            })
            if st.button("🔄 重新开始"):
                st.session_state.workflow = None
                st.session_state.messages = []
                st.rerun()
        else:
            # 检查是否需要补充
            need_supplement, supplement_prompt = should_request_supplement(wf, current_node)
            
            if need_supplement and not st.session_state.waiting_supplement:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ {supplement_prompt}"
                })
                st.session_state.waiting_supplement = True
                st.rerun()
            
            # 用户输入
            user_input = st.text_input("请输入...", key="chat_input", 
                                     placeholder="输入后按回车提交")
            
            if st.button("发送", type="primary") and user_input:
                # 用户消息
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input
                })
                
                # 执行
                manager = get_manager()
                result = manager.execute_step(wf.workflow_id, user_input)
                
                # AI 回复
                response = generate_ai_response(user_input, wf, current_node)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
                # 重置补充标记
                st.session_state.waiting_supplement = False
                st.rerun()
            
            # 自动执行节点
            if current_node.node_type == NodeType.AUTO:
                if not need_supplement:
                    with st.spinner("处理中..."):
                        manager = get_manager()
                        result = manager.execute_step(wf.workflow_id)
                    
                    response = generate_ai_response("", wf, current_node)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    st.rerun()


def render_message(role, content):
    """渲染单条消息"""
    if role == "user":
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end; margin:10px 0;">
            <div style="background:#007AFF; color:white; padding:12px 16px; border-radius:18px 18px 4px 18px; max-width:70%;">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-start; margin:10px 0;">
            <div style="background:#E9E9EB; color:black; padding:12px 16px; border-radius:18px 18px 18px 4px; max-width:70%;">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_chat()
