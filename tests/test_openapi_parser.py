from backend.app.services.openapi_parser import OpenAPIParser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # cloudHackaton/
DATA_PATH = PROJECT_ROOT / "tests" / "data" / "openapi_sample.yaml"

def test_load_from_string():
    raw = """
    openapi: 3.0.0
    paths: {}
    """
    parser = OpenAPIParser.load_from_string(raw)
    assert parser.spec.raw["openapi"] == "3.0.0"

def test_parse_endpoints_from_file():
    parser = OpenAPIParser.load_from_file(str(DATA_PATH))
    endpoints = parser.parse_endpoints()

    assert len(endpoints) == 2

    paths = {ep.path for ep in endpoints}
    assert "/v3/vms" in paths
    assert "/v3/vms/{vm_id}" in paths

    methods = {ep.method for ep in endpoints}
    assert "GET" in methods

def test_resolve_ref():
    parser = OpenAPIParser.load_from_file(str(DATA_PATH))

    vm_schema = parser.resolve_ref("#/components/schemas/VM")

    assert vm_schema["type"] == "object"
    assert "properties" in vm_schema
    assert "id" in vm_schema["properties"]

def test_get_response_schema_list():
    parser = OpenAPIParser.load_from_file(str(DATA_PATH))

    ep_list = [ep for ep in parser.parse_endpoints() if ep.path == "/v3/vms"][0]
    schema = parser.get_response_schema(ep_list)

    assert schema["type"] == "array"
    assert "items" in schema
    assert schema["items"]["type"] == "object"
    assert "id" in schema["items"]["properties"]

def test_get_response_schema_single():
    parser = OpenAPIParser.load_from_file(str(DATA_PATH))

    ep = [ep for ep in parser.parse_endpoints() if ep.path == "/v3/vms/{vm_id}"][0]
    schema = parser.get_response_schema(ep)

    assert schema["type"] == "object"
    assert "id" in schema["properties"]
    assert schema["properties"]["id"]["format"] == "uuid"

def test_extract_schema_fields():
    parser = OpenAPIParser.load_from_file(str(DATA_PATH))

    ep = [ep for ep in parser.parse_endpoints() if ep.path == "/v3/vms/{vm_id}"][0]
    schema = parser.get_response_schema(ep)
    fields_meta = parser.extract_schema_fields(schema)

    assert fields_meta["required"] == ["id", "name", "status"]
    assert "id" in fields_meta["uuid_fields"]
    assert fields_meta["enum_fields"]["status"] == ["ACTIVE", "STOPPED"]

from backend.app.services.llm_payload_builder import build_llm_payload


def test_payload_builder():
    parser = OpenAPIParser.load_from_file(str(DATA_PATH))
    ep = [ep for ep in parser.parse_endpoints() if ep.path == "/v3/vms/{vm_id}"][0]

    payload = build_llm_payload(parser, ep)

    assert payload["uuid_path_params"] == ["vm_id"]
    assert payload["negative_cases"]["supports_404"] is True
    assert payload["negative_cases"]["invalid_uuid"] is True
