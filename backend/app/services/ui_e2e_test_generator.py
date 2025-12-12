from app.services.llm_service import call_llm


def prepare_e2e_prompt(requirements: str) -> str:
    return f"""
Ты — Senior QA Automation Engineer.
Твоя задача — сгенерировать корректный e2e автотест на Playwright (Python)
по следующему пользовательскому сценарию:

--- BEGIN REQUIREMENTS ---
{requirements}
--- END REQUIREMENTS ---

‼ Условия:
1. Тест предназначен ДЛЯ Cloud.ru калькулятора цен.
2. Базовый URL калькулятора:
   https://cloud.ru/calculator 
3. Не используй calculator.net.
4. Используй локаторы, основанные на:
   - текстовых кнопках ("Добавить сервис")
   - CSS (#total-price, .product-card)
   - aria-label, placeholder, role

Формат теста:
- только Python-код, без Markdown
- from playwright.sync_api import Page, expect
- AAA-паттерн (Arrange / Act / Assert)
- def test_<описание>(page: Page):

Сгенерируй реальный Playwright тест для Cloud.ru калькулятора.
"""


def generate_ui_e2e_test(requirements: str) -> str:
    prompt = prepare_e2e_prompt(requirements)
    code = call_llm(prompt)
    return code.strip()
