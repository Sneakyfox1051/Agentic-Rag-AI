# logging/logger.py
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional

# -----------------------------
# Configure structured logger
# -----------------------------
logger = logging.getLogger("agentic_rag")
logger.setLevel(logging.DEBUG)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Custom formatter for JSON logs
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "extra": getattr(record, "extra", {})
        }
        return json.dumps(log_record)

ch.setFormatter(JsonFormatter())
logger.addHandler(ch)


# -----------------------------
# Logging utility functions
# -----------------------------
def log_planner_decision(user_query: str, planner_output: Dict[str, Any]):
    logger.info(
        "Planner decision",
        extra={"extra": {"user_query": user_query, "planner_output": planner_output}}
    )


def log_retrieved_chunks(chunks: list, scores: list, metadata: list):
    logger.debug(
        "Retrieved chunks",
        extra={"extra": {"chunks": chunks, "scores": scores, "metadata": metadata}}
    )


def log_agent_output(agent_name: str, output: Dict[str, Any]):
    logger.info(
        f"{agent_name} output",
        extra={"extra": {"agent": agent_name, "output": output}}
    )


def log_final_action(action_result: Dict[str, Any]):
    logger.info(
        "Final action",
        extra={"extra": action_result}
    )


def log_warning(message: str, context: Optional[Dict[str, Any]] = None):
    logger.warning(
        message,
        extra={"extra": context or {}}
    )


def log_error(message: str, context: Optional[Dict[str, Any]] = None):
    logger.error(
        message,
        extra={"extra": context or {}}
    )
