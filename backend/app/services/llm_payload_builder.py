from typing import Dict, Any

from app.services.openapi_parser import OpenAPIParser, Endpoint


def build_llm_payload(
    parser: OpenAPIParser,
    endpoint: Endpoint,
    mode: str = "auto"
) -> Dict[str, Any]:

    # --- Основные схемы ---
    response_schema = parser.get_response_schema(endpoint)
    request_schema = parser.get_request_schema(endpoint)

    fields_meta = (
        parser.extract_schema_fields(response_schema)
        if response_schema else {}
    )

    # --- UUID параметры в path ---
    uuid_path_params = [
        param["name"]
        for param in endpoint.parameters
        if param.get("in") == "path"
        and param.get("schema", {}).get("format") == "uuid"
    ]

    # --- Негативные кейсы ---
    negative_cases = {
        "invalid_uuid": bool(uuid_path_params),
        "missing_required_parameters": [
            param["name"]
            for param in endpoint.parameters
            if param.get("required") is True
        ],
        "supports_404": "404" in endpoint.responses
    }

    # --- Ошибки по статус-кодам ---
    error_schemas = {
        code: schema
        for code in ["400", "401", "403", "404", "500"]
        if (schema := parser.get_error_schema(endpoint, code))
    }

    has_exceptions = bool(error_schemas)

    # --- Итоговый payload ---
    return {
        "mode": mode,                          # auto/manual
        "path": endpoint.path,
        "method": endpoint.method,
        "summary": endpoint.summary or "",
        "operation_id": endpoint.operation_id or "",
        "parameters": endpoint.parameters,

        "request_schema": request_schema,
        "response_schema": response_schema,
        "fields_meta": fields_meta,

        "uuid_path_params": uuid_path_params,
        "negative_cases": negative_cases,

        "error_schemas": error_schemas,
        "has_exceptions": has_exceptions,
    }