import urllib.request
import json

url = 'http://localhost:8000/api/v1/hollow/posts?page=1&size=10'
headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzMwMDMwMjY2fQ.U7p3U35D3pXj0J2y1X7h8h9h8h8h8h8h8h8h8h8h8'
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
        print("成功:", data)
except urllib.error.HTTPError as e:
    print(f"HTTP错误 {e.code}:")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"请求失败: {e}")