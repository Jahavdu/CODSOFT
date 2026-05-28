import customtkinter as ctk
import re
from datetime import datetime
import sqlite3
import platform
import threading
import pyttsx3
from thefuzz import process


class AdvancedBrain:
    def __init__(self):
        self.conn = sqlite3.connect("bot_memory.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS user_data (key TEXT UNIQUE, value TEXT)")
        self.conn.commit()

        self.user_name = self.get_memory("name")
        self.last_math_result = None

        self.intents = [
            "system info", "what is my name", "what time is it",
            "hello", "hi", "calculate"
        ]

        self.positive_words = ['good', 'great', 'awesome', 'thanks', 'love', 'happy', 'cool']
        self.negative_words = ['bad', 'terrible', 'hate', 'stupid', 'wrong', 'sucks', 'angry']

    def get_memory(self, key):
        self.cursor.execute("SELECT value FROM user_data WHERE key=?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def save_memory(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO user_data (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def analyze_sentiment(self, text):
        words = text.split()
        if any(word in self.negative_words for word in words):
            return "negative"
        if any(word in self.positive_words for word in words):
            return "positive"
        return "neutral"

    def process_input(self, text):
        text = text.lower().strip()

        sentiment = self.analyze_sentiment(text)
        sentiment_prefix = ""
        if sentiment == "negative":
            sentiment_prefix = "I'm sorry you feel that way! Let me try to help. "
        elif sentiment == "positive":
            sentiment_prefix = "I'm glad to hear that! "

        if text.startswith("my name is"):
            name = text.replace("my name is", "").strip().title()
            if name:
                self.user_name = name
                self.save_memory("name", name)
                return f"{sentiment_prefix}Nice to meet you, {self.user_name}! I've securely saved your name."
            return "I didn't quite catch your name."

        if "calculate" in text or re.search(r'\d+\s*[\+\-\*/]\s*\d+', text):
            match = re.search(r"(\d+(\.\d+)?)\s*([\+\-\*/])\s*(\d+(\.\d+)?)", text)
            if match:
                num1, operator, num2 = float(match.group(1)), match.group(3), float(match.group(4))
                try:
                    if operator == '+':
                        res = num1 + num2
                    elif operator == '-':
                        res = num1 - num2
                    elif operator == '*':
                        res = num1 * num2
                    elif operator == '/':
                        res = num1 / num2

                    self.last_math_result = res
                    res = int(res) if res == int(res) else round(res, 4)
                    return f"{sentiment_prefix}The result is {res}"
                except ZeroDivisionError:
                    return "I can't divide by zero!"

        best_match, match_score = process.extractOne(text, self.intents)

        if match_score >= 70:
            if best_match == "system info":
                return f"{sentiment_prefix}Running offline on your {platform.system()} {platform.release()} machine."
            elif best_match == "what is my name":
                if self.user_name:
                    return f"{sentiment_prefix}Your name is {self.user_name}."
                return "I don't know your name yet! Just say 'My name is...'"
            elif best_match == "what time is it":
                return f"{sentiment_prefix}The current time is {datetime.now().strftime('%I:%M %p')}."
            elif best_match in ["hello", "hi"]:
                if self.user_name:
                    return f"{sentiment_prefix}Welcome back, {self.user_name}!"
                return f"{sentiment_prefix}Hello there! How can I help?"

        return f"{sentiment_prefix}I'm not quite sure how to respond to that. Try asking for system info or math!"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("AI Assistant")
        self.geometry("600x700")
        self.configure(fg_color="#18181B")

        self.attributes("-alpha", 0.0)

        self.brain = AdvancedBrain()
        self.voice_enabled = ctk.BooleanVar(value=False)
        self.is_thinking = False

        self.build_ui()
        self.fade_in()

        if self.brain.user_name:
            startup_msg = f"Database connected. Welcome back, {self.brain.user_name}."
        else:
            startup_msg = "Database connected. Welcome! I am your AI Assistant."

        self.status_label.configure(text="Typing...")

        # Log the startup message
        self.log_to_file("Bot", startup_msg)
        self.type_bot_message(startup_msg)

    def log_to_file(self, sender, text):
        """Appends the conversation history to a local text file with timestamps."""
        try:
            with open("chat_history.txt", "a", encoding="utf-8") as file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"[{timestamp}] {sender}: {text}\n")
        except Exception as e:
            print(f"Failed to write to log: {e}")

    def fade_in(self, current_alpha=0.0):
        if current_alpha < 1.0:
            current_alpha += 0.05
            self.attributes("-alpha", current_alpha)
            self.after(20, self.fade_in, current_alpha)

    def speak_text(self, text):
        if not self.voice_enabled.get():
            return

        def run_speech():
            engine = pyttsx3.init()
            engine.setProperty('rate', 160)
            voices = engine.getProperty('voices')
            if len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            engine.say(text)
            engine.runAndWait()

        threading.Thread(target=run_speech, daemon=True).start()

    def build_ui(self):
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=(20, 5), fill="x", padx=20)

        self.header = ctk.CTkLabel(
            self.top_frame, text="AI Assistant",
            font=("Helvetica", 24, "bold"), text_color="#F4F4F5"
        )
        self.header.pack(side="left", padx=10)

        self.voice_switch = ctk.CTkSwitch(
            self.top_frame, text="Voice output", variable=self.voice_enabled,
            font=("Helvetica", 12), text_color="#A1A1AA",
            progress_color="#3B82F6", button_color="#FFFFFF", button_hover_color="#E4E4E7"
        )
        self.voice_switch.pack(side="right", padx=10)

        self.chat_display = ctk.CTkTextbox(
            self, width=500, height=430,
            corner_radius=12, fg_color="#27272A", text_color="#FFFFFF",
            font=("Helvetica", 15), wrap="word"
        )
        self.chat_display.pack(pady=5, padx=20)
        self.chat_display.configure(state="disabled")

        self.status_label = ctk.CTkLabel(
            self, text="", font=("Helvetica", 12, "italic"), text_color="#A1A1AA"
        )
        self.status_label.pack(anchor="w", padx=45)

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=10, fill="x", padx=45)

        self.entry = ctk.CTkEntry(
            self.input_frame, width=400, height=45,
            corner_radius=20, fg_color="#3F3F46", border_width=0,
            text_color="#FFFFFF", placeholder_text="Type a message..."
        )
        self.entry.pack(side="left", padx=(0, 10))
        self.entry.bind("<Return>", self.handle_send)

        self.send_btn = ctk.CTkButton(
            self.input_frame, text="Send", width=90, height=45,
            corner_radius=20, fg_color="#3B82F6", text_color="#FFFFFF",
            font=("Helvetica", 14, "bold"), hover_color="#2563EB",
            command=self.handle_send
        )
        self.send_btn.pack(side="left")

    def display_user_message(self, text):
        self.chat_display.configure(state="normal")
        self.chat_display.tag_config("You_Name", foreground="#A1A1AA")
        self.chat_display.tag_config("You_Text", foreground="#D4D4D8")

        self.chat_display.insert("end", "You\n", "You_Name")
        self.chat_display.insert("end", f"{text}\n\n", "You_Text")

        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def animate_dots(self, count=0):
        if self.is_thinking:
            dots = "." * (count % 4)
            self.status_label.configure(text=f"Thinking{dots}")
            self.after(300, self.animate_dots, count + 1)

    def start_bot_typing(self, bot_response):
        self.is_thinking = False
        self.status_label.configure(text="Typing...")
        self.speak_text(bot_response)
        self.type_bot_message(bot_response, 0)

    def type_bot_message(self, full_text, index=0):
        self.chat_display.configure(state="normal")

        if index == 0:
            self.chat_display.tag_config("Bot_Name", foreground="#FFFFFF")
            self.chat_display.tag_config("Bot_Text", foreground="#FFFFFF")
            self.chat_display.insert("end", "Bot\n", "Bot_Name")

        if index < len(full_text):
            self.chat_display.insert("end", full_text[index], "Bot_Text")
            self.chat_display.see("end")
            self.after(15, self.type_bot_message, full_text, index + 1)
        else:
            self.chat_display.insert("end", "\n\n")
            self.chat_display.configure(state="disabled")
            self.chat_display.see("end")

            self.status_label.configure(text="")
            self.entry.configure(state="normal")
            self.send_btn.configure(state="normal")
            self.entry.focus()

    def handle_send(self, event=None):
        user_input = self.entry.get()
        if not user_input.strip():
            return

        self.entry.delete(0, "end")
        self.entry.configure(state="disabled")
        self.send_btn.configure(state="disabled")

        self.display_user_message(user_input)

        # Log the user's message
        self.log_to_file("You", user_input)

        self.is_thinking = True
        self.animate_dots()

        bot_response = self.brain.process_input(user_input)

        # Log the bot's message instantly (even though it types slowly on screen)
        self.log_to_file("Bot", bot_response)

        self.after(1200, self.start_bot_typing, bot_response)


if __name__ == "__main__":
    app = App()
    app.mainloop()