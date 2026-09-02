from fastapi import APIRouter

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.get("/")
def get_conversations():
    return []