"""
Clawlize - 对话式工作流 UI
模仿 OpenClaw 的 Web Chat 方式
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
    
    wf.add_node(InputCompanyNode())        # 1. 输入公司
    wf.add_node(GetCompanyInfoNode())      # 2. 获取工商信息
    wf.add_node(DownloadReportNode())      # 3. 下载年报
    wf.add_node(ParsePDFNode())            # 4. 解析PDF
    wf.add_node(SearchNewsNode())          # 5. 搜索舆情
    wf.add_node(ConfirmFocusNode())        # 6. 确认关注领域
    wf.add_node(GenerateReportNode())      # 7. 生成报告
    wf.add_node(ReviewReportNode())        # 8. 人工审核
    wf.add_node(ExportReportNode())        # 9. 导出报告
    
    return wf


def render_chat_message(role, content, timestamp=None):
    """渲染聊天消息"""
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


def render_chat():
    """渲染聊天界面"""
    st.set_page_config(page_title="Clawlize - 对话式工作流", page_icon="💬", layout="wide")
    
    # 初始化 session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "workflow" not in st.session_state:
        st.session_state.workflow = None
    
    # 标题
    st.title("💬 Clawlize - 企业尽职调查")
    st.markdown("---")
    
    # 聊天消息区域
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            render_chat_message(msg["role"], msg["content"], msg.get("timestamp"))
    
    # 输入区域
    st.markdown("---")
    
    # 处理用户输入
    if st.session_state.workflow is None:
        # 需要创建新工作流
        if st.button("🚀 开始企业尽职调查", type="primary"):
            # 创建工作流
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
        # 工作流进行中
        wf = st.session_state.workflow
        current_node = wf.get_current_node()
        
        if not current_node:
            # 工作流完成
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "🎉 企业尽职调查已完成！\n\n您可以查看右侧的详细数据，或点击下方按钮开始新的调查。"
            })
            
            if st.button("🔄 重新开始"):
                st.session_state.workflow = None
                st.session_state.messages = []
                st.rerun()
        
        else:
            # 显示当前步骤信息
            step_info = f"📍 当前步骤 {wf.current_node_index + 1}/{len(wf.nodes)}: {current_node.name}"
            st.markdown(f"**{step_info}**")
            
            # 根据节点类型处理
            if current_node.node_type == NodeType.USER_INPUT:
                handle_user_input_node(current_node, wf)
            else:
                handle_auto_node(current_node, wf)


def handle_user_input_node(node, wf):
    """处理用户输入节点"""
    user_input = st.text_input("请输入...", key="chat_input", placeholder="输入后按回车提交")
    
    if st.button("发送", type="primary") or (user_input and st.session_state.get("input_submitted")):
        if user_input:
            # 添加用户消息
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # 执行节点
            manager = get_manager()
            result = manager.execute_step(wf.workflow_id, user_input)
            
            # 添加助手响应
            if node.node_id == "input_company":
                response = f"收到！正在查询 {user_input} 的信息..."
            elif node.node_id == "confirm_focus":
                response = f"好的，您关注领域是：{', '.join(user_input if isinstance(user_input, list) else [user_input])}"
            elif node.node_id == "review_report":
                response = f"收到审核结果：{user_input}"
            else:
                response = f"收到您的输入：{user_input}"
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
            
            st.rerun()


def handle_auto_node(node, wf):
    """处理自动执行节点"""
    # 自动执行
    with st.spinner("正在处理..."):
        manager = get_manager()
        result = manager.execute_step(wf.workflow_id)
    
    # 添加系统消息
    messages_map = {
        "get_company_info": "🔍 正在查询公司信息...",
        "download_report": "📥 正在下载年报...",
        "parse_pdf": "📄 正在解析年报...",
        "search_news": "📰 正在搜索舆情...",
        "generate_report": "📝 正在生成报告...",
        "export_report": "💾 正在导出报告..."
    }
    
    msg = messages_map.get(node.node_id, f"正在执行: {node.name}")
    st.session_state.messages.append({
        "role": "assistant",
        "content": msg
    })
    
    # 显示结果
    if node.node_id == "get_company_info":
        info = wf.context.get("company_info", {})
        if info:
            name = info.get("company_name", "")
            price = info.get("current_price", "")
            response = f"✅ 找到公司信息！\n\n**{name}**\n当前价格: {price}"
        else:
            response = "⚠️ 未能自动获取公司信息，请手动补充"
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    elif node.node_id == "generate_report":
        risk = wf.context.get("risk_level", "")
        rec = wf.context.get("recommendation", "")
        response = f"📊 报告生成完成！\n\n**风险等级**: {risk}\n**建议**: {rec}"
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()


if __name__ == "__main__":
    render_chat()
