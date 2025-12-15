from __future__ import annotations

import os

from celery import Celery

from prime_utils import first_n_primes


def _redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")


celery_app = Celery(
    "prime_tasks",
    broker=_redis_url(),
    backend=_redis_url(),
)


@celery_app.task(name="compute_first_n_primes")
def compute_first_n_primes(n: int) -> list[int]:
    return first_n_primes(n)


