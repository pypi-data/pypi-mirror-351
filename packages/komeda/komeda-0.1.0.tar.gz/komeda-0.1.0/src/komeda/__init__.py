import os
import yaml

MENUS_FILE_PATH = os.path.join(os.path.dirname(__file__), "../config/menus.yaml")

class Komeda:
    pass

class Item(dict):
    def __getattr__(self, name):
        return self.get(name)

def make_method(items):
    return lambda: [Item(item) for item in items]

with open(MENUS_FILE_PATH, "r") as f:
    menus = yaml.load(f, Loader=yaml.FullLoader) or {}

for key, items in menus.items():
    setattr(Komeda, key, make_method(items))
