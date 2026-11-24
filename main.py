import sys
import os
import math
import sqlite3
import csv
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QTableWidgetItem, QCompleter,
    QMessageBox, QPushButton, QFileDialog, QInputDialog, QVBoxLayout
)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from CakeCalculator import Ui_MainWindow
from ResultWindow import Ui_ResultWindow


def resource_path(relsative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relsative_path)
    return os.path.join(os.path.abspath('.'), relsative_path)

# второе окно
class ResultWindow(QWidget, Ui_ResultWindow):
    def __init__(self, coefficient, ingredients):
        super().__init__()
        self.setupUi(self)
        self.tab(coefficient, ingredients)

        self.coefficient = coefficient
        self.ingredients = ingredients

        # Кнопка сохранения в csv
        self.save_btn = QPushButton("Сохранить в CSV")
        self.save_btn.clicked.connect(self.save_csv)

        lay = self.layout()
        if not lay:
            lay = QVBoxLayout(self)
            self.setLayout(lay)
        lay.addWidget(self.save_btn)

    def tab(self, coefficient, ingredients):
        # коэффициент в подпись над таблицей
        self.coeff_label.setText(f"Коэффициент пересчёта: {coefficient:.2f}")

        self.ingredients_table.setColumnCount(3)
        self.ingredients_table.setHorizontalHeaderLabels(
            ["Ингредиент", "Было", "Станет"]
        )
        self.ingredients_table.setRowCount(len(ingredients))

        for row_index, (name, base_weight) in enumerate(ingredients):
            new_weight = base_weight * coefficient

            self.ingredients_table.setItem(row_index, 0, QTableWidgetItem(name))
            self.ingredients_table.setItem(row_index, 1, QTableWidgetItem(f"{base_weight:.1f}"))
            self.ingredients_table.setItem(row_index, 2, QTableWidgetItem(f"{new_weight:.1f}"))

        self.ingredients_table.resizeColumnsToContents()

    # 
    def save_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить результат", "результат.csv", "CSV файлы (*.csv)")
        if not file_path:  # Отмена
            return

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")

            # Заголовок таблицы
            writer.writerow(["Ингредиент", "Было (г)", "Станет (г)"])
            for name, base_weight in self.ingredients:
                writer.writerow(
                    [name, f"{base_weight:.1f}", f"{base_weight * self.coefficient:.1f}"]
                )

        QMessageBox.information(self, "Готово", "Файл сохранён!")


# первое окно
class CakeCalculator(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connect_databases()
        self.Window_title()
        self.input_fields()
        self.autocomplete()

    # Подключение баз данных
    def connect_databases(self):
        self.conn_forms = sqlite3.connect("forms.db")
        self.choose_form = self.conn_forms.cursor()

        self.choose_form.execute(
            'CREATE TABLE IF NOT EXISTS forms (f_id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'title TEXT NOT NULL, type TEXT NOT NULL, size1 REAL NOT NULL, size2 REAL NOT NULL)'
        )

        self.choose_form.execute("SELECT COUNT(*) FROM forms")
        (count_forms,) = self.choose_form.fetchone()
        if count_forms == 0:
            forms_data = [
                ("Круглая малая (16 см)", "circle", 8.0, 0.0),
                ("Круглая стандарт (20 см)", "circle", 10.0, 0.0),
                ("Круглая большая (24 см)", "circle", 12.0, 0.0),
                ("Квадратная (20x20 см)", "rect", 20.0, 20.0),
                ("Прямоугольная (20x30 см)", "rect", 20.0, 30.0)
            ]
            self.choose_form.executemany(
                'INSERT INTO forms (title, type, size1, size2) VALUES (?, ?, ?, ?)',
                forms_data
            )
            self.conn_forms.commit()

        self.conn_ing = sqlite3.connect("ingredients.db")
        self.cursor_ing = self.conn_ing.cursor()

        try:
            self.cursor_ing.execute('ALTER TABLE ingredients RENAME COLUMN "weight/volume" TO weight')
            self.conn_ing.commit()
        except sqlite3.OperationalError:
            pass  # столбца нет или он уже называется weight

        self.cursor_ing.execute(
            '''CREATE TABLE IF NOT EXISTS ingredients (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT UNIQUE ON CONFLICT FAIL NOT NULL, weight REAL NOT NULL)'''
        )

        self.cursor_ing.execute("SELECT COUNT(*) FROM ingredients")
        (count,) = self.cursor_ing.fetchone()
        if count == 0:
            ingredients_data = [
                ("Мука пшеничная", 1000.0),
                ("Сахар", 1000.0),
                ("Масло сливочное", 180.0),
                ("Яйца куриные (10 шт)", 550.0),
                ("Сливки 33%", 500.0),
                ("Творожный сыр", 400.0)
            ]
            self.cursor_ing.executemany(
                'INSERT INTO ingredients (name, weight) VALUES (?, ?)',
                ingredients_data
            )
            self.conn_ing.commit()

    def Window_title(self):
        self.setWindowTitle('Калькулятор пересчета ингредиентов торта')
        self.setFixedHeight(450)
        self.setFixedWidth(600)

    def autocomplete(self):
        self.choose_form.execute('SELECT type, size1, size2 FROM forms')
        forms = self.choose_form.fetchall()

        circle_sizes = []
        rect_sizes = []

        for form_type, s1, s2 in forms:
            if form_type == "circle":
                diam_val = float(s1) * 2
                diam = str(int(diam_val)) if diam_val.is_integer() else str(diam_val)
                if diam not in circle_sizes:
                    circle_sizes.append(diam)
            elif form_type == "rect":
                s1_val = float(s1)
                s2_val = float(s2)
                side1 = str(int(s1_val)) if s1_val.is_integer() else str(s1_val)
                side2 = str(int(s2_val)) if s2_val.is_integer() else str(s2_val)
                if side1 not in rect_sizes:
                    rect_sizes.append(side1)
                if side2 not in rect_sizes:
                    rect_sizes.append(side2)

        for field in (self.rad_1, self.rad_2):
            completer = QCompleter(circle_sizes, self)
            completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
            field.setCompleter(completer)
            field.mousePressEvent = self.opener(field)

        for field in (self.height_1, self.width_1, self.height_2, self.width_2):
            completer = QCompleter(rect_sizes, self)
            completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
            field.setCompleter(completer)
            field.mousePressEvent = self.opener(field)

    def opener(self, line_edit):
        original_mouse_press = line_edit.mousePressEvent

        def click(w):
            original_mouse_press(w)
            if line_edit.completer():
                line_edit.completer().complete()

        return click

    def input_fields(self):
        self.hide_line()

        self.rad_1.setPlaceholderText('Диаметр')
        self.rad_2.setPlaceholderText('Диаметр')
        self.height_1.setPlaceholderText('Длина')
        self.width_1.setPlaceholderText('Ширина')
        self.height_2.setPlaceholderText('Длина')
        self.width_2.setPlaceholderText('Ширина')

        self.circlebtn_1.clicked.connect(self.show_circle1)
        self.squarebtn_1.clicked.connect(self.show_rect1)

        self.circlebtn_2.clicked.connect(self.show_circle2)
        self.squarebtn_2.clicked.connect(self.show_rect2)

        self.calculate.clicked.connect(self.calculate_ingredients)

        self.add_ing_btn.clicked.connect(self.add_ingredient)
        self.del_ing_btn.clicked.connect(self.delete_ingredient)

        # размер иконок
        icon_size = QSize(100, 100)
        icon_size1 = QSize(150, 150)

        # кнопки круглой формы
        self.circlebtn_1.setIcon(QIcon(resource_path("circle.png")))
        self.circlebtn_2.setIcon(QIcon(resource_path("circle.png")))

        # кнопки квадратной формы
        self.squarebtn_1.setIcon(QIcon(resource_path("rect.png")))
        self.squarebtn_2.setIcon(QIcon(resource_path("rect.png")))

        # сразмер кнопок
        for btn in (self.circlebtn_1, self.circlebtn_2):
            btn.setIconSize(icon_size)

        for btn1 in (self.squarebtn_1, self.squarebtn_2):
            btn1.setIconSize(icon_size1)

    def hide_line(self):
        self.rad_1.hide()
        self.height_1.hide()
        self.width_1.hide()
        self.rad_2.hide()
        self.height_2.hide()
        self.width_2.hide()

    def show_circle1(self):
        self.height_1.hide()
        self.width_1.hide()
        self.rad_1.show()

    def show_rect1(self):
        self.rad_1.hide()
        self.height_1.show()
        self.width_1.show()

    def show_circle2(self):
        self.height_2.hide()
        self.width_2.hide()
        self.rad_2.show()

    def show_rect2(self):
        self.rad_2.hide()
        self.height_2.show()
        self.width_2.show()

    def calculate_ingredients(self):
        try:
            # 1. площадь формы из рецепта
            if self.rad_1.isVisible():
                d1 = float(self.rad_1.text())
                r1 = d1 / 2
                area_recipe = math.pi * (r1 ** 2)
            elif self.height_1.isVisible() and self.width_1.isVisible():
                a1 = float(self.height_1.text())
                b1 = float(self.width_1.text())
                area_recipe = a1 * b1
            else:
                QMessageBox.warning(self, "Форма не выбрана",
                                    "Сначала выберите форму из рецепта!")
                return

            # 2. площадь нужной формы
            if self.rad_2.isVisible():
                d2 = float(self.rad_2.text())
                r2 = d2 / 2
                area_my = math.pi * (r2 ** 2)
            elif self.height_2.isVisible() and self.width_2.isVisible():
                a2 = float(self.height_2.text())
                b2 = float(self.width_2.text())
                area_my = a2 * b2
            else:
                QMessageBox.warning(self, "Форма не выбрана",
                                    "Сначала выберите свою форму!")
                return

            if area_recipe <= 0 or area_my <= 0:
                QMessageBox.warning(self, "Неверные числа",
                                    "Числа должны быть больше нуля!")
                return

            coefficient = area_my / area_recipe
            self.result.setText(f"Коэффициент = {coefficient:.2f}")

            self.cursor_ing.execute('SELECT name, weight FROM ingredients')
            ingredients_data = self.cursor_ing.fetchall()
            self.window_2 = ResultWindow(coefficient, ingredients_data)
            self.window_2.show()

        except ValueError:
            QMessageBox.critical(self, "Ошибка ввода",
                                 "В поля нужно вводить только числа!")

     # Добавление ингредиентов в бд
    def add_ingredient(self):
        """Добавляет новый ингредиент в базу"""
        name, ok = QInputDialog.getText(self, "Новый ингредиент", "Название:")
        if not ok or not name.strip():
            return

        weight_input, ok = QInputDialog.getText(
            self, "Новый ингредиент", f"Вес «{name}» (в граммах):")
        if not ok:
            return

        try:
            weight = float(weight_input.replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Ошибка ввода",
                                "Вес должен быть числом!")
            return

        if weight <= 0:
            QMessageBox.warning(self, "Неверное число",
                                "Вес должен быть больше нуля!")
            return

        try:
            self.cursor_ing.execute(
                'INSERT INTO ingredients (name, weight) VALUES (?, ?)',
                (name.strip(), weight)
            )
            self.conn_ing.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Такой уже есть",
                                f"Ингредиент «{name}» уже есть в базе!")
            return

        QMessageBox.information(self, "Готово",
                                f"«{name}» добавлен в базу!")

    # Удаление ингредиентов из бд
    def delete_ingredient(self):
        self.cursor_ing.execute('SELECT name FROM ingredients')
        names = [row[0] for row in self.cursor_ing.fetchall()]

        if not names:
            QMessageBox.information(self, "Пусто", "В базе нет ингредиентов.")
            return

        name, ok = QInputDialog.getItem(
            self, "Удаление ингредиента",
            "Выберите ингредиент для удаления:", names, 0, False)
        if not ok:
            return

        answer = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить «{name}» из базы?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if answer == QMessageBox.StandardButton.Yes:
            self.cursor_ing.execute(
                'DELETE FROM ingredients WHERE name = ?', (name))
            self.conn_ing.commit()
            QMessageBox.information(self, "Готово", "Ингредиент удалён.")

    def closeEvent(self, w):
        self.conn_forms.close()
        self.conn_ing.close()
        w.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CakeCalculator()
    window.show()
    sys.exit(app.exec())
