import customtkinter as ctk
import math
import random
import sqlite3


class TicTacToeGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        ctk.set_appearance_mode("dark")
        self.title("Advanced AI Tic-Tac-Toe")
        self.geometry("460x760")
        self.configure(fg_color="#18181B")
        self.resizable(False, False)

        # --- Database Storage Initialization ---
        self.conn = sqlite3.connect("tictactoe_stats.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS stats (key TEXT UNIQUE, value INTEGER)")
        self.conn.commit()

        # Load scores from local DB
        self.player_wins = self.get_score_stat("player_wins")
        self.ai_wins = self.get_score_stat("ai_wins")
        self.draws = self.get_score_stat("draws")

        # --- Core Game State ---
        self.board = [" " for _ in range(9)]
        self.buttons = []
        self.game_active = True
        self.first_turn = "Player"  # Default starting player

        self.build_ui()

    # --- DB Helper Functions ---
    def get_score_stat(self, key):
        self.cursor.execute("SELECT value FROM stats WHERE key=?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def save_score_stat(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO stats (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    # --- UI Layout Assembly ---
    def build_ui(self):
        # 1. Main Header Title
        self.header = ctk.CTkLabel(
            self, text="Tic-Tac-Toe Engine",
            font=("Helvetica", 26, "bold"), text_color="#F4F4F5"
        )
        self.header.pack(pady=(20, 5))

        # 2. Control Panel Frame (Difficulty & Starting Turn Options)
        self.panel_frame = ctk.CTkFrame(self, fg_color="#27272A", corner_radius=12)
        self.panel_frame.pack(pady=10, padx=20, fill="x")

        # Difficulty Dropdown Selector
        self.diff_label = ctk.CTkLabel(self.panel_frame, text="AI Difficulty:", font=("Helvetica", 12, "bold"),
                                       text_color="#A1A1AA")
        self.diff_label.grid(row=0, column=0, padx=15, pady=(10, 2), sticky="w")

        self.diff_select = ctk.CTkComboBox(
            self.panel_frame, values=["Unbeatable", "Medium", "Easy"],
            font=("Helvetica", 12), width=160, fg_color="#3F3F46", border_width=0
        )
        self.diff_select.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="w")

        # Starting Turn Selector
        self.turn_label = ctk.CTkLabel(self.panel_frame, text="First Move:", font=("Helvetica", 12, "bold"),
                                       text_color="#A1A1AA")
        self.turn_label.grid(row=0, column=1, padx=15, pady=(10, 2), sticky="w")

        self.turn_select = ctk.CTkSegmentedButton(
            self.panel_frame, values=["Player", "AI"], font=("Helvetica", 12),
            selected_color="#3B82F6", unselected_color="#3F3F46", command=self.change_start_turn
        )
        self.turn_select.set("Player")
        self.turn_select.grid(row=1, column=1, padx=15, pady=(0, 12), sticky="w")

        # 3. Persistent Scoreboard
        self.score_label = ctk.CTkLabel(
            self,
            text=f"You: {self.player_wins}   |   Draws: {self.draws}   |   AI: {self.ai_wins}",
            font=("Helvetica", 15, "bold"), text_color="#A1A1AA"
        )
        self.score_label.pack(pady=5)

        # 4. Game Board Matrix
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(pady=15)

        for i in range(9):
            btn = ctk.CTkButton(
                self.grid_frame, text=" ", width=105, height=105,
                font=("Helvetica", 42, "bold"), fg_color="#27272A",
                hover_color="#3F3F46", text_color="#FFFFFF",
                corner_radius=12, command=lambda idx=i: self.player_click(idx)
            )
            row, col = divmod(i, 3)
            btn.grid(row=row, column=col, padx=6, pady=6)
            self.buttons.append(btn)

        # 5. Status Output bar
        self.status_label = ctk.CTkLabel(
            self, text="Your turn! Place an X",
            font=("Helvetica", 16, "bold"), text_color="#60A5FA"
        )
        self.status_label.pack(pady=5)

        # 6. Action Control Action Buttons
        self.reset_btn = ctk.CTkButton(
            self, text="Next Match", width=220, height=45,
            font=("Helvetica", 14, "bold"), fg_color="#3B82F6",
            hover_color="#2563EB", corner_radius=22, command=self.reset_game
        )
        self.reset_btn.pack(pady=5)

        self.clear_stats_btn = ctk.CTkButton(
            self, text="Reset Career History", width=160, height=30,
            font=("Helvetica", 11), fg_color="transparent", text_color="#EF4444",
            hover_color="#27272A", command=self.clear_career_history
        )
        self.clear_stats_btn.pack(pady=(2, 10))

    # --- Runtime Custom Configurations ---
    def change_start_turn(self, selection):
        self.first_turn = selection
        if len([x for x in self.board if x == " "]) == 9:
            if self.first_turn == "AI":
                self.status_label.configure(text="AI is processing strategy...", text_color="#F472B6")
                self.after(500, self.ai_turn)

    # --- Game Mechanics Engines ---
    def player_click(self, index):
        if self.game_active and self.board[index] == " " and "thinking" not in self.status_label.cget("text"):
            # Lock selections during an active match round
            self.diff_select.configure(state="disabled")
            self.turn_select.configure(state="disabled")

            self.board[index] = "X"
            self.buttons[index].configure(text="X", text_color="#60A5FA")

            if self.check_game_over(): return

            self.status_label.configure(text="AI is processing strategy...", text_color="#F472B6")
            self.after(500, self.ai_turn)

    def ai_turn(self):
        if not self.game_active: return

        difficulty = self.diff_select.get()
        chosen_move = None

        # Logic Branching based on selected difficulty engine
        if difficulty == "Easy":
            chosen_move = self.get_random_move()
        elif difficulty == "Medium":
            # 50% chance to make a random choice vs a perfect logic choice
            if random.random() < 0.5:
                chosen_move = self.get_random_move()
            else:
                chosen_move = self.get_best_minimax_move()
        else:  # Unbeatable default routing
            chosen_move = self.get_best_minimax_move()

        if chosen_move is not None:
            self.board[chosen_move] = "O"
            self.buttons[chosen_move].configure(text="O", text_color="#F87171")

        if self.check_game_over(): return

        self.status_label.configure(text="Your turn! Place an X", text_color="#60A5FA")

    def get_random_move(self):
        empty_indices = [i for i, val in enumerate(self.board) if val == " "]
        return random.choice(empty_indices) if empty_indices else None

    def get_best_minimax_move(self):
        best_score = -math.inf
        best_move = None
        for i in range(9):
            if self.board[i] == " ":
                self.board[i] = "O"
                score = self.minimax(False)
                self.board[i] = " "
                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move

    def minimax(self, is_maximizing):
        winner, _ = self.check_winner_logic()
        if winner == "O": return 1
        if winner == "X": return -1
        if " " not in self.board: return 0

        if is_maximizing:
            best_score = -math.inf
            for i in range(9):
                if self.board[i] == " ":
                    self.board[i] = "O"
                    score = self.minimax(False)
                    self.board[i] = " "
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = math.inf
            for i in range(9):
                if self.board[i] == " ":
                    self.board[i] = "X"
                    score = self.minimax(True)
                    self.board[i] = " "
                    best_score = min(score, best_score)
            return best_score

    # --- Structural Verification & Diagnostics ---
    def check_winner_logic(self):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for combo in win_conditions:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != " ":
                return self.board[combo[0]], combo
        return None, None

    def check_game_over(self):
        winner, winning_combo = self.check_winner_logic()

        if winner:
            self.game_active = False
            if winner == "X":
                self.player_wins += 1
                self.save_score_stat("player_wins", self.player_wins)
                self.status_label.configure(text="Victory achieved!", text_color="#34D399")
                self.highlight_winning_cells(winning_combo, "#059669")
            else:
                self.ai_wins += 1
                self.save_score_stat("ai_wins", self.ai_wins)
                self.status_label.configure(text="AI successfully outmaneuvered you.", text_color="#F87171")
                self.highlight_winning_cells(winning_combo, "#991B1B")

            self.refresh_scoreboard_display()
            return True

        if " " not in self.board:
            self.game_active = False
            self.draws += 1
            self.save_score_stat("draws", self.draws)
            self.status_label.configure(text="Stalemate. Board complete.", text_color="#FBBF24")
            self.refresh_scoreboard_display()
            for btn in self.buttons:
                btn.configure(fg_color="#78350F")
            return True

        return False

    def highlight_winning_cells(self, combo, target_color):
        for index in combo:
            self.buttons[index].configure(fg_color=target_color)

    def refresh_scoreboard_display(self):
        self.score_label.configure(text=f"You: {self.player_wins}   |   Draws: {self.draws}   |   AI: {self.ai_wins}")

    # --- Match & Session Controls ---
    def reset_game(self):
        self.board = [" " for _ in range(9)]
        self.game_active = True

        # Unlock parameters for custom configurations before starting match
        self.diff_select.configure(state="normal")
        self.turn_select.configure(state="normal")

        for btn in self.buttons:
            btn.configure(text=" ", fg_color="#27272A")

        if self.first_turn == "AI":
            self.status_label.configure(text="AI is processing strategy...", text_color="#F472B6")
            self.after(500, self.ai_turn)
        else:
            self.status_label.configure(text="Your turn! Place an X", text_color="#60A5FA")

    def clear_career_history(self):
        self.player_wins = 0
        self.ai_wins = 0
        self.draws = 0
        self.save_score_stat("player_wins", 0)
        self.save_score_stat("ai_wins", 0)
        self.save_score_stat("draws", 0)
        self.refresh_scoreboard_display()


if __name__ == "__main__":
    app = TicTacToeGUI()
    app.mainloop()