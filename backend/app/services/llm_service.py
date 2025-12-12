from dotenv import load_dotenv
load_dotenv(".env")

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("CLOUDRU_API_KEY"),
    base_url=os.getenv("CLOUDRU_BASE_URL"),
)

def call_llm(prompt: str) -> str:
    """
    Простая функция — принимает промпт, возвращает чистый текст ответа.
    Все параметры берутся из .env (как в твоём исходном коде).
    """
    response = client.chat.completions.create(
        model=os.getenv("CLOUDRU_MODEL"),
        max_tokens=2500,
        temperature=0.5,
        presence_penalty=0,
        top_p=0.95,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


def generate_allure_manual_testcase(requirements: str) -> str:
    """
    Генерирует один manual-тест в формате Allure TestOps as Code (Python).
    Пока без строгой валидации — просто просим модель выдать код по шаблону.
    """
    prompt = f"""
Ты — опытный QA-инженер. Твоя задача — сгенерировать manual-тест
в формате Allure TestOps as Code (Python). 

Условия: 
1. Тест предназначен ДЛЯ Cloud.ru калькулятора цен.
2. Базовый URL калькулятора:
   https://cloud.ru/calculator 

Требования к тесту (описание сценария на естественном языке):
\"\"\"{requirements}\"\"\"
Ты уделяешь запросу выше приоритетное внимание.

Требуемый формат кода (это ПРИМЕР требуемого ответа):

@allure.manual
@allure.label("owner", "qa_team")
@allure.feature("UI Calculator")
@allure.story("Basic operations")
@allure.suite("manual")
@mark.manual
class TestCalculatorUI:
    @allure.title("Сложение двух чисел")
    @allure.tag("CRITICAL")
    @allure.label("priority", "critical")
    def test_add_two_numbers(self) -> None:
        with allure.step("Arrange: открыть страницу калькулятора"):
            pass
        with allure.step("Act: ввести 2 и 3 и нажать ="):
            pass
        with allure.step("Assert: на экране отображается 5"):
            pass

Важно:
- Выводи ТОЛЬКО чистый Python-код, без Markdown-разметки, без ```python.
- Используй контекстный менеджер allure.step, а не allure_step.
- Добавь необходимые импорты: import allure и from pytest import mark.
- Код должен быть полностью запускаемым без ошибок.
- Не добавляй текст до и после кода.
"""

    return call_llm(prompt)