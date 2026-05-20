import requests
import json
def fetch_data(url: str) -> dict:
    try:
        response = requests.get(url, timeout=5)
    except requests.Timeout:
        return None
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {url}: {response.status_code}")
        # 如果想让程序直接继续运行，可以return None
    try:
        data = response.json()
    except json.JSONDecodeError:
        return None
    return data
    # 你来填