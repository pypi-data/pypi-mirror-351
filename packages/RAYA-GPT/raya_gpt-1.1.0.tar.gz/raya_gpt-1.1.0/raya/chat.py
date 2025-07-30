import requests
import urllib.parse

class RayaGPT:
    def __init__(self, base_url="https://raya-gpt.abas-server.ir/chat"):
        self.base_url = base_url

    def ask(self, user: str, message: str) -> str:
        user_encoded = urllib.parse.quote(user)
        message_encoded = urllib.parse.quote(message)
        url = f"{self.base_url}?user={user_encoded}&message={message_encoded}"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()  # انتظار داریم پاسخ به صورت JSON باشد
            return data.get("reply", "❌ پاسخ نامشخص دریافت شد.")
        except requests.exceptions.RequestException as e:
            return f"❌ خطا در ارتباط با سرور: {e}"
        except ValueError:
            return "❌ خطا در خواندن پاسخ JSON از سرور."