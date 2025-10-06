import requests
import json

def test_create_companion():
    url = "http://localhost:8000/api/companions/"
    data = {
        "user_id": "test_user_123",
        "name": "测试伙伴",
        "avatar_id": "avatar_1",
        "personality_archetype": "friend"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 伙伴创建成功!")
            return response.json()
        else:
            print("❌ 伙伴创建失败!")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

if __name__ == "__main__":
    test_create_companion()
