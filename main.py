from flask import Flask, jsonify
import csv

app = Flask(__name__)
with open('comuni.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    reader = list(reader)

@app.route("/comune")
def all_codici_catastali():
    d = {}
    for row in reader:
        d[row[0]] = row[1]
    return jsonify(d)

@app.route("/codiceCatastale")
def all_comuni():
    d = {}
    for row in reader:
        d[row[1]] = row[0]
    return jsonify(d)

@app.route("/comune/<comune>")
def codice_catastale(comune):
    for row in reader:
        if row[0] == comune.title():
            return jsonify({"nome": row[0], "codiceCatastale": row[1]})
    return jsonify({"nome": comune, "codiceCatastale": None})

@app.route("/codiceCatastale/<codice_catastale>")
def comune(codice_catastale):
    for row in reader:
        if row[1] == codice_catastale.upper():
            return jsonify({"nome": row[0], "codiceCatastale": row[1]})
    return jsonify({"nome": None, "codiceCatastale": codice_catastale})

if __name__ == "__main__":
    app.run()