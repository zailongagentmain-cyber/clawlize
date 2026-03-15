"""
工作流持久化 - 保存和加载工作流
"""
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

from src.workflow import Workflow, WorkflowStatus


class WorkflowStorage:
    """工作流存储"""
    
    def __init__(self, storage_dir: str = "data/workflows"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save(self, workflow: Workflow) -> str:
        """保存工作流"""
        filepath = os.path.join(self.storage_dir, f"{workflow.workflow_id}.json")
        
        data = {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status,
            "current_node_index": workflow.current_node_index,
            "context": workflow.context,
            "nodes": [
                {
                    "node_id": n.node_id,
                    "name": n.name,
                    "node_type": n.node_type.value
                }
                for n in workflow.nodes
            ],
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load(self, workflow_id: str) -> Optional[Workflow]:
        """加载工作流"""
        filepath = os.path.join(self.storage_dir, f"{workflow_id}.json")
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 重建工作流（需要节点定义）
        workflow = Workflow(
            name=data["name"],
            description=data.get("description", ""),
            workflow_id=data["workflow_id"]
        )
        workflow.status = data.get("status", WorkflowStatus.DRAFT)
        workflow.current_node_index = data.get("current_node_index", 0)
        workflow.context = data.get("context", {})
        workflow.created_at = data.get("created_at", datetime.now().isoformat())
        workflow.updated_at = data.get("updated_at", datetime.now().isoformat())
        
        return workflow
    
    def list_workflows(self) -> list:
        """列出所有工作流"""
        workflows = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.storage_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    workflows.append({
                        "workflow_id": data["workflow_id"],
                        "name": data["name"],
                        "status": data.get("status"),
                        "updated_at": data.get("updated_at")
                    })
        
        return sorted(workflows, key=lambda x: x["updated_at"], reverse=True)
    
    def delete(self, workflow_id: str) -> bool:
        """删除工作流"""
        filepath = os.path.join(self.storage_dir, f"{workflow_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False


# 全局存储实例
_storage = None

def get_storage() -> WorkflowStorage:
    """获取存储实例"""
    global _storage
    if _storage is None:
        _storage = WorkflowStorage()
    return _storage
