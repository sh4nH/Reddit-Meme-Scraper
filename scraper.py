from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import mysql.connector
import datetime
import csv
import telebot
import os
import praw
import threading

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'shanushan1234',
    'database': 'memes_db'
}

# telegram bot Token
TELEGRAM_BOT_TOKEN = '7586741604:AAGoZlNFbnI8bFnk_9InTtT9YeVqk4Z2IbI'
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# reddit API Config
reddit = praw.Reddit(
    client_id="",
    client_secret="",
    user_agent="meme-scraper"
)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            url TEXT,
            votes INT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def scrape_reddit():
    posts = []
    for submission in reddit.subreddit("memes").top(time_filter="day", limit=20):
        posts.append({
            "title": submission.title,
            "url": submission.url,
            "votes": submission.score
        })
    return posts

def store_data(posts):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memes")
    cursor.execute("ALTER TABLE memes AUTO_INCREMENT = 1")
    for post in posts:
        cursor.execute(
            "INSERT INTO memes (title, url, votes, timestamp) VALUES (%s, %s, %s, %s)",
            (post['title'], post['url'], post['votes'], datetime.datetime.now())
        )
    conn.commit()
    conn.close()

# API Endpoint to Fetch Memes
@app.route("/api/memes", methods=["GET"])
def get_memes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM memes ORDER BY votes DESC LIMIT 20")
    memes = cursor.fetchall()
    conn.close()
    return jsonify(memes)

def generate_report():
    filename = "top_memes.csv"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, url, votes FROM memes ORDER BY votes DESC LIMIT 20")
    memes = cursor.fetchall()
    conn.close()
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "URL", "Votes"])
        writer.writerows(memes)
    print(f"csv file has been created successfully!")
    
    return filename

# use threading to make sure the bot runs concurrently with Flask service
def run_bot():
    bot.polling(none_stop=True)

@bot.message_handler(commands=['get_report'])
def send_report(message):
    file_path = generate_report()
    user_chat_id = message.chat.id
    with open(file_path, "rb") as file:
        bot.send_document(user_chat_id, file)
    os.remove(file_path)

if __name__ == "__main__":
    create_table()
    scraped_data = scrape_reddit()
    store_data(scraped_data)
    generate_report()
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    app.run(debug=True)