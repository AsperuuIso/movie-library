import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "movies.json"


class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library")
        self.root.geometry("800x600")

        # Инициализация хранилища данных
        self.movies = []
        self.load_data()

        # Создание интерфейса
        self._create_input_frame()
        self._create_filter_frame()
        self._create_table_frame()

    def _create_input_frame(self):
        """Создает панель ввода данных о фильме."""
        frame = tk.LabelFrame(self.root, text="Добавить фильм", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Поле: Название
        tk.Label(frame, text="Название:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_title = tk.Entry(frame, width=40)
        self.entry_title.grid(row=0, column=1, padx=5, pady=2)

        # Поле: Жанр
        tk.Label(frame, text="Жанр:").grid(row=0, column=2, sticky="w", pady=2)
        self.entry_genre = tk.Entry(frame, width=20)
        self.entry_genre.grid(row=0, column=3, padx=5, pady=2)

        # Поле: Год выпуска
        tk.Label(frame, text="Год:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_year = tk.Entry(frame, width=10)
        self.entry_year.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Поле: Рейтинг
        tk.Label(frame, text="Рейтинг (0-10):").grid(row=1, column=2, sticky="w", pady=2)
        self.entry_rating = tk.Entry(frame, width=10)
        self.entry_rating.grid(row=1, column=3, sticky="w", padx=5, pady=2)

        # Кнопка добавления
        btn_add = tk.Button(frame, text="Добавить фильм", command=self.add_movie)
        btn_add.grid(row=2, column=0, columnspan=4, pady=10, sticky="e")

    def _create_filter_frame(self):
        """Создает панель фильтрации."""
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Фильтр по жанру:").pack(side="left")
        self.filter_genre = tk.Entry(frame, width=15)
        self.filter_genre.pack(side="left", padx=5)
        self.filter_genre.bind("<KeyRelease>", self.apply_filters)

        tk.Label(frame, text="Фильтр по году:").pack(side="left", padx=(20, 0))
        self.filter_year = tk.Entry(frame, width=10)
        self.filter_year.pack(side="left", padx=5)
        self.filter_year.bind("<KeyRelease>", self.apply_filters)

        btn_reset = tk.Button(frame, text="Сброс", command=self.reset_filters)
        btn_reset.pack(side="right", padx=5)

    def _create_table_frame(self):
        """Создает таблицу для отображения фильмов."""
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("title", "genre", "year", "rating")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год")
        self.tree.heading("rating", text="Рейтинг")

        self.tree.column("title", width=300)
        self.tree.column("genre", width=150)
        self.tree.column("year", width=80)
        self.tree.column("rating", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Первоначальная отрисовка
        self.refresh_table()

    def validate_input(self):
        """Проверяет корректность введенных данных."""
        title = self.entry_title.get().strip()
        genre = self.entry_genre.get().strip()
        year_str = self.entry_year.get().strip()
        rating_str = self.entry_rating.get().strip()

        if not title or not genre:
            messagebox.showerror("Ошибка", "Название и жанр не могут быть пустыми.")
            return None

        try:
            year = int(year_str)
            if year < 1888 or year > 2026:  # 1888 - год первого фильма
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный год выпуска.")
            return None

        try:
            rating = float(rating_str)
            if rating < 0 or rating > 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом от 0 до 10.")
            return None

        return {
            "title": title,
            "genre": genre,
            "year": year,
            "rating": rating
        }

    def add_movie(self):
        """Добавляет фильм в список и сохраняет данные."""
        movie_data = self.validate_input()
        if movie_data is None:
            return

        self.movies.append(movie_data)
        self.save_data()
        self.refresh_table()
        self.clear_inputs()

    def clear_inputs(self):
        """Очищает поля ввода."""
        self.entry_title.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_rating.delete(0, tk.END)

    def get_filtered_movies(self):
        """Возвращает отфильтрованный список фильмов."""
        genre_filter = self.filter_genre.get().strip().lower()
        year_filter = self.filter_year.get().strip()

        filtered = []
        for movie in self.movies:
            match_genre = True
            match_year = True

            if genre_filter:
                if genre_filter not in movie["genre"].lower():
                    match_genre = False

            if year_filter:
                try:
                    if str(movie["year"]) != year_filter:
                        match_year = False
                except ValueError:
                    match_year = False

            if match_genre and match_year:
                filtered.append(movie)

        return filtered

    def apply_filters(self, event=None):
        """Обновляет таблицу при изменении фильтров."""
        self.refresh_table()

    def reset_filters(self):
        """Сбрасывает фильтры и обновляет таблицу."""
        self.filter_genre.delete(0, tk.END)
        self.filter_year.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self):
        """Перерисовывает таблицу с текущими данными."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        movies_to_show = self.get_filtered_movies()
        for movie in movies_to_show:
            self.tree.insert("", "end", values=(
                movie["title"],
                movie["genre"],
                movie["year"],
                movie["rating"]
            ))

    def save_data(self):
        """Сохраняет данные в JSON файл."""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
        except IOError as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        """Загружает данные из JSON файла."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showwarning("Предупреждение", f"Ошибка загрузки данных: {e}. Начнем с пустого списка.")
                self.movies = []


if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.mainloop()