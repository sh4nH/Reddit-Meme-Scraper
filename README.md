# Reddit Meme Scraper with Telegram Bot

This project is a Python-based web scraping service that collects the top 20 trending memes from the `/r/memes` subreddit on Reddit, stores them in a MySQL database, and allows users to retrieve and share the top memes via a Telegram bot.

## Features:
- Scrapes the top 20 voted memes from the `/r/memes` subreddit for the past 24 hours.
- Stores the scraped data in a MySQL database for historical tracking.
- Creates a RESTful API endpoint to fetch the top 20 memes stored in the database.
- Allows users to generate and share a CSV report of the top memes through a Telegram chatbot.
