# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 00:58:33 2025

@author: darel
"""

import tkinter as tk
from tkinter import messagebox, ttk, Canvas, Frame
import requests
from PIL import Image, ImageTk
from io import BytesIO


class OMDBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OMDB Movie Search")
        self.api_key = 'f0674f3f'  # Replace with your OMDB API key

        # Set full screen and background color
        self.root.attributes("-fullscreen", True)
        self.root.config(bg="#d6eaf8")

        self.recommendation_genre = None  # For storing genre for recommendations
        self.create_widgets()

    def create_widgets(self):
        # Header
        self.header_frame = tk.Frame(self.root, bg="#5dade2")
        self.header_frame.pack(fill=tk.X)

        self.title_label = tk.Label(
            self.header_frame,
            text="Welcome to the TMDB Movie App",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#5dade2",
            pady=10
        )
        self.title_label.pack()

        # Button Section
        self.button_frame = tk.Frame(self.root, bg="#d6eaf8")
        self.button_frame.pack(pady=20)

        self.search_label = tk.Label(self.button_frame, text="Enter Movie/Actor Name:", font=("Arial", 14), bg="#d6eaf8")
        self.search_label.grid(row=0, column=0, padx=10)

        self.search_entry = tk.Entry(self.button_frame, width=40, font=("Arial", 14), bd=2, relief="solid")
        self.search_entry.grid(row=0, column=1, padx=10)

        self.search_button = tk.Button(
            self.button_frame,
            text="Search",
            font=("Arial", 12),
            bg="#1abc9c",
            fg="white",
            relief="raised",
            command=self.search_movie
        )
        self.search_button.grid(row=0, column=2, padx=10)

        self.latest_button = tk.Button(
            self.button_frame,
            text="Latest Movies",
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            relief="raised",
            command=self.show_latest_movies
        )
        self.latest_button.grid(row=1, column=0, columnspan=3, pady=10)

        self.recommend_button = tk.Button(
            self.button_frame,
            text="Recommendations",
            font=("Arial", 12),
            bg="#9b59b6",
            fg="white",
            relief="raised",
            command=self.get_recommendations
        )
        self.recommend_button.grid(row=2, column=0, columnspan=3, pady=10)

        # Main Content
        self.content_frame = tk.Frame(self.root, bg="#d6eaf8")
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        self.result_text = tk.Text(self.content_frame, width=60, height=20, wrap=tk.WORD, font=("Arial", 12), bd=2, relief="solid", bg="#ecf0f1")
        self.result_text.grid(row=0, column=0, padx=10)

        self.poster_frame = tk.Frame(self.content_frame, bg="#d6eaf8")
        self.poster_frame.grid(row=0, column=1, padx=10)

        # Footer
        self.footer_frame = tk.Frame(self.root, bg="#5dade2")
        self.footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.exit_button = tk.Button(
            self.footer_frame,
            text="Exit",
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            relief="raised",
            command=self.root.quit
        )
        self.exit_button.pack(pady=10)

    def search_movie(self):
        movie_name = self.search_entry.get()
        if not movie_name:
            messagebox.showerror("Error", "Please enter a movie name.")
            return

        url = f'http://www.omdbapi.com/?apikey={self.api_key}&t={movie_name}'
        response = requests.get(url)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to retrieve data.")
            return

        data = response.json()
        if data.get('Response') == 'False':
            messagebox.showerror("Error", "Movie not found.")
            return

        self.recommendation_genre = data.get('Genre', '').split(',')[0].strip()  # Save genre for recommendations
        self.display_result(data)

        # Fetch the poster and display it
        poster_url = data.get('Poster', '')
        if poster_url and poster_url != 'N/A':
            response = requests.get(poster_url)
            if response.status_code == 200:
                image_data = response.content
                image = Image.open(BytesIO(image_data))
                image = image.resize((150, 200))  # Resize as needed
                photo = ImageTk.PhotoImage(image)

                # Display the poster in the poster frame
                poster_label = tk.Label(self.poster_frame, image=photo, bg="#d6eaf8")
                poster_label.image = photo  # Keep a reference to avoid garbage collection
                poster_label.pack(pady=10)

    def get_recommendations(self):
        if not self.recommendation_genre:
            messagebox.showinfo("Recommendations", "Search for a movie first to get recommendations.")
            return

        url = f'http://www.omdbapi.com/?apikey={self.api_key}&s={self.recommendation_genre}&page=1'
        response = requests.get(url)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to retrieve recommendations.")
            return

        data = response.json()
        if data.get('Response') == 'False':
            messagebox.showinfo("Recommendations", "No recommendations found.")
            return

        movies = data.get('Search', [])
        self.display_posters(movies)

    def show_latest_movies(self):
        url = f'http://www.omdbapi.com/?apikey={self.api_key}&s=2023&page=1'
        response = requests.get(url)
        if response.status_code != 200:
            messagebox.showerror("Error", "Failed to retrieve latest movies.")
            return

        data = response.json()
        if data.get('Response') == 'False':
            messagebox.showerror("Error", "No latest movies found.")
            return

        movies = data.get('Search', [])
        self.display_posters(movies)

    def display_posters(self, movies):
        # Clear existing widgets
        for widget in self.poster_frame.winfo_children():
            widget.destroy()

        # Scrollable Frame
        canvas = Canvas(self.poster_frame, bg="#d6eaf8")
        scroll_y = ttk.Scrollbar(self.poster_frame, orient="vertical", command=canvas.yview)

        scrollable_frame = Frame(canvas, bg="#d6eaf8")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Display posters in grid
        row, col = 0, 0
        for movie in movies:
            title = movie.get('Title', 'Unknown')
            poster_url = movie.get('Poster', '')
            if poster_url and poster_url != 'N/A':
                response = requests.get(poster_url)
                if response.status_code == 200:
                    image_data = response.content
                    image = Image.open(BytesIO(image_data))
                    image = image.resize((150, 200))
                    photo = ImageTk.PhotoImage(image)

                    frame = tk.Frame(scrollable_frame, bg="#d6eaf8", pady=10, padx=10)
                    frame.grid(row=row, column=col, padx=20, pady=10)

                    label = tk.Label(frame, image=photo, bg="#d6eaf8")
                    label.image = photo
                    label.pack()

                    text = tk.Label(frame, text=title, font=("Arial", 10), wraplength=150, bg="#d6eaf8")
                    text.pack()

                    col += 1
                    if col > 3:  # Limit to 4 posters per row
                        col = 0
                        row += 1

    def display_result(self, data):
        self.result_text.delete(1.0, tk.END)
        result = (f"Title: {data.get('Title')}\n"
                  f"Year: {data.get('Year')}\n"
                  f"Genre: {data.get('Genre')}\n"
                  f"Director: {data.get('Director')}\n"
                  f"Actors: {data.get('Actors')}\n"
                  f"Plot: {data.get('Plot')}\n")
        self.result_text.insert(tk.END, result)


if __name__ == "__main__":
    root = tk.Tk()
    app = OMDBApp(root)
    root.mainloop()
