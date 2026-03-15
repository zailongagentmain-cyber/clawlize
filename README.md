# Clawlize

> 业务 OpenClaw 化框架 - 探索将传统业务改造为 OpenClaw 范式的工作流框架

## MVP: 企业尽职调查工作流

```
👤 输入公司名称 → 🤖 获取工商信息 → 🤖 下载年报 PDF → 🤖 解析 PDF → 🤖 搜索舆情 → 👤 确认关注领域 → 🤖 生成报告 → 👤 人工审核 → 🤖 导出报告
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动
streamlit run src/ui/app.py
```

## 项目结构

```
clawlize/
├── src/
│   ├── workflow/     # 工作流引擎
│   ├── nodes/       # 节点实现
│   └── ui/          # Streamlit 页面
├── data/
│   ├── db.sqlite    # 数据存储
│   └── pdfs/        # PDF 文件
├── templates/       # 报告模板
├── tests/           # 测试
└── requirements.txt
```
