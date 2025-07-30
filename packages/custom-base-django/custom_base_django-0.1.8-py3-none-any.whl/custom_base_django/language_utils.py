import json
from django.conf import settings
lang_json = dict()

def load_language(lang=''):
    global lang_json
    lang = lang or getattr(settings, 'SITE_LANGUAGE', 'fa')
    try:
        with open(f'static/local/lang/{lang}.json', encoding='utf8') as f:
            lang_json = json.load(f)
    except:
        lang_json = dict()

def translate(key):
    return lang_json.get(key, key)


load_language()