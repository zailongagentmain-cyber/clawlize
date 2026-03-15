"""
Clawlize - 企业尽职调查工作流 UI (增强版)
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from src.workflow import get_manager, WorkflowStatus, NodeType
from src.nodes import (
    InputCompanyNode,
    GetCompanyInfoNode,
    SupplementCompanyInfoNode,
    DownloadReportNode,
    InputReportNode,
    ParsePDFNode,
    ConfirmFinancialDataNode,
    SearchNewsNode,
    InputNewsNode,
    ConfirmFocusNode,
    GenerateReportNode,
    ReviewReportNode,
    ExportReportNode
)


def create_due_diligence_workflow():
    """创建企业尽职调查工作流"""
    from src.workflow import Workflow
    
    wf = Workflow(
        name="企业尽职调查",
        description="输入公司名称，获取工商信息、年报分析、舆情搜索，生成尽调报告"
    )
    
    # 添加节点 (支持用户补充)
    wf.add_node(InputCompanyNode())            # 1. 输入公司
    wf.add_node(GetCompanyInfoNode())        # 2. 获取工商信息
    #wf.add_node(SupplementCompanyInfoNode()) # 2.1 补充公司信息
    wf.add_node(DownloadReportNode())         # 3. 下载年报
    #wf.add_node(InputReportNode())           # 3.1 上传年报
    wf.add_node(ParsePDFNode())               # 4. 解析PDF
    #wf.add_node(ConfirmFinancialDataNode())  # 4.1 确认财务数据
    wf.add_node(SearchNewsNode())             # 5. 搜索舆情
    #wf.add_node(InputNewsNode())             # 5.1 提供舆情
    wf.add_node(ConfirmFocusNode())           # 6. 确认关注领域
    wf.add_node(GenerateReportNode())         # 7. 生成报告
    wf.add_node(ReviewReportNode())           # 8. 人工审核
    wf.add_node(ExportReportNode())           # 9. 导出报告
    
    return wf


def render_workflow_detail(workflow_id: str):
    """渲染工作流详情"""
    manager = get_manager()
    wf = manager.get_workflow(workflow_id)
    
    if not wf:
        st.error("工作流不存在")
        return
    
    # 侧边栏进度
    render_progress(wf)
    
    # 标题
    st.title(f"🔍 {wf.name}")
    st.markdown(f"**状态**: {wf.status}")
    
    # 当前节点
    current_node = wf.get_current_node()
    
    if not current_node:
        st.success("🎉 工作流已完成!")
        st.json(wf.context)
        
        if st.button("新建工作流", type="primary"):
            new_wf = create_due_diligence_workflow()
            manager.workflows[new_wf.workflow_id] = new_wf
            manager.save_workflow(new_wf.workflow_id)
            st.rerun()
        return
    
    st.header(f"步骤 {wf.current_node_index + 1}: {current_node.name}")
    
    # 检查是否需要用户补充
    need_supplement = False
    if current_node.node_id == "get_company_info":
        # 检查API状态
        api_status = wf.context.get("api_status", "success")
        if api_status == "failed":
            need_supplement = True
            st.warning("⚠️ 自动获取失败，请手动补充信息")
    
    elif current_node.node_id == "download_report":
        download_status = wf.context.get("download_status", "success")
        if download_status == "failed":
            need_supplement = True
            st.warning("⚠️ PDF下载失败，请上传年报或手动输入")
    
    # 渲染节点
    if current_node.node_type == NodeType.USER_INPUT or need_supplement:
        render_user_input_node(current_node, wf)
    else:
        render_auto_node(current_node, wf)
    
    # 显示当前数据
    st.markdown("---")
    st.subheader("📋 当前数据")
    render_context_data(wf.context)


def render_context_data(context):
    """渲染上下文数据"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**基本信息**")
        st.write(f"公司: {context.get('company_name', '-')}")
        st.write(f"代码: {context.get('stock_code', '-')}")
        st.write(f"价格: {context.get('current_price', '-')}")
    
    with col2:
        st.write("**财务数据**")
        revenue = context.get("revenue", 0)
        profit = context.get("profit", 0)
        if revenue:
            st.write(f"营收: {revenue:,.0f}")
        if profit:
            st.write(f"利润: {profit:,.0f}")
        st.write(f"风险: {context.get('risk_level', '-')}")
    
    with col3:
        st.write("**其他**")
        sentiment = context.get("sentiment", {})
        if sentiment:
            st.write(f"舆情: {sentiment.get('sentiment', '-')}")
        st.write(f"建议: {context.get('recommendation', '-')}")


def render_progress(workflow):
    """渲染工作流进度"""
    st.sidebar.header("📊 工作流进度")
    
    progress = workflow.current_node_index / len(workflow.nodes) if workflow.nodes else 0
    st.sidebar.progress(progress)
    st.sidebar.write(f"**{workflow.current_node_index + 1} / {len(workflow.nodes)}**")
    
    node_type_emoji = {
        NodeType.USER_INPUT: "👤",
        NodeType.AUTO: "🤖",
        NodeType.CONFIRM: "✅"
    }
    
    for i, node in enumerate(workflow.nodes):
        if i < workflow.current_node_index:
            icon = "✅"
        elif i == workflow.current_node_index:
            icon = "🔄"
        else:
            icon = "⏳"
        
        type_icon = node_type_emoji.get(node.node_type, "")
        st.sidebar.write(f"{icon} {type_icon} {i+1}. {node.name}")


def render_user_input_node(node, workflow):
    """渲染用户输入节点"""
    user_input = None
    
    if node.node_id == "input_company":
        user_input = st.text_input(
            "请输入公司名称或股票代码", 
            placeholder="如: 贵州茅台 或 600519",
            key="company_input"
        )
    
    elif node.node_id == "supplement_company_info":
        st.info("自动获取失败，请补充以下信息：")
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("公司名称", key="supp_name")
            industry = st.text_input("行业", key="supp_industry")
        with col2:
            capital = st.text_input("注册资本", key="supp_capital")
        user_input = {"company_name": company_name, "industry": industry, "registered_capital": capital}
    
    elif node.node_id == "input_report":
        st.info("请提供年报文件路径或上传年报：")
        user_input = st.text_input("PDF文件路径", placeholder="/path/to/report.pdf", key="report_path")
    
    elif node.node_id == "confirm_financial":
        st.info("请确认或填写财务数据：")
        col1, col2 = st.columns(2)
        with col1:
            revenue = st.number_input("营业收入(元)", value=10000000000.0, key="rev")
            profit = st.number_input("净利润(元)", value=2000000000.0, key="profit")
        with col2:
            assets = st.number_input("总资产(元)", value=50000000000.0, key="assets")
            liability = st.number_input("总负债(元)", value=3000000000.0, key="liability")
        user_input = {"revenue": revenue, "profit": profit, "total_assets": assets, "total_liability": liability}
    
    elif node.node_id == "input_news":
        st.info("请提供舆情信息（可选）：")
        user_input = st.text_area("舆情摘要", placeholder="输入您了解的相关信息...", key="news_input")
    
    elif node.node_id == "confirm_focus":
        options = ["行业前景", "财务风险", "法律风险", "经营状况", "公司治理"]
        user_input = st.multiselect("请选择关注领域", options, default=options[:2], key="focus_input")
    
    elif node.node_id == "review_report":
        st.json(workflow.context.get("summary", {}))
        user_input = st.radio("请审核报告", ["通过", "退回修改"], key="review_input")
    
    if st.button("提交", type="primary", key="submit_btn"):
        if user_input:
            manager = get_manager()
            result = manager.execute_step(workflow.workflow_id, user_input)
            
            if result.get("status") == "error":
                st.error(result.get("message", ""))
            else:
                st.success(result.get("message", ""))
                st.rerun()
        else:
            st.warning("请输入内容")


def render_auto_node(node, workflow):
    """渲染自动执行节点"""
    with st.spinner("正在执行..."):
        manager = get_manager()
        result = manager.execute_step(workflow.workflow_id)
    
    if result.get("status") == "waiting":
        st.warning(result.get("message", ""))
    elif result.get("status") == "running":
        st.success(result.get("message", ""))
        st.rerun()
    elif result.get("status") == "completed":
        st.success("工作流完成!")
        st.rerun()
    else:
        st.error(result.get("message", "执行失败"))


def render_workflow_list():
    """渲染工作流列表"""
    st.title("📋 Clawlize - 工作流管理")
    
    manager = get_manager()
    workflows = manager.list_workflows()
    
    if st.button("➕ 新建工作流", type="primary"):
        new_wf = create_due_diligence_workflow()
        manager.workflows[new_wf.workflow_id] = new_wf
        manager.save_workflow(new_wf.workflow_id)
        st.rerun()
    
    st.markdown("---")
    
    if not workflows:
        st.info("暂无工作流，请新建")
        return
    
    for wf_data in workflows:
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.write(f"**{wf_data['name']}**")
        
        with col2:
            st.write(f"{wf_data.get('status', 'draft')}")
        
        with col3:
            if st.button("打开", key=f"open_{wf_data['workflow_id']}"):
                st.session_state.current_workflow = wf_data['workflow_id']
                st.rerun()
        
        st.divider()


def main():
    st.set_page_config(
        page_title="Clawlize - 企业尽职调查",
        page_icon="🔍",
        layout="wide"
    )
    
    if "current_workflow" not in st.session_state:
        st.session_state.current_workflow = None
    
    with st.sidebar:
        st.title("🔧 Clawlize")
        st.markdown("---")
        
        if st.button("🏠 工作流列表"):
            st.session_state.current_workflow = None
            st.rerun()
    
    if st.session_state.current_workflow:
        render_workflow_detail(st.session_state.current_workflow)
    else:
        render_workflow_list()


if __name__ == "__main__":
    main()
