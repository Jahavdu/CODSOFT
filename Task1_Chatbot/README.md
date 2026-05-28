# Advanced AI Chatbot

An advanced offline AI chatbot built using Python and CustomTkinter for the CodSoft Artificial Intelligence Internship.

## Features

* Modern dark-themed GUI
* Voice output support
* Sentiment analysis
* User memory with SQLite database
* Typing animation effect
* Chat history logging
* Time detection
* Basic calculator support
* Fuzzy text matching
* Persistent user data
* Offline functionality

## Technologies Used

* Python
* CustomTkinter
* SQLite3
* pyttsx3
* thefuzz

## Project Structure

```text
Task1_Chatbot
│
├── chatbot.py
├── requirements.txt
├── README.md
├── bot_memory.db
└── chat_history.txt
```

## How to Run

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/CODSOFT.git
```

### 2. Navigate to Project

```bash
cd CODSOFT/Task1_Chatbot
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Run the Chatbot

```bash
python chatbot.py
```

## Example Commands

* hello
* hi
* what time is it
* calculate 5 + 5
* my name is Durvesh
* what is my name
* system info

## Features Explained

### SQLite Memory

The chatbot remembers user information even after restarting the application.

### Sentiment Analysis

The chatbot detects positive and negative emotions in user messages.

### Voice Output

Optional text-to-speech functionality using pyttsx3.

### Fuzzy Matching

Handles typos and similar text using thefuzz library.

## Internship

This project was created as part of the CodSoft Artificial Intelligence Internship.

## Author

Durvesh Jadhav
