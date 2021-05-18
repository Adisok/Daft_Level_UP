from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import PositiveInt, ValidationError
from sqlalchemy.orm import Session

import crud
import schemas
import models
from database import get_db

router = APIRouter()

def check_for_supplier(db, supp_id):
    is_supp = crud.get_supplier(db, supp_id)
    if is_supp is None:
        raise HTTPException(status_code=404, detail="Not Okie Dokie ID")
    return is_supp


@router.get("/shippers/{shipper_id}", response_model=schemas.Shipper)
async def get_shipper(shipper_id: PositiveInt, db: Session = Depends(get_db)):
    db_shipper = crud.get_shipper(db, shipper_id)
    if db_shipper is None:
        raise HTTPException(status_code=404, detail="Shipper not found")
    return db_shipper


@router.get("/shippers", response_model=List[schemas.Shipper])
async def get_shippers(db: Session = Depends(get_db)):
    return crud.get_shippers(db)


@router.get("/suppliers", response_model=List[schemas.Suppliers])
async def get_supplier(db: Session = Depends(get_db)):
    return crud.get_suppliers(db)


@router.get("/suppliers/{supplier_id}", response_model=schemas.Supplier)
async def get_supplier(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = check_for_supplier(db, supplier_id)
    return db_supplier


@router.get("/suppliers/{id}/products")
async def get_sorted_supplier(pid: PositiveInt, db: Session = Depends(get_db)):
    db_products = crud.get_products(db, pid)
    if db_products:
        data = [{"ProductID": prod.ProductID,
                 "ProductName": prod.ProductName,
                 "Category": {
                    "CategoryID": prod.CategoryID,
                    "CategoryName": prod.CategoryName,
                            },
                "Discontinued": prod.Discontinued}
                for prod in db_products]
        return data
    else:
        raise HTTPException(status_code=404, detail="Not Oki Doki ID!")


@router.post("/suppliers", response_model=schemas.Supplier, status_code=201)
async def add_supplier(supp: schemas.AddSupplier, db: Session = Depends(get_db)):
    return crud.add_supplier(db, supp)

@router.put("/suppliers/{sup_id}", response_model= schemas.Supplier, status_code=200)
async def update_supplier(sup_id: int, supp: schemas.UpdateSupplier, db: Session = Depends(get_db)):
    db_supplier = check_for_supplier(db, sup_id)
    crud.upd_supp(db, supp, sup_id)
    return get_db(db, sup_id)
