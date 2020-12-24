import os
import json


class JsonStorage:
    def __init__(self, dir, default=0):
        self.dir = dir
        self.default = default
        if not os.path.exists(dir):
            os.mkdir(dir)

    def get(self, vk_id, key):
        data, fn, fp = self.get_data(vk_id)
        if data is None or key not in data:
            return None
        else:
            return data[key]

    def set(self, vk_id, key, value):
        data, fn, fp = self.get_data(vk_id)
        if data is None:
            data, fn, fp = self.create_user(vk_id)
        data[key] = value
        with open(fp, "w") as jf:
            json.dump(data, jf)
        return 1

    def get_data(self, vk_id):
        fn, fp = self.get_f(vk_id)
        if fn not in os.listdir(self.dir):
            return self.create_user(vk_id)
        else:
            with open(fp, 'r') as jf:
                data = json.load(jf)
                return data, fn, fp

    def get_f(self, vk_id):
        fn = str(vk_id) + ".json"
        fp = os.path.join(self.dir, fn)
        return fn, fp

    def create_user(self, vk_id):
        fn, fp = self.get_f(vk_id)
        data = {"state": self.default}
        with open(fp, 'w') as jf:
            json.dump(data, jf)
        return self.get_data(vk_id)


class User:
    def __init__(self, vk_id, storage):
        self.vk_id = vk_id
        self.storage = storage

    def __getitem__(self, key):
        return self.storage.get(self.vk_id, key)

    def __setitem__(self, key, value):
        self.storage.set(self.vk_id, key, value)

    def keys(self):
        return self.storage.get_data(self.vk_id)[0].keys()
