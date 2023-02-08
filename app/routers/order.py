from .. import schemas, models
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends, HTTPException, status, APIRouter
from ..database import get_db


router = APIRouter()

@router.get('/', response_model=schemas.ListOrderResponse)
def get_orders(db: Session = Depends(get_db), limit: int = 10, page: int = 1):
    skip = (page - 1) * limit
    orders = db.query(models.Order).limit(limit).offset(skip).all()
    return {
        'status': 'success',
        'results': len(orders),
        'orders': orders
    }


@router.get('/{id}', response_model=schemas.OrderDetailResponse)
def get_order_detail(id: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).options(joinedload(models.Order.order_details)).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order Not Found')
    return order
