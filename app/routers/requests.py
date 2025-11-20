from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import httpx, asyncio

from app.db import get_db
from app.models import InvestmentRequest
from app.schemas import InvestmentRequestCreate, InvestmentRequestOut
from app.security import get_current_investor_id
from app.config import settings
from app.notify import notify_startup_new_request, notify_investor_confirmation

router = APIRouter(prefix="/investments/requests", tags=["investment-requests"])

OPEN_STATUSES = {"open", "opened", "active"}
bearer = HTTPBearer(auto_error=True)

async def _check_project_open(project_id: int, creds: HTTPAuthorizationCredentials) -> bool:
    base = settings.GATEWAY_BASE
    url = f"{base}/api/projects/startup-projects/{project_id}/"
    headers = {"Authorization": f"{creds.scheme} {creds.credentials}"}

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)

        if resp.status_code in (401, 403):
            raise HTTPException(status_code=401, detail="Authorization to monolith failed (via KrakenD).")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Project not found in monolith.")
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Monolith error {resp.status_code} via KrakenD.")

        data = resp.json()
        raw_status = data.get("status") or (data.get("project") or {}).get("status")
        if raw_status is None:
            raise HTTPException(status_code=502, detail="Monolith response has no 'status' field.")
        state = str(raw_status).strip().lower()
        return state in OPEN_STATUSES

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to contact monolith via KrakenD: {e}")


async def _get_investor_profile_id(token_header: str) -> int | None:

    url = f"{settings.GATEWAY_BASE}/api/profiles/search/?me=1&role=investor"
    headers = {"Authorization": token_header}
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            r = await client.get(url, headers=headers)
        if r.status_code != 200:
            return None
        data = r.json()
        if isinstance(data, list) and data:
            return data[0].get("id")
        if isinstance(data, dict):
            return data.get("id")
        return None
    except Exception:
        return None


@router.post("/", response_model=InvestmentRequestOut, status_code=status.HTTP_201_CREATED)
async def create_request(
    payload: InvestmentRequestCreate,
    background: BackgroundTasks,
    investor_id: int = Depends(get_current_investor_id),
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    is_open = await _check_project_open(payload.project_id, creds)
    if not is_open:
        raise HTTPException(status_code=400, detail="Project is not open for investment (required status: 'open').")

    obj = InvestmentRequest(
        project_id=payload.project_id,
        investor_id=investor_id,
        amount=payload.amount,
        message=payload.message,
        status="pending",
    )
    db.add(obj)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(obj)

    token_header = f"{creds.scheme} {creds.credentials}"

    background.add_task(
        notify_startup_new_request,
        token=token_header,
        project_id=obj.project_id,
        amount=float(obj.amount),
    )

    investor_profile_id = await _get_investor_profile_id(token_header)
    background.add_task(
        notify_investor_confirmation,
        token=token_header,
        message=f"Your investment request for project #{obj.project_id} is created with amount {float(obj.amount)}",
        investor_profile_id=investor_profile_id
    )

    return obj
