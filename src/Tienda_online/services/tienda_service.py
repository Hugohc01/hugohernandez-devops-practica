"""Modulo que define la capa de servicios de la tienda."""

from typing import Dict, List, Optional, Tuple

from models.pedido import Pedido
from models.producto import Producto, ProductoElectronico, ProductoRopa
from models.usuario import Administrador, Cliente, Usuario


# Excepciones propias del servicio.
# Heredan de ValueError para seguir siendo compatibles con el codigo de la
# Practica 1, pero permiten a la API distinguir el tipo de error y devolver
# el codigo HTTP adecuado (404, 400, 409...).
class RecursoNoEncontrado(ValueError):
    """Se lanza cuando un usuario o producto no existe."""


class OperacionNoValida(ValueError):
    """Se lanza cuando la operacion no esta permitida (tipo incorrecto, etc.)."""


class StockInsuficiente(ValueError):
    """Se lanza cuando no hay stock suficiente para un pedido."""


class UsuarioDuplicado(ValueError):
    """Se lanza cuando ya existe un usuario con el mismo email."""


# Servicio que centraliza las operaciones de la tienda online
class TiendaService:

    # Inicializa el servicio con inventario, usuarios y pedidos vacios
    def __init__(self) -> None:

        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []

    # ------------------------------------------------------------------
    # Usuarios
    # ------------------------------------------------------------------

    # Registra un nuevo usuario en la tienda
    def registrar_usuario(self, tipo: str, nombre: str, email: str, **kwargs) -> Usuario:

        if any(u.email.lower() == email.lower() for u in self.usuarios.values()):
            raise UsuarioDuplicado(f"Ya existe un usuario con el email '{email}'.")

        tipo_normalizado = tipo.strip().lower()
        if tipo_normalizado == "cliente":
            usuario: Usuario = Cliente(nombre, email, kwargs.get("direccion", ""))
        elif tipo_normalizado == "administrador":
            usuario = Administrador(nombre, email)
        else:
            raise OperacionNoValida(f"Tipo de usuario no reconocido: '{tipo}'.")

        self.usuarios[usuario.id] = usuario
        return usuario

    # Devuelve un usuario a partir de su id (o None si no existe)
    def obtener_usuario(self, usuario_id: str) -> Optional[Usuario]:
        return self.usuarios.get(usuario_id)

    # Lista todos los usuarios registrados
    def listar_usuarios(self) -> List[Usuario]:
        return list(self.usuarios.values())

    # ------------------------------------------------------------------
    # Productos
    # ------------------------------------------------------------------

    # Añade un nuevo producto al inventario de la tienda
    def anadir_producto(self, tipo: str, nombre: str, precio: float, stock: int, **kwargs) -> Producto:

        tipo_normalizado = tipo.strip().lower()
        if tipo_normalizado == "electronico":
            producto: Producto = ProductoElectronico(
                nombre, precio, stock, kwargs.get("meses_garantia", 0)
            )
        elif tipo_normalizado == "ropa":
            producto = ProductoRopa(
                nombre, precio, stock, kwargs.get("talla", ""), kwargs.get("color", "")
            )
        elif tipo_normalizado == "generico":
            producto = Producto(nombre, precio, stock)
        else:
            raise OperacionNoValida(f"Categoria de producto no reconocida: '{tipo}'.")

        self.productos[producto.id] = producto
        return producto

    # Devuelve un producto a partir de su id (o None si no existe)
    def obtener_producto(self, producto_id: str) -> Optional[Producto]:
        return self.productos.get(producto_id)

    # Elimina un producto del inventario a partir de su identificador
    def eliminar_producto(self, producto_id: str) -> bool:
        if producto_id in self.productos:
            del self.productos[producto_id]
            return True
        return False

    # Lista todos los productos disponibles en la tienda
    def listar_productos(self) -> List[Producto]:

        return list(self.productos.values())

    # ------------------------------------------------------------------
    # Pedidos
    # ------------------------------------------------------------------

    # Realiza un pedido para un cliente, verificando usuario y stock
    def realizar_pedido(
        self, usuario_id: str, productos_cantidades: List[Tuple[str, int]]
    ) -> Pedido:

        usuario = self.usuarios.get(usuario_id)
        if usuario is None:
            raise RecursoNoEncontrado(f"El usuario con id '{usuario_id}' no existe.")
        if not isinstance(usuario, Cliente):
            raise OperacionNoValida("Solo los usuarios de tipo Cliente pueden realizar pedidos.")

        # Se agrupan las cantidades por producto por si el mismo producto
        # aparece en varias lineas del pedido
        cantidades_totales: Dict[str, int] = {}
        for producto_id, cantidad in productos_cantidades:
            cantidades_totales[producto_id] = cantidades_totales.get(producto_id, 0) + cantidad

        for producto_id, cantidad in cantidades_totales.items():
            producto = self.productos.get(producto_id)
            if producto is None:
                raise RecursoNoEncontrado(f"El producto con id '{producto_id}' no existe.")
            if not producto.hay_stock(cantidad):
                raise StockInsuficiente(
                    f"Stock insuficiente para '{producto.nombre}' "
                    f"(solicitado: {cantidad}, disponible: {producto.stock})."
                )

        lineas_pedido: List[Tuple[Producto, int]] = [
            (self.productos[producto_id], cantidad)
            for producto_id, cantidad in productos_cantidades
        ]

        # una vez comprobado que todo es valido, se descuenta el stock
        for producto, cantidad in lineas_pedido:
            producto.actualizar_stock(-cantidad)

        pedido = Pedido(usuario, lineas_pedido)
        self.pedidos.append(pedido)
        return pedido

    # Lista los pedidos de un usuario ordenados por fecha
    def listar_pedidos_usuario(self, usuario_id: str) -> List[Pedido]:

        pedidos_usuario = [p for p in self.pedidos if p.cliente.id == usuario_id]
        return sorted(pedidos_usuario, key=lambda p: p.fecha)
