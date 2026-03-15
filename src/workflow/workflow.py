"""
工作流引擎 - 工作流类
"""
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from .node import Node, NodeContext, NodeStatus, NodeType


class WorkflowStatus:
    """工作流状态"""
    DRAFT = "draft"          # 草稿
    RUNNING = "running"      # 运行中
    WAITING = "waiting"      # 等待用户输入
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败


@dataclass
class Workflow:
    """工作流"""
    name: str
    description: str = ""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nodes: List[Node] = field(default_factory=list)
    current_node_index: int = 0
    status: str = WorkflowStatus.DRAFT
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_node(self, node: Node) -> None:
        """添加节点"""
        self.nodes.append(node)
    
    def get_current_node(self) -> Optional[Node]:
        """获取当前节点"""
        if 0 <= self.current_node_index < len(self.nodes):
            return self.nodes[self.current_node_index]
        return None
    
    def get_next_node(self) -> Optional[Node]:
        """获取下一个节点"""
        if self.current_node_index + 1 < len(self.nodes):
            return self.nodes[self.current_node_index + 1]
        return None
    
    def execute_next(self, user_input: Any = None) -> Dict[str, Any]:
        """执行下一个节点"""
        node = self.get_current_node()
        if not node:
            return {"status": "completed", "message": "工作流已完成"}
        
        # 创建上下文
        context = NodeContext(
            workflow_id=self.workflow_id,
            node_id=node.node_id,
            data=self.context.copy()
        )
        
        # 如果是用户输入节点，设置用户输入
        if user_input is not None:
            context.user_input = user_input
            self.context[node.node_id + "_input"] = user_input
        
        # 验证输入
        if not node.validate_input(context):
            return {"status": "failed", "message": "输入验证失败"}
        
        # 执行节点
        try:
            result = node.execute(context)
            self.context.update(result)
            self.context[node.node_id + "_result"] = result
            
            # 更新状态
            self.current_node_index += 1
            self.updated_at = datetime.now().isoformat()
            
            # 检查下一个节点类型
            next_node = self.get_current_node()
            if next_node and next_node.node_type == NodeType.USER_INPUT:
                self.status = WorkflowStatus.WAITING
                return {
                    "status": "waiting",
                    "message": f"等待用户输入: {next_node.name}",
                    "node_id": next_node.node_id,
                    "node_name": next_node.name
                }
            
            if self.current_node_index >= len(self.nodes):
                self.status = WorkflowStatus.COMPLETED
                return {"status": "completed", "message": "工作流已完成"}
            
            return {"status": "running", "message": f"完成节点: {node.name}"}
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            return {"status": "failed", "message": str(e)}
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "current_node": self.get_current_node().name if self.get_current_node() else None,
            "progress": f"{self.current_node_index}/{len(self.nodes)}",
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def __repr__(self):
        return f"<Workflow {self.name} ({self.status})>"
