# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-10-10 14:18:27
import json


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=4)
