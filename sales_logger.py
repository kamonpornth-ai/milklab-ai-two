"""MilkLab Sales Logger (S2).

Usage:
    python sales_logger.py --menu "นมหมีฮอกไกโด" --qty 2 --price 65

Reads GOOGLE_SHEETS_CREDENTIALS and TELEGRAM_BOT_TOKEN (or LINE_CHANNEL_TOKEN) from env.
Appends row [timestamp, menu, qty, price, total] to a Google Sheet,
then sends a notification via Telegram or LINE bot.

นักศึกษาต้องเติม TODO ใน 4 จุดด้านล่างใน Session 2 Lab 1.3
"""

import os
import json
import argparse
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import requests

def main():
    # 1. รับ Command-line arguments (--menu, --qty, --price)
    parser = argparse.ArgumentParser(description="Sales Logger")
    parser.add_argument("--menu", type=str, required=True, help="Menu name")
    parser.add_argument("--qty", type=int, required=True, help="Quantity")
    parser.add_argument("--price", type=float, required=True, help="Price per unit")
    args = parser.parse_args()

    total_price = args.qty * args.price
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. ดึงค่า Secrets จาก Environment Variables
    creds_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS") or os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    spreadsheet_id = os.environ.get("SPREADSHEET_ID") or os.environ.get("GOOGLE_SHEET_ID")
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    # 3. Handle case Sheets ไม่ accessible (Lab 1.3 ข้อ 4)
    if not creds_json or not spreadsheet_id:
        print("Error: Sheets credentials or Spreadsheet ID is missing!")
        exit(1)

    try:
        # 4. บันทึกข้อมูลลง Google Sheets (Lab 1.3 ข้อ 2)
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(spreadsheet_id).sheet1
        sheet.append_row([timestamp, args.menu, args.qty, args.price, total_price])
        print(f"Successfully logged sale: {args.menu} x {args.qty} = {total_price}")

    except Exception as e:
        print(f"Error: Sheets ไม่สามารถเข้าถึงได้ - {str(e)}")
        exit(1)

    # 5. ส่ง Notification ผ่าน Bot (Lab 1.3 ข้อ 3)
    if bot_token and chat_id:
        msg = f"🔔 *บันทึกยอดขายใหม่*\n📅 เวลา: {timestamp}\n🍹 เมนู: {args.menu}\n🔢 จำนวน: {args.qty}\n💵 รวม: {total_price:,.2f} บาท"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
        print("Telegram notification sent!")

if __name__ == "__main__":
    main()
