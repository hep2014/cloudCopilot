import json
import yaml
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class Endpoint(BaseModel):
    path: str
    method: str
    summary: Optional[str]
    operation_id: Optional[str]
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Any]


class OpenAPISpec(BaseModel):
    raw: Dict[str, Any]

    def get_paths(self) -> Dict[str, Any]:
        return self.raw.get("paths", {})

    def get_components(self) -> Dict[str, Any]:
        return self.raw.get("components", {})


class OpenAPIParser:
    def __init__(self, data: Dict[str, Any]):
        self.spec = OpenAPISpec(raw=data)

    @staticmethod
    def load_from_file(path: str) -> "OpenAPIParser":
        if path.endswith(".json"):
            with open(path, "r") as f:
                data = json.load(f)
        else:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
        return OpenAPIParser(data)

    @staticmethod
    def load_from_string(raw: str) -> "OpenAPIParser":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = yaml.safe_load(raw)
        return OpenAPIParser(data)

    def list_endpoints(self) -> List[Dict[str, Any]]:
        result = []
        paths = self.spec.get_paths()

        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                    continue

                entry = {
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary"),
                    "operationId": details.get("operationId"),
                    "parameters": details.get("parameters", []),
                    "requestBody": details.get("requestBody"),
                    "responses": details.get("responses", {}),
                }
                result.append(entry)

        return result

    def list_structured_endpoints(self) -> List[Endpoint]:
        eps = []
        for ep in self.list_endpoints():
            eps.append(
                Endpoint(
                    path=ep["path"],
                    method=ep["method"],
                    summary=ep.get("summary"),
                    operation_id=ep.get("operationId"),
                    parameters=ep.get("parameters", []),
                    request_body=ep.get("requestBody"),
                    responses=ep.get("responses", {}),
                )
            )
        return eps

    def resolve_ref(self, ref: str) -> Dict[str, Any]:
        parts = ref.lstrip("#/").split("/")
        node = self.spec.raw
        for part in parts:
            node = node.get(part)
            if node is None:
                raise ValueError(f"Invalid $ref path: {ref}")
        return node

    def get_path_parameters(self, endpoint: Endpoint) -> List[Dict[str, Any]]:
        return [p for p in endpoint.parameters if p.get("in") == "path"]

    def get_query_parameters(self, endpoint: Endpoint) -> List[Dict[str, Any]]:
        return [p for p in endpoint.parameters if p.get("in") == "query"]

    def _resolve_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        if not schema:
            return schema

        if "$ref" in schema:
            resolved = self.resolve_ref(schema["$ref"])
            return self._resolve_schema(resolved)

        if schema.get("type") == "array":
            items = schema.get("items", {})
            if "$ref" in items:
                resolved_items = self.resolve_ref(items["$ref"])
                schema["items"] = self._resolve_schema(resolved_items)
            else:
                schema["items"] = self._resolve_schema(items)
            return schema

        if schema.get("type") == "object":
            props = schema.get("properties", {})
            for name, sub in props.items():
                schema["properties"][name] = self._resolve_schema(sub)

        # oneOf / anyOf lists
        if "oneOf" in schema:
            schema["oneOf"] = [self._resolve_schema(s) for s in schema["oneOf"]]

        if "anyOf" in schema:
            schema["anyOf"] = [self._resolve_schema(s) for s in schema["anyOf"]]

        return schema

    def get_response_schema(self, endpoint: Endpoint, status_code: str = "200") -> Optional[Dict[str, Any]]:
        responses = endpoint.responses
        if status_code not in responses:
            return None

        content = responses[status_code].get("content", {})
        app_json = content.get("application/json", {})
        schema = app_json.get("schema")

        if not schema:
            return None

        return self._resolve_schema(schema)

    def get_request_schema(self, endpoint: Endpoint) -> Optional[Dict[str, Any]]:
        if not endpoint.request_body:
            return None

        content = endpoint.request_body.get("content", {})
        app_json = content.get("application/json", {})
        schema = app_json.get("schema")

        if not schema:
            return None

        return self._resolve_schema(schema)

    def extract_schema_fields(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        if not schema:
            return {
                "fields": [],
                "required": [],
                "uuid_fields": [],
                "enum_fields": {}
            }

        properties = schema.get("properties", {})
        required = schema.get("required", [])

        fields = list(properties.keys())

        uuid_fields = [
            name for name, info in properties.items()
            if info.get("format") == "uuid"
        ]

        enum_fields = {
            name: info["enum"]
            for name, info in properties.items()
            if "enum" in info
        }

        return {
            "fields": fields,
            "required": required,
            "uuid_fields": uuid_fields,
            "enum_fields": enum_fields,
        }

    def parse_endpoints(self) -> List[Endpoint]:
        endpoints = []
        paths = self.spec.get_paths()

        for path, methods in paths.items():
            for method, details in methods.items():
                # Пропускаем не-HTTP методы
                if method.lower() not in ["get", "post", "put", "patch", "delete"]:
                    continue

                endpoint = Endpoint(
                    path=path,
                    method=method.upper(),
                    summary=details.get("summary"),
                    operation_id=details.get("operationId"),
                    parameters=details.get("parameters", []),  # List[Dict]
                    request_body=details.get("requestBody"),  # Dict or None
                    responses=details.get("responses", {}),  # Dict[str, Any]
                )

                endpoints.append(endpoint)

        return endpoints

    def get_error_schema(self, endpoint: Endpoint, status_code: str) -> Optional[Dict[str, Any]]:
        resp = endpoint.responses.get(status_code)
        if not resp:
            return None

        content = resp.get("content", {})
        app_json = content.get("application/json", {})
        schema = app_json.get("schema")

        if not schema:
            return None

        # Если ошибка через $ref
        if "$ref" in schema:
            return self._resolve_schema(schema)

        return self._resolve_schema(schema)