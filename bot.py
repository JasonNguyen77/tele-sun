import time
import requests
from collections import deque

# Cấu hình bot
TOKEN = "7451739544:AAEAog4UiF0M2P-v1sOIbL8IyAAhAeKtIoM"
CHAT_IDS = ["6254591457"]
API_URL = "https://dudoanteat-production.up.railway.app/prediction"
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

last_sent_round = None
history = deque(maxlen=10)  # Lưu 10 phiên gần nhất


def get_prediction():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("❌ Lỗi API:", e)
    return None


def build_message(data):
    try:
        current = data.get("current_round")
        last = data.get("last_result")
        prediction = data.get("prediction")
        verdict = data.get("verdict")

        if not current or not last or not prediction or not verdict:
            return None, None

        result_emoji = "✅" if last["ket_qua"] == "Tài" else "🚫"
        pred_emoji = "💵" if prediction == "Tài" else "🇻🇳"
        verdict_emoji = "✅ Đúng" if verdict == "Đúng" else "🚫 Sai"

        # Lưu vào history
        history.append({
            "phien": current["phien"],
            "verdict": verdict
        })

        # Tính toán nếu đủ 10 phiên
        thong_ke_text = ""
        if len(history) == 10:
            dung = sum(1 for i in history if i["verdict"] == "Đúng")
            sai = 10 - dung
            min_round = history[0]["phien"]
            max_round = history[-1]["phien"]
            thong_ke_text = f"\n📈 <b>Thống kê 10 phiên:</b>\nPhiên <code>#{min_round}</code> - <code>#{max_round}</code>\n✅Đúng : {dung}    🚫Sai : {sai}"

        message = f"""
🤖 <b>Bot Sunwin By Jason Nguyên</b>

📢 <b>Kết quả phiên trước</b>
🔢 Phiên: <code>#{last['phien']}</code>
🎲 Kết quả: {result_emoji} <b>{last['ket_qua']}</b>

🔮 <b>Dự đoán phiên tiếp theo</b>
🔢 Phiên: <code>#{current['phien']}</code>
📈 Dự đoán: {pred_emoji} <b>{prediction}</b>

📊 <b>Đánh giá</b>
✔️ Phiên #{current['phien']} → <b>{verdict_emoji}</b>
------------------------------{thong_ke_text}
"""
        return message.strip(), current["phien"]

    except Exception as e:
        print("❌ Lỗi build_message:", e)
        return None, None


def send_message(chat_id, message):
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(TELEGRAM_URL, data=payload)
        print(f"✅ Đã gửi đến {chat_id}")
    except Exception as e:
        print("❌ Lỗi gửi:", e)


def main():
    global last_sent_round
    print("🚀 Bot Sunwin đang chạy...")
    while True:
        data = get_prediction()
        if data:
            message, current_round = build_message(data)
            if message and current_round and current_round != last_sent_round:
                for chat_id in CHAT_IDS:
                    send_message(chat_id, message)
                last_sent_round = current_round
        else:
            print("⚠️ Không lấy được dữ liệu từ API")
        time.sleep(5)


if __name__ == "__main__":
    main()
