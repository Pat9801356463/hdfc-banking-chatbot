# app/debug_logger.py

from collections import deque

MAX_LOGS = 50
debug_logs = deque(maxlen=MAX_LOGS)

def add_log(query, steps):
    debug_logs.appendleft({
        "query": query,
        "steps": steps
    })

def get_logs():
    return list(debug_logs)
