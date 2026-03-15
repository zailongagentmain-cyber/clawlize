"""
数据获取模块 - 公司信息
"""
import requests
from typing import Dict, Optional


def get_company_info_by_code(stock_code: str) -> Dict:
    """
    根据股票代码获取公司信息
    使用东方财富API
    """
    # 东方财富股票信息API
    url = f"https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "invt": "2",
        "fltt": "2",
        "fields": "f58,f43,f57,f107,f127,f168,f116,f162,f173,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f1001,f1002,f1003,f1004,f1005,f1006,f1007,f1008,f1009,f1010,f1011,f1012,f1013,f1014",
        "secid": f"1.{stock_code}"  # 上海交易所
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get("data"):
            d = data["data"]
            return {
                "company_code": stock_code,
                "company_name": d.get("f58"),  # 股票名称
                "current_price": d.get("f43"),  # 当前价格
                "change_pct": d.get("f170"),  # 涨跌幅
                "turnover": d.get("f168"),  # 成交额
                "volume": d.get("f116"),  # 成交量
                "high": d.get("f162"),  # 最高
                "low": d.get("f163"),  # 最低
                "open": d.get("f43"),  # 开盘价
                "previous_close": d.get("f170"),  # 昨收
            }
    except Exception as e:
        print(f"获取公司信息失败: {e}")
    
    return {}


def search_company(keyword: str) -> list:
    """
    搜索公司
    """
    url = "https://searchapi.eastmoney.com/api/suggest/get"
    params = {
        "input": keyword,
        "type": "14",
        "token": "D43BF722C8E33BDC906FB84D85E326E8",
        "count": 10
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        results = []
        if data.get("Data"):
            for item in data["Data"]:
                results.append({
                    "code": item.get("Code"),
                    "name": item.get("Name"),
                    "source": item.get("Source")
                })
        return results
    except Exception as e:
        print(f"搜索公司失败: {e}")
    
    return []


if __name__ == "__main__":
    # 测试
    print("=== 测试获取公司信息 ===")
    info = get_company_info_by_code("600519")
    print(info)
    
    print("\n=== 测试搜索 ===")
    results = search_company("茅台")
    print(results)
