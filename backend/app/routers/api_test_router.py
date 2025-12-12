from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.openapi_parser import OpenAPIParser
from app.services.llm_payload_builder import build_llm_payload
from app.services.api_test_generator import generate_api_test
from app.services.api_manual_test_generator import generate_api_manual_test
from app.services.test_validators import (
    validate_pytest_api,
    validate_manual_test
)
router = APIRouter()


class ApiTestRequest(BaseModel):
    openapi: str
    endpoint_path: str
    method: str = "GET"


@router.post("/llm/generate-api-test")
async def generate_api_test_handler(req: ApiTestRequest):
    try:
        parser = OpenAPIParser.load_from_string(req.openapi)

        endpoints = parser.parse_endpoints()
        ep = next(
            (e for e in endpoints
             if e.path == req.endpoint_path
             and e.method == req.method.upper()),
            None
        )

        if not ep:
            raise HTTPException(
                status_code=404,
                detail=f"Эндпоинт {req.method} {req.endpoint_path} не найден."
            )

        payload = build_llm_payload(parser, ep)
        code = generate_api_test(payload)
        validation = validate_pytest_api(code)
        return {"code": code, "validation": validation}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации теста: {str(e)}"
        )

@router.post("/llm/generate-api-manual-test")
async def generate_api_manual_test_handler(req: ApiTestRequest):
    try:
        parser = OpenAPIParser.load_from_string(req.openapi)
        endpoints = parser.parse_endpoints()

        ep = next(
            (e for e in endpoints
             if e.path == req.endpoint_path
             and e.method == req.method.upper()),
            None
        )

        if not ep:
            raise HTTPException(
                status_code=404,
                detail=f"Эндпоинт {req.method} {req.endpoint_path} не найден."
            )

        payload = build_llm_payload(parser, ep, mode="manual")

        code = generate_api_manual_test(payload)
        validation = validate_manual_test(code)
        return {"code": code, "validation": validation}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации manual API теста: {str(e)}"
        )
