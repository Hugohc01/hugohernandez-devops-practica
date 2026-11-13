"""Punto de entrada de la API REST de la tienda online"""

import os
from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware

from models.pedido import Pedido
from models.producto import Producto, ProductoElectronico, ProductoRopa
from models.usuario import Cliente, Usuario
from schemas import (
    PedidoCreate,
    PedidoItemRead,
    PedidoRead,
    ProductoCreate,
    ProductoRead,
    UsuarioCreate,
    UsuarioRead,
)
from services.tienda_service import (
    OperacionNoValida,
    RecursoNoEncontrado,
    StockInsuficiente,
    TiendaService,
    UsuarioDuplicado,
)

app = FastAPI(
    title="Tienda online API",
    description="API REST que expone la logica de TiendaService.",
    version="1.0.0",
)

# CORS: permite que el frontend (abierto desde otro origen, p. ej. un
# fichero HTML local o http://localhost:5500) pueda llamar a la API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clave necesaria para crear usuarios administradores.
# Se envia en la cabecera HTTP "X-Admin-Token". Puede cambiarse aqui o con la
# variable de entorno ADMIN_TOKEN. Si no se define, nadie puede crear administradores.
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
if not ADMIN_TOKEN:
    print("AVISO: ADMIN_TOKEN no definida; la creacion de administradores esta desactivada.")

# Unica instancia del servicio: todos los clientes (/docs, cliente Python y
# frontend) trabajan sobre los mismos datos mientras el servidor este activo.
tienda = TiendaService()


# ----------------------------------------------------------------------
# Datos de ejemplo (para que la tienda no arranque vacia)
# ----------------------------------------------------------------------

def cargar_datos_ejemplo(servicio: TiendaService) -> None:
    servicio.registrar_usuario("cliente", "Fry", "fry@futurama.com", direccion="Calle Bender 23")
    servicio.registrar_usuario("cliente", "Teo", "losada@brothers.com", direccion="Calle bb 69")
    servicio.registrar_usuario("administrador", "diosito", "jesus@divino.com")
    servicio.anadir_producto("electronico", "Portatil", 899.99, 10, meses_garantia=24)
    servicio.anadir_producto("electronico", "Movil", 499.99, 15, meses_garantia=12)
    servicio.anadir_producto("ropa", "Camiseta", 19.99, 50, talla="M", color="Negro")
    servicio.anadir_producto("generico", "Mochila", 29.99, 20)


cargar_datos_ejemplo(tienda)


# ----------------------------------------------------------------------
# Conversores: objetos del dominio -> esquemas de respuesta
# ----------------------------------------------------------------------

def usuario_a_read(usuario: Usuario) -> UsuarioRead:
    return UsuarioRead(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        es_admin=usuario.is_admin(),
        direccion_postal=usuario.direccion if isinstance(usuario, Cliente) else None,
    )


def producto_a_read(producto: Producto) -> ProductoRead:
    if isinstance(producto, ProductoElectronico):
        return ProductoRead(
            id=producto.id, tipo="electronico", nombre=producto.nombre,
            precio=producto.precio, stock=producto.stock,
            meses_garantia=producto.meses_garantia,
        )
    if isinstance(producto, ProductoRopa):
        return ProductoRead(
            id=producto.id, tipo="ropa", nombre=producto.nombre,
            precio=producto.precio, stock=producto.stock,
            talla=producto.talla, color=producto.color,
        )
    return ProductoRead(
        id=producto.id, tipo="generico", nombre=producto.nombre,
        precio=producto.precio, stock=producto.stock,
    )


def pedido_a_read(pedido: Pedido) -> PedidoRead:
    items = [
        PedidoItemRead(
            producto_id=producto.id,
            nombre=producto.nombre,
            precio_unitario=producto.precio,
            cantidad=cantidad,
            subtotal=round(producto.precio * cantidad, 2),
        )
        for producto, cantidad in pedido.productos
    ]
    return PedidoRead(
        id=pedido.id,
        fecha=pedido.fecha,
        cliente_id=pedido.cliente.id,
        cliente_nombre=pedido.cliente.nombre,
        total=round(pedido.calcular_total(), 2),
        items=items,
    )


# ----------------------------------------------------------------------
# Endpoints de usuarios
# ----------------------------------------------------------------------

@app.post(
    "/usuarios",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios"],
    responses={
        403: {"description": "Falta la clave de administrador o es incorrecta"},
        409: {"description": "Email ya registrado"},
    },
)
def crear_usuario(
    datos: UsuarioCreate,
    x_admin_token: Optional[str] = Header(
        None, description="Solo necesaria para crear usuarios de tipo administrador"
    ),
):
    # Cualquiera puede registrarse como cliente, pero para crear un
    # administrador hay que enviar la clave en la cabecera X-Admin-Token
    if datos.tipo == "administrador" and (not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se necesita una clave de administrador valida (cabecera X-Admin-Token).",
        )
    try:
        usuario = tienda.registrar_usuario(
            datos.tipo, datos.nombre, datos.email, direccion=datos.direccion_postal or ""
        )
    except UsuarioDuplicado as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except OperacionNoValida as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return usuario_a_read(usuario)


@app.get("/usuarios", response_model=List[UsuarioRead], tags=["Usuarios"])
def listar_usuarios():
    return [usuario_a_read(u) for u in tienda.listar_usuarios()]


@app.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioRead,
    tags=["Usuarios"],
    responses={404: {"description": "Usuario no encontrado"}},
)
def obtener_usuario(usuario_id: str):
    usuario = tienda.obtener_usuario(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"El usuario '{usuario_id}' no existe.")
    return usuario_a_read(usuario)


# ----------------------------------------------------------------------
# Endpoints de productos
# ----------------------------------------------------------------------

@app.post(
    "/productos",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Productos"],
)
def crear_producto(datos: ProductoCreate):
    try:
        producto = tienda.anadir_producto(
            datos.tipo, datos.nombre, datos.precio, datos.stock,
            meses_garantia=datos.meses_garantia,
            talla=datos.talla,
            color=datos.color,
        )
    except OperacionNoValida as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return producto_a_read(producto)


@app.get("/productos", response_model=List[ProductoRead], tags=["Productos"])
def listar_productos():
    return [producto_a_read(p) for p in tienda.listar_productos()]


@app.get(
    "/productos/{producto_id}",
    response_model=ProductoRead,
    tags=["Productos"],
    responses={404: {"description": "Producto no encontrado"}},
)
def obtener_producto(producto_id: str):
    producto = tienda.obtener_producto(producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail=f"El producto '{producto_id}' no existe.")
    return producto_a_read(producto)


@app.delete(
    "/productos/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Productos"],
    responses={404: {"description": "Producto no encontrado"}},
)
def eliminar_producto(producto_id: str):
    if not tienda.eliminar_producto(producto_id):
        raise HTTPException(status_code=404, detail=f"El producto '{producto_id}' no existe.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ----------------------------------------------------------------------
# Endpoints de pedidos
# ----------------------------------------------------------------------

@app.post(
    "/pedidos",
    response_model=PedidoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Pedidos"],
    responses={
        400: {"description": "El usuario no es un cliente"},
        404: {"description": "Cliente o producto no encontrado"},
        409: {"description": "Stock insuficiente"},
    },
)
def crear_pedido(datos: PedidoCreate):
    lineas = [(item.producto_id, item.cantidad) for item in datos.items]
    try:
        pedido = tienda.realizar_pedido(datos.cliente_id, lineas)
    except RecursoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except OperacionNoValida as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except StockInsuficiente as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return pedido_a_read(pedido)


@app.get(
    "/usuarios/{cliente_id}/pedidos",
    response_model=List[PedidoRead],
    tags=["Pedidos"],
    responses={404: {"description": "Usuario no encontrado"}},
)
def listar_pedidos_cliente(cliente_id: str):
    if tienda.obtener_usuario(cliente_id) is None:
        raise HTTPException(status_code=404, detail=f"El usuario '{cliente_id}' no existe.")
    return [pedido_a_read(p) for p in tienda.listar_pedidos_usuario(cliente_id)]


# ----------------------------------------------------------------------
# Arranque para hacerlo como un script normal
# HOST y PORT se pueden cambiar con variables de entorno:
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

if __name__ == "__main__":
    import uvicorn

    print(f"API en http://localhost:{PORT}  ·  documentacion en http://localhost:{PORT}/docs")
    uvicorn.run(app, host=HOST, port=PORT)
