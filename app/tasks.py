"""Synchronous RQ task wrappers.

RQ calls these functions in a worker process. Each wraps an async job runner
via asyncio.run(). Add your task functions here following this pattern:

    def my_task(job_id: int, **kwargs):
        import asyncio
        asyncio.run(_run_with_error_handling(job_id, run_my_job, **kwargs))
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def _run_with_error_handling(job_id: int, runner, **kwargs):
    """Run an async job runner, logging and re-raising unhandled exceptions."""
    try:
        await runner(job_id=job_id, **kwargs)
    except Exception as exc:
        logger.error("RQ task (job %d) failed: %s", job_id, exc)
        raise
