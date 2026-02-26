import csv
import json
import uuid
import random
import string
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs
from workers import WorkerEntrypoint, Response


def json_response(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        headers={"content-type": "application/json; charset=utf-8"},
    )


def html_response(html_content, status=200):
    return Response(
        html_content,
        status=status,
        headers={"content-type": "text/html; charset=utf-8"},
    )


csv_path = Path(__file__).with_name("comuni.csv")
docs_path = Path(__file__).with_name("docs.html")

with open(csv_path, "r", encoding="utf-8") as file:
    rows = list(csv.reader(file))

with open(docs_path, "r", encoding="utf-8") as file:
    docs_html = file.read()

by_comune = {row[0]: row[1] for row in rows}
by_codice = {row[1]: row[0] for row in rows}


def handle_request(request):
    parsed_url = urlparse(str(request.url))
    path = unquote(parsed_url.path)
    query = parse_qs(parsed_url.query)

    if path == "/" or path == "/docs":
        return html_response(docs_html)

    # --- API: Codice Catastale ---
    if path == "/comune":
        return json_response(by_comune)

    if path == "/codiceCatastale":
        return json_response(by_codice)

    if path.startswith("/comune/"):
        comune = path[len("/comune/") :]
        nome = comune.title()
        codice = by_comune.get(nome)
        return json_response({"nome": nome if codice else comune, "codiceCatastale": codice})

    if path.startswith("/codiceCatastale/"):
        codice = path[len("/codiceCatastale/") :].upper()
        nome = by_codice.get(codice)
        return json_response({"nome": nome, "codiceCatastale": codice})

    # --- API: UUID Generator ---
    if path == "/api/uuid":
        try:
            count = int(query.get("count", ["1"])[0])
        except ValueError:
            count = 1
        count = min(max(1, count), 100)
        uuids = [str(uuid.uuid4()) for _ in range(count)]
        return json_response({"uuids": uuids if count > 1 else uuids[0], "count": count})

    # --- API: Password Generator ---
    if path == "/api/password":
        try:
            length = int(query.get("length", ["12"])[0])
        except ValueError:
            length = 12
        length = min(max(4, length), 128)
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        pwd = "".join(random.choice(chars) for _ in range(length))
        return json_response({"password": pwd, "length": length})

    # --- API: Text Analyzer ---
    if path == "/api/text":
        text = query.get("text", [""])[0]
        words = len(text.split()) if text else 0
        chars = len(text)
        chars_no_spaces = len(text.replace(" ", ""))
        is_palindrome = False
        if text:
            clean_text = "".join(c.lower() for c in text if c.isalnum())
            is_palindrome = clean_text == clean_text[::-1] and len(clean_text) > 0
            
        return json_response({
            "text": text,
            "words": words,
            "characters": chars,
            "characters_no_spaces": chars_no_spaces,
            "is_palindrome": is_palindrome
        })

    # --- API: Lancio Dadi ---
    if path == "/api/dice":
        try:
            faces = int(query.get("faces", ["6"])[0])
        except ValueError:
            faces = 6
        faces = max(2, faces)
        result = random.randint(1, faces)
        return json_response({"result": result, "faces": faces})

    return json_response({"errore": "Not found"}, 404)


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return handle_request(request)
