# TODO - Clawlize

## 项目目标

探索将传统业务改造为 OpenClaw 范式的工作流框架

## MVP: 企业尽职调查工作流

### Phase 1: 基础框架 ✅

- [x] **1.1** 项目初始化
- [x] **1.2** 工作流引擎基础 (Node, Workflow)
- [x] **1.3** 基本 UI 界面

### Phase 2: 核心功能 ✅

- [x] **2.1** 步骤1 - 用户输入公司名称
- [x] **2.2** 步骤2 - 获取工商信息 (真实API)
- [x] **2.3** 步骤3 - 下载年报 PDF
- [x] **2.4** 步骤4 - 解析 PDF 提取指标
- [x] **2.5** 步骤5 - 搜索舆情

### Phase 3: 报告生成 ✅

- [x] **3.1** 步骤6 - 用户确认关注领域
- [x] **3.2** 步骤7 - 生成尽调报告
- [x] **3.3** 步骤8 - 人工审核
- [x] **3.4** 步骤9 - 导出报告

### Phase 4: 框架增强 ✅

- [x] **4.1** 工作流持久化 (WorkflowStorage)
- [x] **4.2** 工作流管理器 (WorkflowManager)
- [x] **4.3** 工作流列表 UI
- [x] **4.4** 增强的详情页面

---

## 已完成项目结构

```
clawlize/
├── README.md
├── TODO.md
├── PRD.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── node.py           # 节点基类
│   │   ├── workflow.py       # 工作流类
│   │   ├── storage.py        # 持久化存储
│   │   └── manager.py        # 工作流管理器
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── data/             # 数据获取
│   │   │   ├── company.py    # 公司信息API
│   │   │   ├── report.py     # 年报PDF
│   │   │   └── news.py       # 舆情搜索
│   │   └── due_diligence.py  # 9个业务节点
│   └── ui/
│       └── app.py            # Streamlit UI
├── data/
│   ├── pdfs/
│   ├── reports/
│   └── workflows/           # 工作流存储
└── tests/
    └── test_workflow.py
```

## 框架能力

1. **工作流引擎**
   - 节点定义 (用户输入/自动执行/确认)
   - 状态管理 (pending/running/waiting/completed/failed)
   - 上下文传递

2. **持久化**
   - 保存工作流到 JSON
   - 加载已存工作流
   - 列表展示

3. **管理器**
   - 创建/获取/删除工作流
   - 执行步骤
   - 进度追踪

## 运行方式

```bash
cd ~/.openclaw/workspace/clawlize

# 安装依赖
pip install -r requirements.txt

# 启动 UI
streamlit run src/ui/app.py
```
