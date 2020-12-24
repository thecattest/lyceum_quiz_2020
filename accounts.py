import json
import os
from secrets import token_urlsafe


class Accounts:
    def __init__(self):
        self.fn = 'codes.json'
        if not os.path.exists(self.fn):
            with open(self.fn, 'w') as file:
                json.dump({}, file)

    def get_code(self, vk_id):
        code = token_urlsafe(18)
        with open(self.fn) as file:
            data = json.load(file)
        data[code] = vk_id
        with open(self.fn, 'w') as file:
            json.dump(data, file)
        return code

    def check_code(self, code):
        with open(self.fn) as file:
            data = json.load(file)
        return data.get(code)
