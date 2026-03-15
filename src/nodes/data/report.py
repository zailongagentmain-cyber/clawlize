"""
数据获取模块 - 年报 PDF
"""
import os
import requests
from typing import Optional, Dict
import pdfplumber
import re


PDF_DIR = "data/pdfs"


def get_annual_report_url(stock_code: str, year: int = 2024) -> Optional[str]:
    """
    获取年报PDF下载链接
    使用巨潮资讯网
    """
    # 巨潮年报披露
    url = "http://disclosure.cninfo.com.cn/finalpage/LoadNewestAnnouncementList.do"
    params = {
        "stockCode": stock_code,
        "category": "announcement",
        "page": 1,
        "pageSize": 30,
        "date": str(year)
    }
    
    try:
        resp = requests.post(url, data=params, timeout=30)
        # 这里简化处理，实际需要解析HTML
        # 返回示例URL
        return f"http://static.cninfo.com.cn/finalpage/{year}-12-31/{stock_code}_annual_report.pdf"
    except Exception as e:
        print(f"获取年报URL失败: {e}")
    
    return None


def download_annual_report(stock_code: str, year: int = 2024) -> Optional[str]:
    """
    下载年报PDF
    """
    os.makedirs(PDF_DIR, exist_ok=True)
    
    # 尝试从东方财富获取年报PDF
    # 东方财富年报
    url = f"https://data.eastmoney.com/report/{year}.html"
    
    # 保存路径
    save_path = os.path.join(PDF_DIR, f"{stock_code}_{year}_report.pdf")
    
    # 如果已存在直接返回
    if os.path.exists(save_path):
        return save_path
    
    try:
        # 这里简化处理，实际需要从正确的URL下载
        # 暂时返回模拟路径
        return save_path
    except Exception as e:
        print(f"下载失败: {e}")
    
    return None


def parse_annual_report(pdf_path: str) -> Dict:
    """
    解析年报PDF，提取关键财务指标
    """
    result = {
        "revenue": None,           # 营业收入
        "profit": None,           # 净利润
        "total_assets": None,     # 总资产
        "total_liability": None,  # 总负债
        "cash_flow": None,        # 经营活动现金流
        "equity": None,           # 所有者权益
        "eps": None,              # 每股收益
        "roe": None,              # 净资产收益率
    }
    
    if not os.path.exists(pdf_path):
        return result
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # 提取所有文本
            text = ""
            for page in pdf.pages[:10]:  # 只看前10页
                text += page.extract_text() or ""
            
            # 提取关键指标
            # 营业收入
            patterns = [
                r'营业收入[：:\s]*([\d,]+(?:\.\d+)?)\s*元',
                r'营业总收入[：:\s]*([\d,]+(?:\.\d+)?)\s*元',
            ]
            for p in patterns:
                match = re.search(p, text)
                if match:
                    result["revenue"] = float(match.group(1).replace(",", ""))
                    break
            
            # 净利润
            patterns = [
                r'净利润[：:\s]*([\d,]+(?:\.\d+)?)\s*元',
                r'归属于母公司所有者的净利润[：:\s]*([\d,]+(?:\.\d+)?)\s*元',
            ]
            for p in patterns:
                match = re.search(p, text)
                if match:
                    result["profit"] = float(match.group(1).replace(",", ""))
                    break
            
            # 总资产
            match = re.search(r'资产总计[：:\s]*([\d,]+(?:\.\d+)?)\s*元', text)
            if match:
                result["total_assets"] = float(match.group(1).replace(",", ""))
            
            # 总负债
            match = re.search(r'负债合计[：:\s]*([\d,]+(?:\.\d+)?)\s*元', text)
            if match:
                result["total_liability"] = float(match.group(1).replace(",", ""))
            
            # 现金流
            match = re.search(r'经营活动产生的现金流量净额[：:\s]*([\d,]+(?:\.\d+)?)\s*元', text)
            if match:
                result["cash_flow"] = float(match.group(1).replace(",", ""))
            
            # 每股收益
            match = re.search(r'基本每股收益[：:\s]*([\d,]+(?:\.\d+)?)\s*元', text)
            if match:
                result["eps"] = float(match.group(1).replace(",", ""))
            
            # 净资产收益率
            match = re.search(r'加权平均净资产收益率[：:\s]*([\d,]+(?:\.\d+)?)%', text)
            if match:
                result["roe"] = float(match.group(1))
                
    except Exception as e:
        print(f"解析PDF失败: {e}")
    
    return result


if __name__ == "__main__":
    # 测试
    print("=== 测试解析 ===")
    # 需要有真实PDF才能测试
    result = parse_annual_report("dummy.pdf")
    print(result)
