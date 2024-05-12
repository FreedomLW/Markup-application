import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QMessageBox, QStackedLayout
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView 
from functools import partial
import os

import json
import random
import difflib
from difflib import HtmlDiff
from bs4 import BeautifulSoup

class TextReaderApp(QMainWindow):
    def __init__(self, json_file, output_json_file):
        super().__init__()
        self.json_file = json_file
        self.output_json_file = output_json_file
        self.texts = []
        self.dataset = []
        self.current_index = 0

        self.load_texts_from_json()

        random.seed(666)
        #random.shuffle(self.texts)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.problem_statement_label = QLabel()
        self.layout.addWidget(self.problem_statement_label)

        self.textedit = QTextEdit()
        self.layout.addWidget(self.textedit)

        self.answer_textedit = QTextEdit()
        self.answer_textedit.setPlaceholderText("Write your answer here")
        self.layout.addWidget(self.answer_textedit)
        self.answer_textedit.setPlainText("### Hints:\n1.\n2.")
        
        self.hint_place = QLabel()
        self.layout.addWidget(self.hint_place)
        self.hint_place.hide()

        self.button_texts = [
            "1. Bad answer",
            "2. So so",
            "3. Good answer"
        ]

        self.map_hint_to_type = {
            1 : 'zero-shot',
            2 : 'few-shot',
            3 : 'CoT',
            4 : 'self-reflection',
            5 : 'CoT_test',
            6 : 'self-reflection_test'
        }

        self.buttons = []
        for iter, text in enumerate(self.button_texts):
            button = QPushButton(text)
            self.buttons.append(button)
            button.clicked.connect(partial(self.save_response, iter))
            self.layout.addWidget(button)
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_answer)
        self.layout.addWidget(self.submit_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back)
        self.layout.addWidget(back_button)
        self.layout_iter = 0
        self.load_text()

    def back(self):
        if self.layout_iter == 0:
            if self.current_index != 0:
                self.current_index -= 1
                self.layout_iter = 6
        else:
            self.layout_iter -= 1
        self.load_text()

    def submit_answer(self):
        answer = self.answer_textedit.toPlainText()
        self.texts[self.current_index]['current_answer'] = answer
        self.load_next_stage()

    def save_response(self, iter):
        dataset_iter = self.texts[self.current_index]['dataset_iter']
        code_iter = self.texts[self.current_index]['code_iter']
        self.output_dataset[dataset_iter]['generated_hints'][self.map_hint_to_type[self.layout_iter]][code_iter]['mark'] = iter + 1
        self.load_next_stage()

    def save_answer(self):
        answer = self.answer_textedit.toPlainText()
        dataset_iter = self.texts[self.current_index]['dataset_iter']
        code_iter = self.texts[self.current_index]['code_iter']
        n = len(self.dataset[dataset_iter]['data_for_test'])

        if 'reference_answers' not in self.output_dataset[dataset_iter].keys():
            self.output_dataset[dataset_iter]['reference_answers'] = ["" for _ in range(n)]
        self.output_dataset[dataset_iter]["reference_answers"][code_iter] = answer
        self.texts[self.current_index]['current_answer'] = answer
        with open(self.output_json_file, 'w') as f:
            json.dump(self.output_dataset, f, indent=3)

    def load_next_stage(self):
        self.layout_iter += 1
        if self.layout_iter >= 7:
            self.save_answer()
            self.layout_iter = 0
            self.current_index += 1
        self.load_text()

    def load_text(self):
        start_iter = self.current_index
        for self.current_index in range(start_iter, len(self.texts)):
            if 'reference_answers' in self.texts[self.current_index]: 
                continue
            else: break
        else:
            QMessageBox.information(self, "Texts Finished", "All texts have been processed.")
            self.close()
            exit()
        
        if self.layout_iter == 0:
            if 'current_answer' in self.texts[self.current_index]:
                self.answer_textedit.setPlainText(self.texts[self.current_index]['current_answer'])
            else:
                self.answer_textedit.setPlainText("### Hints:\n1.\n2.")

        code1 = self.texts[self.current_index]["student_code"].split('\n')
        code2 = self.texts[self.current_index]["student_solution"].split('\n')
        difference = difflib.HtmlDiff(tabsize=2).make_table(code1, code2, numlines=10)

        soup = BeautifulSoup(difference, 'html.parser')
        left_column_cells = soup.select('tr td:nth-child(3)')

        for cell in left_column_cells:

            if cell.contents and cell.contents[0].name == 'span' and ('diff_sub' in cell.contents[0].get('class', [])):
                cell['style'] = 'background-color: rgba(255, 0, 0, 0.3);'

            if cell.contents:
                for content in cell.contents:
                    if content.name == 'span' and 'diff_chg' in content.get('class', []):
                        cell['style'] = 'background-color: rgba(255, 255, 0, 0.3);'
                        #content['style'] = 'color: rgba(255, 255, 0, 0.3);'
        right_column_cells = soup.select('tr td:nth-child(6)')

        for cell in right_column_cells:
            if cell.contents and cell.contents[0].name == 'span' and 'diff_add' in cell.contents[0].get('class', []):
                cell['style'] = 'background-color: rgba(0, 255, 0, 0.3);'
            
            if cell.contents:
                for content in cell.contents:
                    if content.name == 'span' and 'diff_chg' in content.get('class', []):
                        cell['style'] = 'background-color: rgba(255, 255, 0, 0.3);'
                        #content['style'] = 'color: rgba(255, 255, 0, 0.3);'

        difference = str(soup)
        difference = f'<style>td {{ padding: 0px 20px; }}</style>{difference}'
        
        self.textedit.setHtml(difference)

        problem_statement = self.texts[self.current_index]['problem_statement'] + '\n' + self.texts[self.current_index]['problem_constraints']
        self.problem_statement_label.setText(problem_statement)

        # Show/hide components based on layout iteration
        if self.layout_iter == 0:
            [button.hide() for button in self.buttons]
            self.submit_button.show()
            self.answer_textedit.show()
            self.hint_place.hide()
        elif self.layout_iter in [1, 2, 3, 4, 5, 6]:
            [button.show() for button in self.buttons]
            self.submit_button.hide()
            self.answer_textedit.hide()
            self.hint_place.show()

            # Update hint text based on layout iteration
            hint_key = f'hint_{self.layout_iter}'
            if hint_key in self.texts[self.current_index]:
                self.hint_place.setText(self.texts[self.current_index][hint_key])
    
    def load_texts_from_json(self):

        if not os.path.exists(self.output_json_file):
            print(f'Output file does not exist. The data will be saved to {self.output_json_file}')
            with open(self.json_file, 'r') as file:
                self.dataset = json.load(file)
            self.output_dataset = self.dataset
        else:
            print(f"Output file exists. Load data from {self.output_json_file}")
            with open(self.output_json_file, 'r') as f:
                self.output_dataset = json.load(f)
            self.dataset = self.output_dataset

        for j, data in enumerate(self.dataset):
            for i in range(len(data['data_for_test'])):
                self.texts.append({
                    'dataset_iter': j,
                    'code_iter': i,
                    'student_code': data['data_for_test'][i]['code'].replace('\r', ''),
                    'student_solution': data['info_for_model'][i]['code'].replace('\r', ''),
                    'problem_statement': data['problem_statement'],
                    'problem_constraints': data['problem_constraints'],
                    'hint_1': data['generated_hints']['zero-shot'][i]['model_answer'],
                    'hint_2': data['generated_hints']['few-shot'][i]['model_answer'],
                    'hint_3': data['generated_hints']['CoT'][i]['model_answer'],
                    'hint_4': data['generated_hints']['self-reflection'][i]['model_answer'],
                    'hint_6': data['generated_hints']['self-reflection_test'][i]['model_answer'],
                    'hint_5': data['generated_hints']['CoT_test'][i]['model_answer'],
                })
                if 'reference_answers' in data.keys():
                    if data['reference_answers'][i] != '':
                        self.texts[-1]['reference_answers'] = data['reference_answers'][i]

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename",
                    help="write report to FILE", metavar="FILE")
parser.add_argument("-of", "--out_file", dest="output_filename",
                    help="write report to FILE", metavar="OUTPUT FILE")
args = parser.parse_args()

def main():
    json_file = args.filename
    output_json_file = args.output_filename
    app = QApplication(sys.argv)
    window = TextReaderApp(json_file, output_json_file)
    window.setWindowTitle("Text Reader Application")
    window.setGeometry(100, 100, 1200, 1000)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
