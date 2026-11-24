import sqlite3

conn_forms = sqlite3.connect("forms.db")
cursor_forms = conn_forms.cursor()

cursor_forms.execute("DROP TABLE IF EXISTS forms")

cursor_forms.execute(
    'CREATE TABLE forms '
    '(f_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, "type" TEXT NOT NULL, size1 REAL NOT NULL, size2 REAL NOT NULL)'
)

forms_data = [
    ("Круглая малая (16 см)", "circle", 8.0, 0.0),
    ("Круглая стандарт (20 см)", "circle", 10.0, 0.0),
    ("Круглая большая (24 см)", "circle", 12.0, 0.0),
    ("Квадратная (20x20 см)", "rect", 20.0, 20.0),
    ("Прямоугольная (20x30 см)", "rect", 20.0, 30.0)
]

cursor_forms.executemany(
    "INSERT INTO forms (title, type, size1, size2) VALUES (?, ?, ?, ?)",
    forms_data
)

conn_forms.commit()
conn_forms.close()


conn_ing = sqlite3.connect("ingredients.db")
cursor_ing = conn_ing.cursor()

cursor_ing.execute("DROP TABLE IF EXISTS ingredients")

cursor_ing.execute(
    'CREATE TABLE ingredients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE ON CONFLICT FAIL NOT NULL, price REAL NOT NULL, "weight/volume" REAL NOT NULL)'
)

ingredients_data = [
    ("Мука пшеничная", 90.0, 1000.0),
    ("Сахар", 75.0, 1000.0),
    ("Масло сливочное", 220.0, 180.0),
    ("Яйца куриные (10 шт)", 130.0, 550.0),
    ("Сливки 33%", 350.0, 500.0),
    ("Творожный сыр", 280.0, 400.0)
]

cursor_ing.executemany(
    'INSERT INTO ingredients (name, price, "weight/volume") VALUES (?, ?, ?)',
    ingredients_data
)

conn_ing.commit()
conn_ing.close()

print("Обе базы данных (forms.db и ingredients.db) готовы!")
