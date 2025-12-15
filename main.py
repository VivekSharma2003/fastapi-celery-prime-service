from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, conint

from tasks import celery_app, compute_first_n_primes

app = FastAPI(title="FastAPI + Celery Prime Service")


class SubmitRequest(BaseModel):
    n: conint(ge=1, le=10_000) = Field(
        ...,
        description="Number of prime numbers to compute (1-10,000).",
    )


class SubmitResponse(BaseModel):
    request_id: str


class ResultResponse(BaseModel):
    status: str
    result: Optional[list[int]] = None


@app.post("/submit", response_model=SubmitResponse)
async def submit_prime_job(payload: SubmitRequest) -> SubmitResponse:
    async_result = compute_first_n_primes.delay(payload.n)
    return SubmitResponse(request_id=async_result.id)


@app.get("/result/{request_id}", response_model=ResultResponse)
async def get_result(request_id: str) -> ResultResponse:
    async_result = celery_app.AsyncResult(request_id)

    status = async_result.status

    if status == "SUCCESS":
        result: Any = async_result.result
        return ResultResponse(status="SUCCESS", result=result)

    return ResultResponse(status=status, result=None)


@app.get("/worker-status")
async def worker_status() -> dict[str, Any]:
    try:
        responses = celery_app.control.ping(timeout=1.0)
        inspect = celery_app.control.inspect()

        active = inspect.active() or {}
        reserved = inspect.reserved() or {}
        scheduled = inspect.scheduled() or {}

        def _count_tasks(mapping: dict[str, list[dict[str, Any]]]) -> int:
            return sum(len(v) for v in mapping.values())

        queue_status = {
            "active": _count_tasks(active),
            "reserved": _count_tasks(reserved),
            "scheduled": _count_tasks(scheduled),
        }
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=503, detail=f"Worker check failed: {exc}")

    is_healthy = bool(responses)
    return {
        "healthy": is_healthy,
        "workers": responses,
        "queue_status": queue_status,
        "active_tasks": active,
    }


