"""
测试工作流引擎
"""
import sys
sys.path.insert(0, '.')

from src.workflow import Workflow, NodeType, NodeContext
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


def test_workflow_creation():
    """测试工作流创建"""
    wf = Workflow(name="测试工作流", description="测试")
    wf.add_node(InputCompanyNode())
    wf.add_node(GetCompanyInfoNode())
    
    assert len(wf.nodes) == 2
    print("✅ 工作流创建测试通过")


def test_workflow_execution():
    """测试工作流执行"""
    wf = Workflow(name="测试工作流")
    
    # 添加节点
    wf.add_node(InputCompanyNode())
    wf.add_node(GetCompanyInfoNode())
    
    # 步骤1: 用户输入
    result = wf.execute_next("贵州茅台")
    assert result["status"] == "running"
    assert "company_name" in wf.context
    print(f"✅ 步骤1完成: {wf.context.get('company_name')}")
    
    # 步骤2: 自动执行
    result = wf.execute_next()
    assert result["status"] == "completed"  # 因为后面没有用户输入节点了
    assert "industry" in wf.context
    print(f"✅ 步骤2完成: {wf.context.get('industry')}")
    
    print("✅ 工作流执行测试通过")


def test_user_input_node():
    """测试用户输入节点"""
    node = InputCompanyNode()
    context = NodeContext(workflow_id="test", node_id="test")
    context.user_input = "600519"
    
    result = node.execute(context)
    assert result["company_name"] == "600519"
    print("✅ 用户输入节点测试通过")


def test_auto_node():
    """测试自动执行节点"""
    node = GetCompanyInfoNode()
    context = NodeContext(workflow_id="test", node_id="test")
    context.data = {"company_name": "贵州茅台", "company_code": "600519"}
    
    result = node.execute(context)
    assert "industry" in result
    print("✅ 自动执行节点测试通过")


def test_full_workflow():
    """测试完整工作流"""
    wf = Workflow(name="企业尽职调查")
    
    # 添加所有节点
    wf.add_node(InputCompanyNode())
    wf.add_node(GetCompanyInfoNode())
    wf.add_node(DownloadReportNode())
    wf.add_node(ParsePDFNode())
    wf.add_node(SearchNewsNode())
    wf.add_node(ConfirmFocusNode())
    wf.add_node(GenerateReportNode())
    wf.add_node(ReviewReportNode())
    wf.add_node(ExportReportNode())
    
    print(f"工作流节点数: {len(wf.nodes)}")
    
    # 步骤1: 输入公司
    result = wf.execute_next("贵州茅台")
    print(f"步骤1: {result}")
    
    # 步骤2: 获取公司信息 (自动)
    result = wf.execute_next()
    print(f"步骤2: {result}")
    
    # 步骤3-5: 自动执行
    for i in range(3):
        result = wf.execute_next()
        print(f"步骤{i+3}: {result.get('status')}")
    
    # 步骤6: 确认关注领域 (用户输入)
    result = wf.execute_next(["财务风险", "行业前景"])
    print(f"步骤6: {result}")
    
    # 步骤7-9: 自动执行
    for i in range(3):
        result = wf.execute_next()
        print(f"步骤{i+7}: {result.get('status')}")
    
    # 步骤8: 审核 (用户输入)
    result = wf.execute_next("通过")
    print(f"步骤8: {result}")
    
    # 步骤9: 导出
    result = wf.execute_next()
    print(f"步骤9: {result}")
    
    print("✅ 完整工作流测试通过")


if __name__ == "__main__":
    print("开始测试...\n")
    
    test_workflow_creation()
    test_workflow_execution()
    test_user_input_node()
    test_auto_node()
    test_full_workflow()
    
    print("\n🎉 所有测试通过!")
