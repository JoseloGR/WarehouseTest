
from .. import schemas, models
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends, HTTPException, status, APIRouter, Response

router = APIRouter()

@router.get('/', response_model=schemas.ListWarehouseResponse)
def get_warehouses(db: Session = Depends(get_db), limit: int = 10, page: int = 1):
    skip = (page - 1) * limit

    warehouses = db.query(models.Warehouse).limit(limit).offset(skip).all()
    return {
        'status': 'success',
        'results': len(warehouses),
        'data': warehouses
    }


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.WarehouseResponse)
def create_warehouse(warehouse: schemas.CreateWarehouseSchema, db: Session = Depends(get_db)):
    try:
        new_warehouse = models.Warehouse(**warehouse.dict())
        db.add(new_warehouse)
        db.commit()
        db.refresh(new_warehouse)
        return new_warehouse
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=error)


@router.put('/{id}', response_model=schemas.WarehouseResponse)
def update_warehouse(id: str, warehouse: schemas.UpdateWarehouseSchema, db: Session = Depends(get_db)):
    warehouse_query = db.query(models.Warehouse).filter(models.Warehouse.id == id)
    updated_warehouse = warehouse_query.first()

    if not updated_warehouse:
        raise HTTPException(status_code=status.HTTP_200_OK,
                            detail=f'No warehouse with this id: {id} found')
    
    warehouse_query.update(warehouse.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return updated_warehouse


@router.get('/{id}', response_model=schemas.WarehouseResponse)
def get_warehouse(id: str, db: Session = Depends(get_db)):
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == id).first()

    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No warehouse with this id: {id} found')

    return warehouse


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_warehouse(id: str, db: Session = Depends(get_db)):
    warehouse_query = db.query(models.Warehouse).filter(models.Warehouse.id == id)
    warehouse = warehouse_query.first()

    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No warehouse with this id: {id} found')

    warehouse_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
