# Лабораторна робота №4: Аналіз вразливостей NVD CVE 2.0 та CVSS v3.1 (Варіант 14)

## 1. Предметна область та критерії варіанту
- **Джерело даних**: NVD CVE 2.0 (локальний JSON-файл або REST API 2.0).
- **Метрика**: CVSS v3.1.
- **Поріг оцінки (`baseScore`)**: `>= 6.0`.
- **Вплив на доступність (`availabilityImpact`)**: `"LOW"`.

## 2. Інструкція з запуску

1. **Встановлення залежностей** (виконувати з кореня репозиторію):
   ```powershell
   pip install -r requirements.txt
   ```

2. **Запуск аналізу на локальному прикладі даних:**
   ```PowerShell
   python -m labs.lab04.main --input labs/lab04/data/nvd_sample.json
   ```

3. **Збереження результату у файл:**
   ```PowerShell
   python -m labs.lab04.main --input labs/lab04/data/nvd_sample.json --output report.json
   ```

4. **Запит до NVD REST API 2.0:**
   ```PowerShell
   python -m labs.lab04.main --results-per-page 20
   ```

## 3. Тестування та перевірка коду

- **Запуск тестів pytest:**
  ```PowerShell
  python -m pytest labs/lab04/tests -q
  ```

- **Перевірка лінтером ruff:**
  ```PowerShell
  python -m ruff check labs/lab04
  ```

- **Перевірка форматування ruff:**
  ```PowerShell
  python -m ruff format --check labs/lab04
  ```

## 4. Формат звіту (JSON)

```json
{
  "variant": 14,
  "rule": {
    "cvss_version": "3.1",
    "min_base_score": 6.0,
    "availability_impact": "LOW"
  },
  "total_vulnerabilities": 20,
  "skipped_missing_cvss_v31": 19,
  "matched_count": 0,
  "matches": []
}
```

## 5. Робота з Git

```PowerShell
git status
git add labs/lab04/README.md
git diff --cached
git commit -m "docs(lab04): update README with report format and git workflow"
git push
```

