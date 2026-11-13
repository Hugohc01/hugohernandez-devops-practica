import uuid

# Clase base que representa un producto generico de la tienda
class Producto:
    
    # Inicializa un producto con id autogenerado, nombre, precio y stock
    def __init__(self, nombre: str, precio: float, stock: int) -> None:

        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock


    # Comprueba si hay stock suficiente para una cantidad solicitada
    def hay_stock(self, cantidad: int) -> bool:

        return self.stock >= cantidad
    
    # Actualiza el stock del producto
    def actualizar_stock(self, cantidad: int) -> None:

        nuevo_stock = self.stock + cantidad
        if nuevo_stock < 0:
            raise ValueError(
                f"Stock insuficiente para '{self.nombre}': "
                f"stock actual {self.stock}, se intento restar {-cantidad}."
            )
        self.stock = nuevo_stock

    # Devuelve una representacion legible del producto
    def __str__(self) -> str:

        return (
            f"[{self.id[:8]}] {self.nombre} - {self.precio:.2f}EUR "
            f"(stock: {self.stock})"
        )

#  Producto electronico, con meses de garantia adicionales
class ProductoElectronico(Producto):
    
    # Inicializa un producto electronico

    def __init__(
        self, nombre: str, precio: float, stock: int, meses_garantia: int
    ) -> None:

        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = meses_garantia

    # Devuelve una representacion legible del producto electronico
    def __str__(self) -> str:
        
        return f"{super().__str__()} | Garantia: {self.meses_garantia} meses"


# Producto de ropa, con talla y color adicionales
class ProductoRopa(Producto):
    
    # Inicializa un producto de ropa
    def __init__(
        self, nombre: str, precio: float, stock: int, talla: str, color: str
    ) -> None:
        
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    # Devuelve una representacion legible del producto de ropa
    def __str__(self) -> str:
        
        return f"{super().__str__()} | Talla: {self.talla}, Color: {self.color}"
