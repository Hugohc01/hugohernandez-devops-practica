import uuid
from datetime import datetime
from typing import List, Tuple

from models.producto import Producto
from models.usuario import Cliente


class Pedido:
    
    
    # Inicializa un pedido
    def __init__(
        self, cliente: Cliente, productos: List[Tuple[Producto, int]]
    ) -> None:

        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.productos: List[Tuple[Producto, int]] = productos
        self.fecha: datetime = datetime.now()



    # Calcula el importe total del pedido
    def calcular_total(self) -> float:
        

        return sum(producto.precio * cantidad for producto, cantidad in self.productos)

    def __str__(self) -> str:
        
        lineas = [
            f"  - {producto.nombre} x{cantidad} ({producto.precio:.2f}EUR c/u)"
            for producto, cantidad in self.productos
        ]
        detalle = "\n".join(lineas)
        return (
            f"Pedido [{self.id[:8]}] de {self.cliente.nombre} "
            f"({self.fecha:%Y-%m-%d %H:%M}):\n"
            f"{detalle}\n"
            f"  Total: {self.calcular_total():.2f}EUR"
        )
