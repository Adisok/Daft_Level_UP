from sqlalchemy.orm import Session

import models
import schemas


def get_shippers(db: Session):
    return db.query(models.Shipper).all()


def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models.Shipper).filter(models.Shipper.ShipperID == shipper_id).first()
    )


def get_suppliers(db: Session):
    return(
        db.query(models.Supplier).all()
    )


def get_supplier(db: Session, supplier_id: int):
    return(
        db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).first()
    )


def get_products(db: Session, id_sup: int):
    return db.query(models.Product.ProductID, models.Product.ProductName, models.Product.Discontinued,
                    models.Category.CategoryID, models.Category.CategoryName) \
            .join(models.Category, models.Product.CategoryID == models.Category.CategoryID) \
            .filter(models.Product.SupplierID == id_sup) \
            .order_by(models.Product.ProductID.desc()).all()


def add_supplier(db: Session, supplier: schemas.AddSupplier):
    supplier_id = db.query(models.Supplier).count() + 1
    db_supplier = models.Supplier(
        SupplierID=supplier_id,
        CompanyName=supplier.CompanyName,
        ContactName=supplier.ContactName,
        ContactTitle=supplier.ContactTitle,
        Address=supplier.Address,
        City=supplier.City,
        PostalCode=supplier.PostalCode,
        Country=supplier.Country,
        Phone=supplier.Phone,
        Fax=supplier.Fax,
        HomePage=supplier.HomePage
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def upd_supp(db: Session, supplier: schemas.AddSupplier, sup_id: int):
    new_vals = {key: val for key,val in dict(supplier).items() if val is not None}
    if new_vals:
        db.query(models.Supplier).filter(models.Supplier.SupplierID == sup_id).update(values=new_vals)
    db.commit()
    pass
