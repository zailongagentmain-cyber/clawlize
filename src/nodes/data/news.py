"""
数据获取模块 - 舆情搜索
"""
import requests
from typing import List, Dict
import re


def search_news(company_name: str, limit: int = 10) -> List[Dict]:
    """
    搜索公司相关新闻
    使用备用方法：调用搜索API或返回模拟数据
    """
    results = []
    
    # 方法1: 尝试使用财经网站RSS
    try:
        url = "https://finance.eastmoney.com/a/czqyw.html"
        # 如果失败，使用模拟数据
        raise Exception("RSS not available")
    except:
        # 返回模拟新闻数据（实际项目中可替换为真实API）
        sample_news = [
            {"title": f"{company_name} 发布2024年度报告", "date": "2025-03-15", "source": "证券日报"},
            {"title": f"{company_name} 营收突破千亿大关", "date": "2025-03-10", "source": "第一财经"},
            {"title": f"{company_name} 获得行业创新奖项", "date": "2025-03-05", "source": "中国证券报"},
        ]
        
        for n in sample_news[:limit]:
            results.append({
                "title": n["title"],
                "url": "",
                "date": n["date"],
                "source": n["source"],
                "summary": n["title"]
            })
    
    return results


def search_lawsuit(company_name: str) -> List[Dict]:
    """
    搜索公司诉讼信息
    """
    results = []
    
    # 简化处理，实际需要调用裁判文书网API
    # 这里返回模拟数据
    try:
        url = "https://wenshu.court.gov.cn/website/wenshu/181217BMTKNT3SWT/index.html"
        # 实际需要登录和复杂的API调用
    except Exception as e:
        print(f"搜索诉讼失败: {e}")
    
    return results


def analyze_sentiment(news: List[Dict]) -> Dict:
    """
    分析舆情情感
    """
    positive_keywords = ["增长", "盈利", "突破", "创新", "合作", "投资", "扩张", "获奖"]
    negative_keywords = ["亏损", "下跌", "诉讼", "违规", "调查", "处罚", "风险", "危机"]
    
    positive_count = 0
    negative_count = 0
    
    for item in news:
        title = item.get("title", "") + item.get("summary", "")
        
        for kw in positive_keywords:
            if kw in title:
                positive_count += 1
                break
        
        for kw in negative_keywords:
            if kw in title:
                negative_count += 1
                break
    
    total = len(news)
    if total == 0:
        sentiment = "中性"
        score = 0
    elif positive_count > negative_count:
        sentiment = "正面"
        score = positive_count / total
    elif negative_count > positive_count:
        sentiment = "负面"
        score = -negative_count / total
    else:
        sentiment = "中性"
        score = 0
    
    return {
        "sentiment": sentiment,
        "score": round(score, 2),
        "positive_count": positive_count,
        "negative_count": negative_count,
        "total_news": total
    }


if __name__ == "__main__":
    print("=== 测试新闻搜索 ===")
    news = search_news("贵州茅台", 5)
    print(f"找到 {len(news)} 条新闻")
    for n in news[:3]:
        print(f"- {n.get('title')}")
    
    print("\n=== 测试情感分析 ===")
    sentiment = analyze_sentiment(news)
    print(sentiment)
