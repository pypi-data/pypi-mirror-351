# 📘 HomeworkEvaluator

The **HomeworkEvaluator** is a Python-based evaluation engine designed to automatically assess student assignments across different technologies including Python, SQL, Power BI, and SSIS. It uses AI to parse and evaluate student-submitted answers against a set of markdown-formatted questions.

---

## ✨ Features

- Supports multiple file types:
  - `.py` → Python
  - `.sql` → SQL
  - `.zip` → Power BI
  - `.dtsx` / `.DTSX` → SSIS
  - `.txt` / `.md` → Plain Text
- Smart evaluator routing based on file extension.
- AI-powered feedback generation and scoring.
- Logging for each evaluation by file type and timestamp.
- Automatic fallback to backup API keys when quota is exceeded.

---

## 📦 Folder Structure

```
.
├── homework_evaluator/
│   ├── homework_evaluator.py         # Main evaluator class
│   ├── python_evaluator.py           # Python evaluator logic
│   ├── sql_evaluator.py              # SQL evaluator logic
│   ├── powerbi_evaluator.py          # Power BI evaluator logic
│   ├── ssis_evaluator.py             # SSIS evaluator logic
│   └── logs/                         # Log files categorized by type and timestamp
```

---

## 🔧 Installation

Clone this repository and install the necessary dependencies:

```bash
git clone https://github.com/yourusername/homework-evaluator.git
cd homework-evaluator
pip install -r requirements.txt
```

---

## 🧠 Usage

```python
from homework_evaluator import HomeworkEvaluator

evaluator = HomeworkEvaluator()

result = evaluator.evaluate_from_content(
    question_content=markdown_questions,
    answer_path="/path/to/answer/file.py",
    api_key="your-main-api-key",
    backup_api_keys=["backup-key-1", "backup-key-2"]
)

print(result["mark"])      # e.g., 85
print(result["feedback"])  # Structured feedback
```

---

## 🗂️ Question Format

The evaluator expects `question_content` as a Markdown-formatted string where each question is separated by a **double newline** (`\n\n`). Example:

```markdown
### Q1
Write a Python function to reverse a string.

### Q2
Explain the purpose of list comprehensions in Python.
```

---

## 🛠️ Logging

All evaluations are logged under the `logs/` directory, grouped by file type and timestamp.

```
logs/
├── python/
│   └── evaluation_2025-05-26_14-00-00.log
├── sql/
│   └── evaluation_2025-05-26_14-10-12.log
```

---

## 🧪 Exception Handling

- If a file is not found or questions are malformed, an informative error is raised.
- If the API quota is exceeded (429 errors or rate limits), it retries using backup keys.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss your ideas.
