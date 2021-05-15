import typing

from pydantic import BaseModel, PositiveInt, constr


class Shipper(BaseModel):
    ShipperID: PositiveInt
    CompanyName: constr(max_length=40)
    Phone: constr(max_length=24)

    class Config:
        orm_mode = True


class Suppliers(BaseModel):
    SupplierID: PositiveInt
    CompanyName: constr(max_length=40)

    class Config:
        orm_mode = True


class Supplier(BaseModel):
    SupplierID: PositiveInt
    CompanyName: typing.Optional[str] = None
    ContactName: typing.Optional[str] = None
    ContactTitle: typing.Optional[str] = None
    Address: typing.Optional[str] = None
    City: typing.Optional[str] = None
    Region: typing.Optional[str] = None
    PostalCode: typing.Optional[str] = None
    Country: typing.Optional[str] = None
    Phone: typing.Optional[str] = None
    Fax: typing.Optional[str] = None
    HomePage: typing.Optional[str] = None


    class Config:
        orm_mode = True

class Supplier(BaseModel):
    SupplierID: PositiveInt
    CompanyName: typing.Optional[str] = None
    ContactName: typing.Optional[str] = None
    ContactTitle: typing.Optional[str] = None
    Address: typing.Optional[str] = None
    City: typing.Optional[str] = None
    Region: typing.Optional[str] = None
    PostalCode: typing.Optional[str] = None
    Country: typing.Optional[str] = None
    Phone: typing.Optional[str] = None
    Fax: typing.Optional[str] = None
    HomePage: typing.Optional[str] = None


    class Config:
        orm_mode = True


class AddSupplier(BaseModel):
    CompanyName: constr(max_length=40)
    ContactName: typing.Optional[str]
    ContactTitle: typing.Optional[str]
    Address: typing.Optional[str]
    City: typing.Optional[str]
    Region: typing.Optional[str]
    PostalCode: typing.Optional[str]
    Country: typing.Optional[str]
    Phone: typing.Optional[str]
    Fax: typing.Optional[str]
    HomePage: typing.Optional[str]

    class Config:
        orm_mode = True