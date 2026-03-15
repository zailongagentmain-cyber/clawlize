"""
工作流引擎 - 节点基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    """节点类型"""
    USER_INPUT = "user_input"      # 用户输入
    AUTO = "auto"                  # 自动执行
    CONFIRM = "confirm"            # 用户确认


class NodeStatus(Enum):
    """节点状态"""
    PENDING = "pending"    # 待执行
    RUNNING = "running"    # 执行中
    WAITING = "waiting"    # 等待用户输入
    COMPLETED = "completed" # 已完成
    FAILED = "failed"      # 失败


@dataclass
class NodeContext:
    """节点执行上下文"""
    workflow_id: str
    node_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    status: NodeStatus = NodeStatus.PENDING
    error: Optional[str] = None
    user_input: Optional[Any] = None


class Node(ABC):
    """节点基类"""
    
    def __init__(self, node_id: str, name: str, node_type: NodeType = NodeType.AUTO):
        self.node_id = node_id
        self.name = name
        self.node_type = node_type
    
    @abstractmethod
    def execute(self, context: NodeContext) -> Dict[str, Any]:
        """执行节点，返回结果数据"""
        pass
    
    @abstractmethod
    def validate_input(self, context: NodeContext) -> bool:
        """验证输入数据"""
        pass
    
    def get_required_inputs(self) -> list:
        """返回需要的输入字段"""
        return []
    
    def __repr__(self):
        return f"<Node {self.node_id}: {self.name}>"
