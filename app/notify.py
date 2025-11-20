import httpx
from app.config import settings

async def notify_startup_new_request(*, token: str, project_id: int, amount: float):
    
    proj_url = f"{settings.GATEWAY_BASE}/api/projects/startup-projects/{project_id}/"
    headers = {"Authorization": token}
    async with httpx.AsyncClient(timeout=8.0) as client:
        r = await client.get(proj_url, headers=headers)
    if r.status_code != 200:
        return
    pdata = r.json()
    startup_profile_id = pdata.get("startup_profile_id")
    if not startup_profile_id:
        return

    notif_url = f"{settings.GATEWAY_BASE}/notifications/"
    payload = {
        "message": f"New investment request for project #{project_id} (amount: {amount})",
        "startup": startup_profile_id
    }
    async with httpx.AsyncClient(timeout=8.0) as client:
        await client.post(notif_url, json=payload, headers=headers)


async def notify_investor_confirmation(*, token: str, message: str, investor_profile_id: int | None):
    
    if not investor_profile_id:
        return

    url = f"{settings.GATEWAY_BASE}/notifications/"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    payload = {
        "message": message,
        "investor": investor_profile_id
    }
    async with httpx.AsyncClient(timeout=8.0) as client:
        await client.post(url, json=payload, headers=headers)
