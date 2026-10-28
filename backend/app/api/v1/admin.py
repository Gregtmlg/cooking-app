from fastapi import APIRouter, Depends

from app.api.deps import DbSession, require_admin
from app.schemas.admin import InventoryRead
from app.services.inventory_service import get_inventory

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/inventory", response_model=InventoryRead)
def inventory(db: DbSession):
    return get_inventory(db)
