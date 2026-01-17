from typing import Dict
from tools.notifications import push

def record_user_details(
    email: str,
    name: str = "Name not provided",
    notes: str = "not provided",
) -> Dict[str, str]:
    push(f"User: {name} | Email: {email} | Notes: {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question: str) -> Dict[str, str]:
    push(f"Recording {question}")
    return {"recorded": "ok"}