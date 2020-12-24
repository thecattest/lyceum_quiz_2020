import os
import json


class QR:
    def __init__(self, file):
        self.file = file + ('' if file.endswith('.json') else '.json')
        print(self.file)
        if not os.path.exists(self.file):
            with open(self.file, 'w'):
                pass
        self.codes = self.load()

    def is_correct(self, code):
        return code in self.codes.keys()

    def get_question(self, code):
        if self.is_correct(code):
            question = self.codes[code]
            return question

    def get_links(self):
        return ["https://lycquiz2020.pythonanywhere.com/qr/" + c for c in self.codes]

    def load(self):
        with open(self.file) as file:
            return json.load(file)
