import re


def validate_manual_test(code: str) -> dict:
    result = {
        "is_python": False,
        "imports_ok": False,
        "has_class": False,
        "has_allure_manual": False,
        "has_mark_manual": False,
        "has_steps": False,
        "aaa_ok": False,
        "errors": []
    }

    # Похоже ли на Python
    if re.search(r"^\s*(import|from)\s+", code):
        result["is_python"] = True
    else:
        result["errors"].append("Код не похож на Python (нет import/from).")

    # Импорты allure + mark
    if "import allure" in code and "from pytest import mark" in code:
        result["imports_ok"] = True
    else:
        result["errors"].append("Не найдены импорты allure или mark.")

    # Класс
    if re.search(r"class\s+\w+", code):
        result["has_class"] = True
    else:
        result["errors"].append("Не найден класс теста.")

    # @allure.manual
    if "@allure.manual" in code:
        result["has_allure_manual"] = True
    else:
        result["errors"].append("Нет аннотации @allure.manual.")

    # @mark.manual
    if "@mark.manual" in code:
        result["has_mark_manual"] = True
    else:
        result["errors"].append("Нет аннотации @mark.manual.")

    # Шаги allure.step
    if "with allure.step" in code:
        result["has_steps"] = True
    else:
        result["errors"].append("Нет шагов с with allure.step.")

    # AAA (может быть либо по текстам, либо по step)
    if (
        "Arrange" in code and
        "Act" in code and
        "Assert" in code
    ) or "with allure.step" in code:
        result["aaa_ok"] = True
    else:
        result["errors"].append("Нет AAA-паттерна.")

    return result

def validate_e2e_test(code: str) -> dict:
    result = {
        "is_python": False,
        "imports_ok": False,
        "has_test_fn": False,
        "uses_playwright": False,
        "aaa_ok": False,
        "no_markdown": False,
        "errors": []
    }

    # Python-подобность
    if re.search(r"^\s*(import|from)\s+", code):
        result["is_python"] = True
    else:
        result["errors"].append("Код не похож на Python.")

    # Импорты playwright
    if "from playwright.sync_api" in code:
        result["imports_ok"] = True
        result["uses_playwright"] = True
    else:
        result["errors"].append("Нет импорта from playwright.sync_api.")

    # def test_...
    if re.search(r"def\s+test_\w+", code):
        result["has_test_fn"] = True
    else:
        result["errors"].append("Нет функции test_.")

    # AAA через комменты
    if "Arrange" in code and "Act" in code and "Assert" in code:
        result["aaa_ok"] = True
    else:
        result["errors"].append("Нет AAA-паттерна.")

    # Markdown
    if "```" not in code:
        result["no_markdown"] = True
    else:
        result["errors"].append("Код содержит Markdown-разметку ```.")

    return result

def validate_pytest_api(code: str) -> dict:
    result = {
        "is_python": False,
        "imports_ok": False,
        "has_fixture": False,
        "has_test_fn": False,
        "aaa_ok": False,
        "no_markdown": False,
        "errors": []
    }

    # Python
    if re.search(r"^\s*(import|from)\s+", code):
        result["is_python"] = True
    else:
        result["errors"].append("Код не похож на Python.")

    # Импорты pytest + httpx
    if "import httpx" in code and "import pytest" in code:
        result["imports_ok"] = True
    else:
        result["errors"].append("Нет import pytest или import httpx.")

    # auth_header fixture
    if re.search(r"@pytest\.fixture", code) and "auth_header" in code:
        result["has_fixture"] = True
    else:
        result["errors"].append("Нет фикстуры @pytest.fixture auth_header.")

    # def test_...
    if re.search(r"def\s+test_\w+", code):
        result["has_test_fn"] = True
    else:
        result["errors"].append("Нет функции test_.")

    # AAA (обычно в комментариях)
    if "Arrange" in code and "Act" in code and "Assert" in code:
        result["aaa_ok"] = True
    else:
        result["errors"].append("Нет AAA-паттерна.")

    # Markdown
    if "```" not in code:
        result["no_markdown"] = True
    else:
        result["errors"].append("Код содержит Markdown-разметку ```.")

    return result
