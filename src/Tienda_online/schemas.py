"""Esquemas Pydantic de la API.

Los esquemas *Create* describen los datos que envia el cliente en las
peticiones y los esquemas *Read* describen los datos que devuelve la API.
FastAPI los usa para validar automaticamente y para generar /docs.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Tallas de ropa permitidas
Talla = Literal["XS", "S", "M", "L", "XL", "XXL"]


# ----------------------------------------------------------------------
# 1.1 Usuarios
# ----------------------------------------------------------------------

class UsuarioCreate(BaseModel):
    # Quita espacios al principio y al final de todos los textos
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(..., min_length=1, examples=["Fry"])
    email: str = Field(
        ...,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        examples=["fry@planetexpress.com"],
    )
    tipo: Literal["cliente", "administrador"] = Field(..., examples=["cliente"])
    direccion_postal: Optional[str] = Field(None, examples=["Calle Delivery 1"])

    # Un cliente necesita direccion postal para poder recibir pedidos
    @model_validator(mode="after")
    def validar_direccion(self):
        if self.tipo == "cliente" and not self.direccion_postal:
            raise ValueError("Los clientes deben tener 'direccion_postal'.")
        return self


class UsuarioRead(BaseModel):
    id: str
    nombre: str
    email: str
    es_admin: bool
    direccion_postal: Optional[str] = None


# ----------------------------------------------------------------------
# 1.2 Productos
# ----------------------------------------------------------------------

class ProductoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    tipo: Literal["generico", "electronico", "ropa"] = Field(..., examples=["electronico"])
    nombre: str = Field(..., min_length=1, examples=["Portatil"])
    precio: float = Field(..., gt=0, examples=[899.99])
    stock: int = Field(..., ge=0, examples=[10])
    # Atributos adicionales segun el tipo de producto
    meses_garantia: Optional[int] = Field(None, ge=0, le=120, examples=[24])
    talla: Optional[Talla] = Field(None, examples=[None])
    color: Optional[str] = Field(None, min_length=1, max_length=30, examples=[None])

    # Acepta la talla en minusculas ("m" -> "M") antes de validarla
    @field_validator("talla", mode="before")
    @classmethod
    def normalizar_talla(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip().upper()
            return valor or None
        return valor

    # Comprueba que cada tipo trae sus atributos obligatorios
    # y que no trae atributos de otro tipo
    @model_validator(mode="after")
    def validar_atributos_por_tipo(self):
        es_ropa = self.tipo == "ropa"
        es_electronico = self.tipo == "electronico"

        if es_electronico and self.meses_garantia is None:
            raise ValueError("Los productos electronicos requieren 'meses_garantia'.")
        if es_ropa and (not self.talla or not self.color):
            raise ValueError("Los productos de ropa requieren 'talla' y 'color'.")

        if not es_electronico and self.meses_garantia is not None:
            raise ValueError("'meses_garantia' solo se permite en productos electronicos.")
        if not es_ropa and (self.talla is not None or self.color is not None):
            raise ValueError("'talla' y 'color' solo se permiten en productos de ropa.")
        return self


class ProductoRead(BaseModel):
    id: str
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None


# ----------------------------------------------------------------------
# 1.3 Pedidos
# ----------------------------------------------------------------------

class PedidoItemCreate(BaseModel):
    producto_id: str
    cantidad: int = Field(..., gt=0, examples=[1])


class PedidoCreate(BaseModel):
    cliente_id: str
    items: List[PedidoItemCreate] = Field(..., min_length=1)


class PedidoItemRead(BaseModel):
    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    id: str
    fecha: datetime
    cliente_id: str
    cliente_nombre: str
    total: float
    items: List[PedidoItemRead]
