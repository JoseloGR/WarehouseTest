
from .. import schemas, models
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response

router = APIRouter()

@router.get('/', response_model=schemas.ListProductResponse)
def get_products(db: Session = Depends(get_db), limit: int = 10, page: int = 1):
    skip = (page - 1) * limit

    products = db.query(models.Product).limit(limit).offset(skip).all()
    return {
        'status': 'success',
        'results': len(products),
        'products': products
    }


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
def create_product(product: schemas.CreateProductSchema, db: Session = Depends(get_db)):
    new_product = models.Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.put('/{id}', response_model=schemas.ProductResponse)
def update_product(id: str, product: schemas.UpdateProductSchema, db: Session = Depends(get_db)):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    updated_product = product_query.first()

    if not updated_product:
        raise HTTPException(status_code=status.HTTP_200_OK,
                            detail=f'No product with this id: {id} found')
    
    product_query.update(product.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return updated_product


@router.get('/{id}', response_model=schemas.ProductResponse)
def get_product(id: str, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No product with this id: {id} found')

    return product


@router.delete('/{id}')
def delete_product(id: str, db: Session = Depends(get_db)):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()

    if not product:
        raise HTTPException

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No product with this id: {id} found')

    product_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
