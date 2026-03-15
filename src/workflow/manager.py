"""
工作流管理器 - 管理多个工作流实例
"""
from typing import Dict, List, Optional
import uuid

from src.workflow import Workflow, WorkflowStatus
from src.workflow.storage import get_storage


class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.storage = get_storage()
    
    def create_workflow(self, name: str, description: str = "") -> Workflow:
        """创建新工作流"""
        wf = Workflow(name=name, description=description)
        self.workflows[wf.workflow_id] = wf
        return wf
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """获取工作流"""
        if workflow_id in self.workflows:
            return self.workflows[workflow_id]
        
        # 尝试从存储加载
        wf = self.storage.load(workflow_id)
        if wf:
            self.workflows[workflow_id] = wf
            return wf
        
        return None
    
    def list_workflows(self) -> List[Dict]:
        """列出所有工作流"""
        result = []
        
        # 内存中的工作流
        for wf in self.workflows.values():
            result.append(wf.to_dict())
        
        # 存储中的工作流
        for data in self.storage.list_workflows():
            if data["workflow_id"] not in self.workflows:
                result.append(data)
        
        return sorted(result, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    def save_workflow(self, workflow_id: str) -> bool:
        """保存工作流"""
        wf = self.get_workflow(workflow_id)
        if wf:
            self.storage.save(wf)
            return True
        return False
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """删除工作流"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
        
        return self.storage.delete(workflow_id)
    
    def execute_step(self, workflow_id: str, user_input: any = None) -> Dict:
        """执行工作流下一步"""
        wf = self.get_workflow(workflow_id)
        if not wf:
            return {"status": "error", "message": "工作流不存在"}
        
        result = wf.execute_next(user_input)
        
        # 自动保存
        self.save_workflow(workflow_id)
        
        return result
    
    def get_progress(self, workflow_id: str) -> Optional[Dict]:
        """获取工作流进度"""
        wf = self.get_workflow(workflow_id)
        if not wf:
            return None
        
        return {
            "workflow_id": wf.workflow_id,
            "name": wf.name,
            "status": wf.status,
            "current_node": wf.get_current_node().name if wf.get_current_node() else None,
            "current_index": wf.current_node_index,
            "total_nodes": len(wf.nodes),
            "progress": f"{wf.current_node_index}/{len(wf.nodes)}",
            "progress_pct": int(wf.current_node_index / len(wf.nodes) * 100) if wf.nodes else 0
        }


# 全局管理器
_manager = None

def get_manager() -> WorkflowManager:
    """获取管理器实例"""
    global _manager
    if _manager is None:
        _manager = WorkflowManager()
    return _manager
