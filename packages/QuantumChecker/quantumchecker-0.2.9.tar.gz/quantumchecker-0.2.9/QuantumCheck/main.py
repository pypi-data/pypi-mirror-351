import logging
import os
import zipfile
import random
from datetime import datetime
from typing import List, Dict, Optional
from .python_evaluator import PythonEvaluator
from .sql_evaluator import SQLEvaluator
from .powerbi_evaluator import PowerBIEvaluator
from .ssis_evaluator import SSISEvaluator
import asyncio

_logger_cache = {}

class HomeworkEvaluator:
    EVALUATOR_REGISTRY = {
        "python": PythonEvaluator,
        "sql": SQLEvaluator,
        "powerbi": PowerBIEvaluator,
        "ssis": SSISEvaluator
    }

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

    API_NAME_MAPPING = {
        "python": "Google Gemini API",
        "sql": "Google Gemini API",
        "powerbi": "Google Gemini API",
        "ssis": "Google Gemini API",
        "text": "Google Gemini API"
    }

    def __init__(self, log_level: int = logging.INFO):
        self.log_level = log_level
        self._successful_key_cache = {}
        self._rate_limit_delay = {}  # Track delay per key

    def _get_logger(self, log_type: str) -> logging.Logger:
        log_name = f"{log_type}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        if log_name not in _logger_cache:
            logger = logging.getLogger(log_name)
            logger.setLevel(self.log_level)
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
                logger.addHandler(handler)
            _logger_cache[log_name] = logger
        return _logger_cache[log_name]

    def parse_questions(self, content: str) -> List[str]:
        logger = self._get_logger("QuantumCheck.main")
        questions = [q.strip() for q in content.split("\n\n") if q.strip()]
        logger.info(f"Parsed {len(questions)} questions from content")
        if not questions:
            raise ValueError("No valid questions found in content")
        return questions

    def _detect_zip_content_type(self, zip_path: str, logger: logging.Logger) -> str:
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                extensions = {os.path.splitext(name)[1].lower() for name in zip_ref.namelist()}
                file_types = [self.EXTENSION_TO_TYPE.get(ext, "text") for ext in extensions if ext]
                logger.info(f"Detected extensions in ZIP {zip_path}: {extensions}, types: {file_types}")
                if "python" in file_types:
                    logger.info(f"Selected file type: python from extension: .py in ZIP: {zip_path}")
                    return "python"
                elif "sql" in file_types:
                    logger.info(f"Selected file type: sql from extension: .sql in ZIP: {zip_path}")
                    return "sql"
                elif "powerbi" in file_types:
                    logger.info(f"Selected file type: powerbi from extension: .pbit or .pdf in ZIP: {zip_path}")
                    return "powerbi"
                elif "ssis" in file_types:
                    logger.info(f"Selected file type: ssis from extension: .dtsx in ZIP: {zip_path}")
                    return "ssis"
                else:
                    logger.info(f"Selected file type: text (default) in ZIP: {zip_path}")
                    return "text"
        except zipfile.BadZipFile:
            logger.error(f"Invalid ZIP file: {zip_path}")
            raise ValueError(f"Invalid ZIP file: {zip_path}")

    async def evaluate_from_content(
            self,
            question_content: str,
            answer_path: str,
            api_keys: List[str],
            question_type: str
    ) -> Dict[str, any]:
        try:
            questions = self.parse_questions(question_content)
        except ValueError as e:
            logger = self._get_logger("QuantumCheck.main")
            logger.error("Failed to parse question content: %s", str(e))
            return {
                "score": 0,
                "feedback": f"Error parsing question content: {str(e)}",
                "issues": [str(e)],
                "recommendations": [],
                "used_api_key_index": None,
                "used_api_name": None
            }

        answer_path = answer_path.strip()
        _, ext = os.path.splitext(answer_path)
        ext = ext.lower()

        # Determine file type, prioritizing question_type for evaluator selection
        if ext == ".zip":
            logger = self._get_logger("zip")
            file_type = self._detect_zip_content_type(answer_path, logger)
        else:
            file_type = self.EXTENSION_TO_TYPE.get(ext, "text")
            logger = self._get_logger(file_type)

        # Use question_type if provided, else fallback to file_type
        eval_type = question_type if question_type in self.EVALUATOR_REGISTRY else file_type
        logger.info(f"Processing answer_path: {answer_path} with detected file type: {file_type}, evaluation type: {eval_type}")

        if not os.path.exists(answer_path):
            logger.error(f"Answer file not found: {answer_path}")
            return {
                "score": 0,
                "feedback": f"Answer file not found: {answer_path}",
                "issues": [f"Answer file not found: {answer_path}"],
                "recommendations": [],
                "used_api_key_index": None,
                "used_api_name": None
            }

        evaluator_class = self.EVALUATOR_REGISTRY.get(eval_type, PythonEvaluator)
        last_error_messages = []

        # Shuffle keys for load balancing
        key_order = [(i + 1, key) for i, key in enumerate(api_keys)]
        random.shuffle(key_order)

        # Try cached key with 30% probability to encourage rotation
        cached_key_idx = self._successful_key_cache.get(eval_type)
        if cached_key_idx is not None and cached_key_idx < len(api_keys) and random.random() < 0.3:
            key_order.insert(0, (cached_key_idx + 1, api_keys[cached_key_idx]))

        for idx, key in key_order:
            # Check rate limit delay
            if key in self._rate_limit_delay:
                delay_until = self._rate_limit_delay[key]
                current_time = datetime.now()
                delay_until_time = datetime.fromtimestamp(delay_until)
                if current_time < delay_until_time:
                    logger.info(f"API key #{idx} is rate-limited until {delay_until_time}, skipping.")
                    continue
                else:
                    del self._rate_limit_delay[key]

            logger.info(f"Trying API key #{idx}")
            evaluator = evaluator_class(key)
            api_name = getattr(evaluator, 'get_api_name', lambda: self.API_NAME_MAPPING.get(eval_type, "Unknown API"))()
            logger.info(f"Using API: {api_name} for evaluation type: {eval_type}")

            try:
                evaluation = evaluator.evaluate(questions, answer_path, temp_dir=f"temp_extract_{os.getpid()}_{idx}")

                feedback = evaluation.get("feedback", "").lower()
                issues = " ".join(evaluation.get("issues", [])).lower()

                # Check for invalid API key
                if any(phrase in feedback or phrase in issues for phrase in ["api key not valid", "api_key_invalid"]):
                    logger.warning(f"API key #{idx} invalid, trying next key.")
                    last_error_messages.append(f"API key #{idx} invalid.")
                    continue

                # Check for rate limit errors
                if any(phrase in feedback or phrase in issues for phrase in ["429", "too many requests", "rate limit"]):
                    logger.warning(f"API key #{idx} hit rate limit, applying delay.")
                    last_error_messages.append(f"API key #{idx} rate limited.")
                    self._rate_limit_delay[key] = datetime.now().timestamp() + 45  # 45s delay
                    continue

                # Check for invalid evaluation
                if evaluation.get("score", 0) == 0 and "evaluation not returned" in feedback:
                    logger.warning(f"API key #{idx} returned invalid evaluation, trying next key.")
                    last_error_messages.append(f"API key #{idx} returned invalid evaluation.")
                    continue

                # Cache successful key
                self._successful_key_cache[eval_type] = idx - 1
                logger.info(f"Evaluation succeeded with API key #{idx}: Score = {evaluation.get('score')}")

                return {
                    "score": evaluation.get("score", 0),
                    "feedback": evaluation.get("feedback", "No feedback provided"),
                    "issues": evaluation.get("issues", []),
                    "recommendations": evaluation.get("recommendations", []),
                    "used_api_key_index": idx,
                    "used_api_name": api_name
                }

            except Exception as e:
                logger.error(f"Exception using API key #{idx}: {str(e)}")
                last_error_messages.append(f"Exception with key #{idx}: {str(e)}")
                if "429" in str(e) or "rate limit" in str(e).lower():
                    self._rate_limit_delay[key] = datetime.now().timestamp() + 45
                continue

        logger.error("Evaluation failed with all API keys.")
        return {
            "score": 0,
            "feedback": "Evaluation failed with all API keys.",
            "issues": last_error_messages if last_error_messages else ["All API keys failed to evaluate the submission."],
            "recommendations": [],
            "used_api_key_index": None,
            "used_api_name": None
        }