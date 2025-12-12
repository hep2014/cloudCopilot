from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.llm_service import generate_allure_manual_testcase
from app.services.ui_e2e_test_generator import generate_ui_e2e_test
from app.services.test_validators import (
    validate_manual_test,
    validate_e2e_test,
)
router = APIRouter()

class ManualTestRequest(BaseModel):
    requirements: str = Field(
        ...,
        description="Описание функционала / сценария, по которому нужно сгенерировать manual-тест",
        example="Проверка сложения двух чисел в UI калькуляторе",
        min_length=1,
        max_length=20000,
    )

class UiE2ERequest(BaseModel):
    requirements: str


@router.post("/llm/manual-test")
async def generate_manual_test(request: ManualTestRequest):
    """
    Новая ручка — генерация manual-теста в формате Allure TestOps as Code.
    """
    try:
        code = generate_allure_manual_testcase(request.requirements)
        validation = validate_manual_test(code)
        return {"code": code, "validation": validation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка модели: {str(e)}")

@router.post("/llm/generate-ui-e2e-test")
async def generate_ui_e2e_test_handler(req: UiE2ERequest):
    try:
        code = generate_ui_e2e_test(req.requirements)
        validation = validate_e2e_test(code)
        return {"code": code, "validation": validation}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации e2e теста: {str(e)}"
        )
# Новые модели запросов для массовой генерации
class BulkManualTestRequest(BaseModel):
    requirements: str
    count: int = Field(15, ge=1, le=50, description="Количество тестов для генерации")

class BulkApiTestRequest(BaseModel):
    openapi: str
    endpoint_path: str
    method: str = "GET"
    count: int = Field(15, ge=1, le=50, description="Количество тестов для генерации")

@router.post("/llm/bulk-manual-tests")
async def generate_bulk_manual_tests(request: BulkManualTestRequest):
    """
    Генерирует N ручных тестов для калькулятора (циклический вызов).
    """
    results = []
    for i in range(request.count):
        try:
            code = generate_allure_manual_testcase(request.requirements)
            validation = validate_manual_test(code)
            results.append({"test_number": i+1, "code": code, "validation": validation})
        except Exception as e:
            results.append({"test_number": i+1, "error": str(e)})
    return {"generated_tests": len(results), "results": results}

@router.post("/llm/bulk-api-tests")
async def generate_bulk_api_tests(request: BulkApiTestRequest):
    """
    Генерирует N API-тестов для указанного эндпоинта.
    """
    from backend.app.services.openapi_parser import OpenAPIParser
    from backend.app.services.llm_payload_builder import build_llm_payload
    from backend.app.services.api_test_generator import generate_api_test
    from backend.app.services.test_validators import validate_pytest_api

    results = []
    try:
        parser = OpenAPIParser.load_from_string(request.openapi)
        endpoints = parser.parse_endpoints()
        ep = next(
            (e for e in endpoints
             if e.path == request.endpoint_path
             and e.method == request.method.upper()),
            None
        )
        if not ep:
            raise HTTPException(status_code=404, detail="Эндпоинт не найден")

        payload = build_llm_payload(parser, ep)
        for i in range(request.count):
            try:
                code = generate_api_test(payload)
                validation = validate_pytest_api(code)
                results.append({"test_number": i+1, "code": code, "validation": validation})
            except Exception as e:
                results.append({"test_number": i+1, "error": str(e)})
        return {"generated_tests": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
