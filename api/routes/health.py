from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/live")
def liveness():
    return {"status": "alive"}

@router.get("/ready")
def readiness():
    # Placeholder for your readiness checks
    is_ready = True  
    if is_ready:
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Not ready")
