import { useState } from 'react';
import './App.css';

type TestType = 
  | 'manual-ui'
  | 'ui-e2e'
  | 'api-test'
  | 'api-manual'
  | 'bulk-manual'
  | 'bulk-api';

type BackendResponse = {
  code: string;
  validation?: {
    errors?: string[];
    warnings?: string[];
  };
};

function App() {
  const [prompt, setPrompt] = useState('');
  const [selectedTest, setSelectedTest] = useState<TestType>('manual-ui');
  const [result, setResult] = useState<BackendResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [modelStatus, setModelStatus] = useState<'unknown' | 'alive' | 'dead'>('unknown');
  const [showStatusToast, setShowStatusToast] = useState(false);

  const testOptions = [
    { id: 'manual-ui' as TestType, label: 'Ручной UI-тест (калькулятор)' },
    { id: 'ui-e2e' as TestType, label: 'Авто UI E2E-тест (калькулятор)' },
    { id: 'api-test' as TestType, label: 'Авто API-тест (Evolution Compute)' },
    { id: 'api-manual' as TestType, label: 'Ручной API-тест (Evolution Compute)' },
    { id: 'bulk-manual' as TestType, label: 'Массовые ручные тесты (15 штук)' },
    { id: 'bulk-api' as TestType, label: 'Массовые API-тесты (15 штук)' },
  ];

  const checkModel = async () => {
    try {
      const res = await fetch('http://localhost:8000/docs', { method: 'GET' });
      if (res.ok) {
        setModelStatus('alive');
      } else {
        setModelStatus('dead');
      }
    } catch {
      setModelStatus('dead');
    }
    setShowStatusToast(true);
    setTimeout(() => setShowStatusToast(false), 3000);
  };

  const generateTest = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setResult(null);

    const BASE_URL = 'http://localhost:8000';

    // Подготовка payload в зависимости от типа теста
    let endpoint = '';
    let payload: any = { requirements: prompt };

    switch (selectedTest) {
      case 'manual-ui':
        endpoint = '/llm/manual-test';
        break;
      case 'ui-e2e':
        endpoint = '/llm/generate-ui-e2e-test';
        break;
      case 'api-test':
        endpoint = '/llm/generate-api-test';
        // Для API-теста нужна OpenAPI спецификация — временно используем пример
        payload = {
          openapi: `openapi: 3.0.0\ninfo:\n  title: Example API\n  version: 1.0.0\npaths:\n  /test:\n    get:\n      responses:\n        '200':\n          description: OK`,
          endpoint_path: '/test',
          method: 'GET',
        };
        break;
      case 'api-manual':
        endpoint = '/llm/generate-api-manual-test';
        payload = {
          openapi: `openapi: 3.0.0\ninfo:\n  title: Example API\n  version: 1.0.0\npaths:\n  /test:\n    get:\n      responses:\n        '200':\n          description: OK`,
          endpoint_path: '/test',
          method: 'GET',
        };
        break;
      case 'bulk-manual':
        endpoint = '/llm/bulk-manual-tests';
        payload.count = 15;
        break;
      case 'bulk-api':
        endpoint = '/llm/bulk-api-tests';
        payload = {
          openapi: `openapi: 3.0.0\ninfo:\n  title: Example API\n  version: 1.0.0\npaths:\n  /test:\n    get:\n      responses:\n        '200':\n          description: OK`,
          endpoint_path: '/test',
          method: 'GET',
          count: 15,
        };
        break;
      default:
        endpoint = '/llm/manual-test';
    }

    try {
      const response = await fetch(`${BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (error: any) {
      setResult({
        code: `// Ошибка при запросе к бэкенду:\n// ${error.message}\n// Убедитесь, что бэкенд запущен на localhost:8000`,
        validation: { errors: [`Ошибка сети: ${error.message}`] },
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => setPrompt(event.target?.result as string);
      reader.readAsText(file);
    }
  };

  return (
    <div className="container">
      {/* Кнопка проверки модели с вопросиком */}
      <button className="model-check-btn" onClick={checkModel} title="Проверить модель">
        <span style={{ fontSize: '24px', fontWeight: 'bold' }}>?</span>
      </button>

      {/* Уведомление о статусе модели */}
      {showStatusToast && (
        <div className={`status-toast ${modelStatus}`}>
          {modelStatus === 'alive' ? 'Модель доступна' : 'Модель недоступна'}
        </div>
      )}

      <div className="buttons-demo">
        <h1>TestOps Copilot</h1>
        <p>Генератор тестов для Cloud.ru</p>

        {/* Поле для промта */}
        <div className="input-section">
          <label htmlFor="prompt">Описание теста (промт):</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Опиши сценарий теста..."
            rows={6}
          />
        </div>

        {/* Загрузка файла */}
        <div className="file-upload-wrapper">
          <input
            type="file"
            id="file-upload"
            accept=".yaml,.yml,.txt"
            onChange={handleFileUpload}
            hidden
          />
          <label htmlFor="file-upload" className="button button--outline">
            <svg className="button-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M16.5 2H12.71C12.09 2 11.5 2.35 11.21 2.88L10.46 4.12C10.17 4.65 9.58 5 8.96 5H4.5C3.12 5 2 6.12 2 7.5V15.5C2 16.88 3.12 18 4.5 18H16.5C17.88 18 19 16.88 19 15.5V4.5C19 3.12 17.88 2 16.5 2ZM10 14C7.79 14 6 12.21 6 10C6 7.79 7.79 6 10 6C12.21 6 14 7.79 14 10C14 12.21 12.21 14 10 14Z" />
              <path d="M10 8C8.34 8 7 9.34 7 11C7 12.66 8.34 14 10 14C11.66 14 13 12.66 13 11C13 9.34 11.66 8 10 8Z" />
            </svg>
            Загрузить YAML
          </label>
        </div>

        {/* Кнопки выбора типа теста */}
        <div className="buttons-wrapper">
          {testOptions.map((opt) => (
            <button
              key={opt.id}
              className={`button ${selectedTest === opt.id ? 'button--filled' : 'button--outline'}`}
              onClick={() => setSelectedTest(opt.id)}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* Кнопка генерации */}
        <div className="generate-wrapper">
          <button
            className="button button--filled generate-button"
            onClick={generateTest}
            disabled={loading || !prompt.trim()}
          >
            {loading ? 'Генерация...' : 'Сгенерировать тест'}
          </button>
        </div>

        {/* Блок результата */}
        {result && (
          <div className="result-section">
            <h3>Сгенерированный код:</h3>
            <pre>{result.code}</pre>

            {/* Ошибки валидации */}
            {result.validation?.errors && result.validation.errors.length > 0 && (
              <div className="validation-errors">
                <div className="validation-header">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6b6b">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                  </svg>
                  <span>Ошибки валидации:</span>
                </div>
                <ul>
                  {result.validation.errors.map((err, idx) => (
                    <li key={idx}>{err}</li>
                  ))}
                </ul>
              </div>
            )}

            <button
              className="button button--outline copy-button"
              onClick={() => navigator.clipboard.writeText(result.code)}
            >
              Копировать код
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
