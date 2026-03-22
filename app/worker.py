"""Optional Redis/RQ queue helpers.

When REDIS_URL is set, jobs are dispatched to an RQ worker process.
When empty, callers should fall back to FastAPI BackgroundTasks.
"""

import logging

from redis import Redis
from rq import Queue

from app.config import settings

logger = logging.getLogger(__name__)

QUEUE_NAME = "base-app"


def get_queue() -> Queue | None:
    """Return an RQ Queue if REDIS_URL is configured, else None."""
    if not settings.REDIS_URL:
        return None
    conn = Redis.from_url(settings.REDIS_URL)
    return Queue(QUEUE_NAME, connection=conn)


def validate_redis() -> str | None:
    """Check Redis is reachable and workers are listening.

    Returns an error message string if there is a problem, None if OK.
    """
    if not settings.REDIS_URL:
        return "REDIS_URL is not configured"
    try:
        conn = Redis.from_url(settings.REDIS_URL)
        conn.ping()
    except Exception as exc:
        return f"Cannot reach Redis: {exc}"
    queue = Queue(QUEUE_NAME, connection=conn)
    workers = queue.workers
    if not workers:
        return f"No workers listening on queue '{QUEUE_NAME}'"
    return None
