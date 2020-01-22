import json

def load_secret(fpath):
    with open(str(fpath), 'r', encoding='utf-8') as fp:
        secret = json.load(fp)
    return secret