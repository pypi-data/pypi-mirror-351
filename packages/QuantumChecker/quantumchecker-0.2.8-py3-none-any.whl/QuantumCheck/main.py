import logging
import os
import zipfile
from datetime import datetime
from typing import List, Dict, Optional
from .python_evaluator import PythonEvaluator
from .sql_evaluator import SQLEvaluator
from .powerbi_evaluator import PowerBIEvaluator
from .ssis_evaluator import SSISEvaluator
from pprint import pprint

logger = logging.getLogger(__name__)

class HomeworkEvaluator:
    EXTENSION_TO_TYPE = {
        ".py": "python",
        ".sql": "sql",
        ".pbit": "powerbi",
        ".pdf": "powerbi",
        ".dtsx": "ssis",
        ".DTSX": "ssis",
        ".txt": "text",
        ".md": "text"
    }

    def _setup_logger(self, file_type: str) -> logging.Logger:
        base_log_dir = os.path.join(os.path.dirname(__file__), "logs")
        type_log_dir = os.path.join(base_log_dir, file_type)
        os.makedirs(type_log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file_path = os.path.join(type_log_dir, f"evaluation_{timestamp}.log")

        logger = logging.getLogger(f"{file_type}_{timestamp}")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    @staticmethod
    def parse_questions(md_content: str) -> List[str]:
        questions = [q.strip() for q in md_content.strip().split("\n\n") if q.strip()]
        if not questions:
            logger.error("No valid questions found in the question content")
            raise ValueError("No valid questions found in the question content")
        logger.info("Parsed %d questions from content", len(questions))
        return questions

    def _detect_zip_content_type(self, zip_path: str) -> str:
        """Determine the file type based on ZIP contents."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                files = [f for f in zip_ref.namelist() if not f.startswith('__MACOSX/')]
                extensions = {os.path.splitext(f)[1].lower() for f in files if os.path.splitext(f)[1]}

                if not extensions:
                    logger.warning("No valid files found in ZIP: %s", zip_path)
                    return "text"

                # Check for specific file types in order of priority: sql, powerbi, ssis, python
                for ext in [".sql", ".pbit", ".pdf", ".dtsx", ".DTSX", ".py"]:
                    if ext in extensions and ext in self.EXTENSION_TO_TYPE:
                        file_type = self.EXTENSION_TO_TYPE[ext]
                        logger.info("Detected file type: %s from extension: %s in ZIP: %s", file_type, ext, zip_path)
                        return file_type

                # Fallback to text if only .txt or .md are present
                if extensions.issubset({".txt", ".md"}):
                    logger.info("Defaulting to text type for ZIP contents with extensions: %s", extensions)
                    return "text"

                logger.warning("No recognized specific file types in ZIP: %s, extensions: %s", zip_path, extensions)
                return "text"
        except zipfile.BadZipFile:
            logger.error("Invalid ZIP file: %s", zip_path)
            return "text"
        except Exception as e:
            logger.error("Error inspecting ZIP file %s: %s", zip_path, str(e))
            return "text"

    def evaluate_from_content(
        self,
        question_content: str,
        answer_path: str,
        api_key: str,
        backup_api_keys: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        if backup_api_keys is None:
            backup_api_keys = []

        try:
            questions = self.parse_questions(question_content)
        except Exception as e:
            logger.error("Failed to parse question content: %s", str(e))
            return {
                "score": 0,
                "feedback": f"Error parsing question content: {str(e)}",
                "issues": [str(e)],
                "recommendations": []
            }

        answer_path = answer_path.strip()
        _, ext = os.path.splitext(answer_path)
        ext = ext.lower()

        # Determine file type
        if ext == ".zip":
            file_type = self._detect_zip_content_type(answer_path)
        else:
            file_type = self.EXTENSION_TO_TYPE.get(ext, "text")

        eval_logger = self._setup_logger(file_type)
        eval_logger.info("Processing answer_path: %s", answer_path)
        eval_logger.info("Extracted extension: %s", ext)
        eval_logger.info("Detected file type: %s for file: %s", file_type, answer_path)
        pprint(f"Processing {len(questions)} questions for file type: {file_type}")

        if not os.path.exists(answer_path):
            eval_logger.error("Answer file not found: %s", answer_path)
            return {
                "score": 0,
                "feedback": f"Answer file not found: {answer_path}",
                "issues": [f"Answer file not found: {answer_path}"],
                "recommendations": []
            }

        def create_evaluator(ftype, key):
            if ftype == "python":
                eval_logger.info("Using PythonEvaluator for file type: %s", ftype)
                return PythonEvaluator(key)
            elif ftype == "sql":
                eval_logger.info("Using SQLEvaluator for file type: %s", ftype)
                return SQLEvaluator(key)
            elif ftype == "powerbi":
                eval_logger.info("Using PowerBIEvaluator for file type: %s", ftype)
                return PowerBIEvaluator(key)
            elif ftype == "ssis":
                eval_logger.info("Using SSISEvaluator for file type: %s", ftype)
                return SSISEvaluator(key)
            else:
                eval_logger.warning("Unknown file type %s, defaulting to PythonEvaluator", ftype)
                return PythonEvaluator(key)

        keys_to_try = [api_key] + backup_api_keys[:5]

        last_exception = None
        for i, key in enumerate(keys_to_try):
            evaluator = create_evaluator(file_type, key)
            try:
                evaluation = evaluator.evaluate(questions, answer_path)
                eval_logger.info(f"Evaluation complete with API key #{i + 1}: Score = {evaluation.get('score')}")
                return {
                    "score": evaluation.get("score", 0),
                    "feedback": evaluation.get("feedback", "No feedback provided"),
                    "issues": evaluation.get("issues", []),
                    "recommendations": evaluation.get("recommendations", [])
                }
            except Exception as e:
                error_msg = str(e).lower()
                if (
                    "429" in error_msg
                    or "rate limit" in error_msg
                    or "quota exceeded" in error_msg
                    or "daily limit exceeded" in error_msg
                    or "quota" in error_msg
                ):
                    eval_logger.warning(f"API key #{i + 1} limited or quota exceeded. Trying next key if available.")
                    last_exception = e
                    continue
                else:
                    eval_logger.error(f"Evaluation failed with API key #{i + 1}: %s", str(e))
                    return {
                        "score": 0,
                        "feedback": f"Evaluation failed: {str(e)}",
                        "issues": [str(e)],
                        "recommendations": []
                    }
        else:
            eval_logger.error("All API keys exhausted and evaluation failed.")
            return {
                "score": 0,
                "feedback": f"All API keys exhausted: {str(last_exception) if last_exception else 'Unknown error'}",
            }