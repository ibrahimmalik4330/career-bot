from tools.handlers import (
    record_user_details,
    record_unknown_question,
)

TOOL_REGISTRY = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
}