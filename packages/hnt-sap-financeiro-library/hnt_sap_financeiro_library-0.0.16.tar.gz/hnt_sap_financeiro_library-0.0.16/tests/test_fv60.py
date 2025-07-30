import json
from hnt_sap_financeiro.hnt_sap_gui import SapGui


def test_create():
    with open("./devdata/json/lancamento_taxa_FIN-48514.json", "r", encoding="utf-8") as payload_json: payload = json.load(payload_json)
    taxa = payload['payloads'][0]['taxa']
    result = SapGui().run_FV60(taxa)
    assert result['error'] is None

def test_create_52009():
    with open("./devdata/json/lancamento_taxa_FIN-52009.json", "r", encoding="utf-8") as payload_json: payload = json.load(payload_json)
    taxa = payload['payloads'][0]['taxa']
    result = SapGui().run_FV60(taxa)
    assert result['error'] is None

def test_create_52073():
    with open("./devdata/json/lancamento_taxa_FIN-52073.json", "r", encoding="utf-8") as payload_json: payload = json.load(payload_json)
    taxa = payload['payloads'][0]['taxa']
    result = SapGui().run_FV60(taxa)
    assert result['error'] is None

def test_create_52295():
    with open("./devdata/json/lancamento_taxa_FIN-52295.json", "r", encoding="utf-8") as payload_json: payload = json.load(payload_json)
    taxa = payload['payloads'][0]['taxa']
    result = SapGui().run_FV60(taxa)
    assert result['error'] is None

def test_create_52370():
    with open("./devdata/json/lancamento_taxa_FIN-52370.json", "r", encoding="utf-8") as payload_json: payload = json.load(payload_json)
    taxa = payload['payloads'][0]['taxa']
    result = SapGui().run_FV60(taxa)
    assert result['error'] is None