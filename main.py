import csv
import json
from pathlib import Path
from urllib.parse import urlparse, unquote
from js import Response
from workers import WorkerEntrypoint


def json_response(data, status=200):
    return Response.new(
        json.dumps(data, ensure_ascii=False),
        {
            "status": status,
            "headers": {"content-type": "application/json; charset=utf-8"},
        },
    )


csv_path = Path(__file__).with_name("comuni.csv")

with open(csv_path, "r", encoding="utf-8") as file:
    rows = list(csv.reader(file))

by_comune = {row[0]: row[1] for row in rows}
by_codice = {row[1]: row[0] for row in rows}


def handle_request(request):
    path = unquote(urlparse(str(request.url)).path)

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

    return json_response({"errore": "Not found"}, 404)


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return handle_request(request)
