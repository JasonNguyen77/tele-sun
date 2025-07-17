import requests
import time
from telegram import Bot
from telegram.error import TelegramError
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# === Cấu hình bot ===
TOKEN = '7451739544:AAEAog4UiF0M2P-v1sOIbL8IyAAhAeKtIoM'
GROUP_ID = '6254591457'
bot = Bot(token=TOKEN)

# === Khởi tạo bộ đệm lịch sử ===
latest_round = None
history = []

def build_message(data):
    current = data.get('current')
    previous = data.get('previous')
    stats = data.get('statistics')

    if not current or not previous:
        return None

    msg = "🤖 <b>Bot Sunwin By Jason Nguyên</b>\n\n"
    msg += f"🎯 <b>Phiên #{previous['phien']}</b>\n"
    msg += f"Kết quả: {'✅Tài' if previous['ket_qua'] == 'Tài' else '🚫Xỉu'}\n\n"
    msg += f"🧠 <b>Phiên #{current['phien']}</b>\n"
    msg += f"Dự đoán: {'💵Tài' if current['du_doan'] == 'Tài' else '🇻🇳Xỉu'}\n"
    msg += "--------Hết--------\n"

    if stats and len(stats) >= 10:
        total = len(stats)
        correct = sum(1 for s in stats if s['ket_qua'] == s['du_doan'])
        wrong = total - correct
        start_round = stats[0]['phien']
        end_round = stats[-1]['phien']
        msg += f"\n📊 Phiên #{start_round} - #{end_round}\n✅Đúng: {correct}    🚫Sai: {wrong}"

    return msg

def main():
    global latest_round

    print("🚀 Bot Sunwin đang chạy...")
    while True:
        try:
            res = requests.get("https://dudoanteat-production.up.railway.app/prediction")
            if res.status_code == 200:
                data = res.json()
                current = data.get('current')
                if current:
                    round_id = current.get('phien')
                    if round_id != latest_round:
                        latest_round = round_id
                        message = build_message(data)
                        if message:
                            bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="HTML")
        except TelegramError as te:
            print(f"Telegram Error: {te}")
        except Exception as e:
            print(f"Lỗi: {e}")
        time.sleep(5)

# === Fake Web Server để giữ bot sống trên Render ===
def run_http_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot Sunwin dang chay")

    server = HTTPServer(("", 10000), Handler)
    server.serve_forever()

# === Chạy bot và server song song ===
threading.Thread(target=run_http_server).start()
main()
