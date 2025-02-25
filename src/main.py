from tkinter import Tk, Frame, Label, Entry, Button, StringVar, messagebox, Canvas, Scrollbar
import random
import requests

class WordleGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Wordle Clone")
        self.master.geometry("400x700")
        self.secret_word = self.get_random_word()
        self.attempts = 6
        self.current_attempt = 0
        self.guesses = []
        self.used_letters = set()
        self.correct_letters = set()
        self.incorrect_position_letters = set()

        self.create_widgets()

    def get_random_word(self):
        response = requests.get("https://random-word-api.herokuapp.com/word?number=1&length=5")
        if response.status_code == 200:
            return response.json()[0]
        else:
            return random.choice(["apple", "grape", "peach", "berry", "melon"])

    def create_widgets(self):
        self.canvas = Canvas(self.master)
        self.scrollbar = Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.frame = Frame(self.scrollable_frame, width=400)
        self.frame.pack(pady=20)

        self.guess_var = StringVar()
        self.guess_entry = Entry(self.frame, textvariable=self.guess_var, width=20, font=('Arial', 18))
        self.guess_entry.grid(row=0, column=0, columnspan=2)
        self.guess_entry.bind("<Return>", lambda event: self.submit_guess())

        self.submit_button = Button(self.frame, text="Submit", command=self.submit_guess, font=('Arial', 14))
        self.submit_button.grid(row=0, column=2)

        self.result_label = Label(self.frame, text="", font=('Arial', 14))
        self.result_label.grid(row=1, columnspan=3)

        self.guesses_frame = Frame(self.scrollable_frame, width=400)
        self.guesses_frame.pack(pady=20)

        self.letters_frame = Frame(self.scrollable_frame, width=400)
        self.letters_frame.pack(pady=20)

        self.update_letters_display()

        # Bind mousewheel scrolling
        self.master.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def is_valid_word(self, word):
        url = f"https://api.datamuse.com/words?sp={word}&max=1"
        response = requests.get(url)
        return response.status_code == 200 and len(response.json()) > 0 and any(word.get("score", 0) > 50000 for word in response.json())

    def submit_guess(self):
        guess = self.guess_var.get().lower()
        self.guess_var.set("")  # Clear the input field
        if len(guess) != 5:
            messagebox.showerror("Error", "Guess must be 5 letters long.")
            return
        if guess in self.guesses:
            messagebox.showerror("Error", "You already guessed that word.")
            return
        if not self.is_valid_word(guess):
            messagebox.showerror("Error", "Invalid word. Please enter a valid word.")
            return
        self.guesses.append(guess)
        self.current_attempt += 1

        self.display_guess(guess)
        self.update_letters(guess)

        if guess == self.secret_word:
            self.result_label.config(text="Congratulations! You've guessed the word!")
            self.guess_entry.config(state='disabled')
            return

        if self.current_attempt >= self.attempts:
            self.result_label.config(text=f"Game Over! The word was: {self.secret_word}")
            self.guess_entry.config(state='disabled')
            return

        self.result_label.config(text=f"Attempts left: {self.attempts - self.current_attempt}")

    def display_guess(self, guess):
        guess_frame = Frame(self.guesses_frame)
        guess_frame.pack()

        for i, letter in enumerate(guess):
            bg_color = "white"
            if letter in self.secret_word:
                if letter == self.secret_word[i]:
                    bg_color = "green"
                else:
                    bg_color = "yellow"

            letter_label = Label(guess_frame, text=letter.upper(), width=4, height=2, font=('Arial', 18), bg=bg_color, relief="solid", borderwidth=2)
            letter_label.pack(side="left", padx=5, pady=5)

    def update_letters(self, guess):
        for i, letter in enumerate(guess):
            self.used_letters.add(letter)
            if letter in self.secret_word:
                if letter == self.secret_word[i]:
                    self.correct_letters.add(letter)
                else:
                    self.incorrect_position_letters.add(letter)
        self.update_letters_display()

    def update_letters_display(self):
        for widget in self.letters_frame.winfo_children():
            widget.destroy()

        used_letters_label = Label(self.letters_frame, text="Used Letters: ", font=('Arial', 14))
        used_letters_label.pack()

        used_letters_box = Frame(self.letters_frame, relief="solid", borderwidth=1, padx=10, pady=10, width=350, height=50)
        used_letters_box.pack(pady=5)
        used_letters_box.pack_propagate(False)

        for letter in sorted(self.used_letters):
            color = "black"
            if letter in self.correct_letters:
                color = "green"
            elif letter in self.incorrect_position_letters:
                color = "yellow"
            letter_label = Label(used_letters_box, text=letter.upper(), font=('Arial', 14), fg=color)
            letter_label.pack(side="left", padx=2)

        unused_letters_label = Label(self.letters_frame, text="Unused Letters: ", font=('Arial', 14))
        unused_letters_label.pack()

        unused_letters_box = Frame(self.letters_frame, relief="solid", borderwidth=1, padx=10, pady=10, width=350, height=50)
        unused_letters_box.pack(pady=5)
        unused_letters_box.pack_propagate(False)

        for letter in "abcdefghijklmnopqrstuvwxyz":
            if letter not in self.used_letters:
                letter_label = Label(unused_letters_box, text=letter.upper(), font=('Arial', 14), fg="black")
                letter_label.pack(side="left", padx=2)

def main():
    root = Tk()
    game = WordleGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()