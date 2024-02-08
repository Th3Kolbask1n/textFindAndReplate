import os
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QFileDialog

class TranslationApp(QWidget):
    def __init__(self):
        super().__init__()

        self.target_directory = ""
        self.files_to_process = []

        self.current_file_index = 0
        self.current_line_index = 0

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.path_label = QLabel("Укажите путь к папке:")
        layout.addWidget(self.path_label)

        self.path_edit = QLineEdit()
        layout.addWidget(self.path_edit)

        self.browse_button = QPushButton("Обзор")
        self.browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_button)

        self.file_info_label = QLabel()
        layout.addWidget(self.file_info_label)

        self.before_label = QLabel("Строка до обработки:")
        layout.addWidget(self.before_label)

        self.before_textedit = QTextEdit()
        self.before_textedit.setReadOnly(True)
        layout.addWidget(self.before_textedit)

        self.after_label = QLabel("Строка после обработки:")
        layout.addWidget(self.after_label)

        self.after_textedit = QTextEdit()
        self.after_textedit.setReadOnly(True)
        layout.addWidget(self.after_textedit)

        self.replace_button = QPushButton("Заменить")
        self.replace_button.clicked.connect(self.replace)
        layout.addWidget(self.replace_button)

        self.next_button = QPushButton("Следующая")
        self.next_button.clicked.connect(self.process_next)
        layout.addWidget(self.next_button)

        self.setLayout(layout)

        self.setWindowTitle('Translator App')
        self.show()

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder_path:
            self.target_directory = folder_path
            self.path_edit.setText(folder_path)
            self.find_files()
            self.update_label()

    def find_files(self):
        self.files_to_process = []
        for root, dirs, files in os.walk(self.target_directory):
            for file in files:
                file_path = os.path.join(root, file)
                if self.file_contains_russian_strings(file_path):
                    self.files_to_process.append(file_path)

    def file_contains_russian_strings(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Используем регулярное выражение для поиска русских строк в кавычках
        russian_strings = [match.group(1) for line in lines for match in re.finditer(r'\"([^\"]*[А-я]+[^\"]*)\"', line) if match.group(1).strip()]
        return bool(russian_strings)

    def contains_tr(self, line):
        return 'tr(' in line

    def replace(self):
        if self.current_file_index < len(self.files_to_process):
            file_path = self.files_to_process[self.current_file_index]
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            before_lines = []
            after_lines = []

            # Используем регулярное выражение для поиска русских строк в кавычках
            russian_strings = [match.group(1) for line in lines for match in re.finditer(r'\"([^\"]*[А-я]+[^\"]*)\"', line) if match.group(1).strip()]

            if self.current_line_index < len(russian_strings):
                current_russian_str = russian_strings[self.current_line_index]

                # Находим номера строк с русской строкой
                line_numbers = [i+1 for i, line in enumerate(lines) if f'"{current_russian_str}"' in line]

                for line_number in line_numbers:
                    # Проверяем, что в строке еще нет tr()
                    if not self.contains_tr(lines[line_number - 1]):
                        # Заменяем все вхождения фразы в кавычках на tr("фраза")
                        modified_line = lines[line_number - 1]
                        modified_line = self.replace_russian_strings(modified_line)

                        # Отображаем строки до и после обработки
                        before_lines.append(lines[line_number - 1].strip())
                        after_lines.append(modified_line.strip())

                        # Заменяем оригинальную строку в списке
                        lines[line_number - 1] = modified_line

                self.before_textedit.setPlainText("\n".join(before_lines))
                self.after_textedit.setPlainText("\n".join(after_lines))

            # Записываем изменения в файл
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)

    def replace_russian_strings(self, line):
        def replace(match):
            return f'tr("{match.group(1)}")'

        return re.sub(r'\"([^\"]*[А-я]+[^\"]*)\"', replace, line)

    def process_next(self):
        self.current_line_index += 1
        self.update_label()

    def update_label(self):
        while self.current_file_index < len(self.files_to_process):
            file_path = self.files_to_process[self.current_file_index]
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            before_lines = []
            after_lines = []

            # Используем регулярное выражение для поиска русских строк в кавычках
            russian_strings = [match.group(1) for line in lines for match in re.finditer(r'\"([^\"]*[А-я]+[^\"]*)\"', line) if match.group(1).strip()]

            if russian_strings and self.current_line_index < len(russian_strings):
                current_file = os.path.basename(file_path)
                current_russian_str = russian_strings[self.current_line_index]

                # Находим номера строк с русской строкой
                line_numbers = [i+1 for i, line in enumerate(lines) if f'"{current_russian_str}"' in line]
                original_line_number = line_numbers[0] if line_numbers else 0
                if original_line_number > 0:
                    # Отображаем строки до и после обработки
                    before_lines.append(lines[original_line_number - 1].strip())
                    after_lines.append(self.replace_russian_strings(lines[original_line_number - 1]).strip())

                    self.before_textedit.setPlainText("\n".join(before_lines))
                    self.after_textedit.setPlainText("\n".join(after_lines))

                    self.file_info_label.setText(f"Файл: {current_file}, Строка: {original_line_number}")
                    break
                else:
                    self.current_file_index += 1
                    self.current_line_index = 0
            else:
                self.current_file_index += 1

        if self.current_file_index >= len(self.files_to_process):
            self.file_info_label.clear()
            self.before_textedit.clear()
            self.after_textedit.clear()
            self.current_file_index = 0
            self.current_line_index = 0

if __name__ == "__main__":
    app = QApplication([])
    translator_app = TranslationApp()
    app.exec_()