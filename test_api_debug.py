import urllib.request
import json

# 测试基础健康检查
print("=== 测试健康检查 ===")
try:
    with urllib.request.urlopen('http://localhost:8000/health') as response:
        print("健康检查成功:", response.read().decode('utf-8'))
except Exception as e:
    print("健康检查失败:", e)

# 测试认证接口
print("\n=== 测试登录 ===")
login_data = json.dumps({"student_id": "2024001", "password": "123456"}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("登录成功:", data)
        token = data.get('access_token')
        
        # 使用获取的token测试树洞列表
        print("\n=== 测试树洞列表 ===")
        req = urllib.request.Request(
            'http://localhost:8000/api/v1/hollow/posts?page=1&size=10',
            headers={'Authorization': f'Bearer {token}'}
        )
        try:
            with urllib.request.urlopen(req) as response:
                print("树洞列表成功:", response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"树洞列表HTTP错误 {e.code}:")
            print(e.read().decode('utf-8'))
        except Exception as e:
            print("树洞列表请求失败:", e)
except urllib.error.HTTPError as e:
    print(f"登录HTTP错误 {e.code}:")
    print(e.read().decode('utf-8'))
except Exception as e:
    print("登录请求失败:", e)