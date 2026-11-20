from fastapi import APIRouter
router = APIRouter(tags=["Santé"])


@router.get("/health")
def health():
    return {"status": "healthy", "application": "Ndonga_buzness"}
