from flask import Flask, jsonify, render_template
from suggest import suggest, suggest_list
import requests
import os
import re

app = Flask(__name__)

MW_KEY = os.getenv('MW_API_KEY')
MW_URL = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={key}'


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/suggest/word/<input_word>.json')
def word_suggest(input_word):
    return jsonify(suggest(input_word))


@app.route('/suggest/list/<input_word>.json')
def list_suggest(input_word):
    return jsonify(suggest_list(input_word))


@app.route('/define/<word>.json')
def get_definition(word):
    word = word.lower()
    def_url = MW_URL.format(word = word, key = MW_KEY)
    res = requests.get(def_url)

    if isinstance(res, list):
        return jsonify(['test'])

    matches = []
    for defn in res.json():
        if not isinstance(defn, dict):  # no result found returns a list of strings
            return jsonify([])
        if not defn['shortdef']:
            continue
        elif (defn['meta']['id']).split(':')[0] == word:
            matches.append(defn)

    if not matches:
        matches = [m for m in res.json() if m['shortdef']]  # fallback on everything with a def

    for m in matches:
        # add a cleaned 'word' to each defn dict
        m['word'] = m['meta']['id'].split(':')[0]

        # cleanup shortdef
        shortdefs = m['shortdef']
        def_str = ''
        for i, sd in enumerate(shortdefs):
            def_str += f'{i+1}. {sd}<br><br>'
        m['definition_str'] = def_str

    return jsonify(matches)
