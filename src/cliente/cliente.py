"""Cliente Python de la API REST de la tienda online"""

import os
import sys
import time
import requests

# Mismo equipo: "http://localhost:8000"  |  Otro equipo: "http://<IP_DEL_SERVIDOR>:8000"
# Tambien se puede pasar como argumento: python cliente.py http://IP:8000
BASE_URL = os.environ.get("API_URL", "http://localhost:8000")

TIMEOUT = 5  # segundos maximos de espera por peticion


class ErrorAPI(Exception):
    """Error devuelto por la API (codigo HTTP distinto del esperado)."""


# Comprueba el codigo de estado y devuelve el JSON de la respuesta
def procesar_respuesta(respuesta: requests.Response, codigo_esperado: int):
    metodo = respuesta.request.method
    print(f"  {metodo} {respuesta.url} -> {respuesta.status_code}")

    if respuesta.status_code != codigo_esperado:
        try:
            detalle = respuesta.json().get("detail")
        except ValueError:
            detalle = respuesta.text
        raise ErrorAPI(
            f"{metodo} {respuesta.url} devolvio {respuesta.status_code} "
            f"(se esperaba {codigo_esperado}): {detalle}"
        )

    if respuesta.status_code == 204:  # sin contenido
        return None
    return respuesta.json()


# ----------------------------------------------------------------------
# Funciones que envuelven cada endpoint
# ----------------------------------------------------------------------

def crear_usuario(nombre, email, tipo="cliente", direccion_postal=None):
    datos = {"nombre": nombre, "email": email, "tipo": tipo, "direccion_postal": direccion_postal}
    r = requests.post(f"{BASE_URL}/usuarios", json=datos, timeout=TIMEOUT)
    return procesar_respuesta(r, 201)


def listar_usuarios():
    r = requests.get(f"{BASE_URL}/usuarios", timeout=TIMEOUT)
    return procesar_respuesta(r, 200)


def obtener_usuario(usuario_id):
    r = requests.get(f"{BASE_URL}/usuarios/{usuario_id}", timeout=TIMEOUT)
    return procesar_respuesta(r, 200)


def crear_producto(**datos):
    r = requests.post(f"{BASE_URL}/productos", json=datos, timeout=TIMEOUT)
    return procesar_respuesta(r, 201)


def listar_productos():
    r = requests.get(f"{BASE_URL}/productos", timeout=TIMEOUT)
    return procesar_respuesta(r, 200)


def crear_pedido(cliente_id, items):
    """items: lista de tuplas (producto_id, cantidad)."""
    datos = {
        "cliente_id": cliente_id,
        "items": [{"producto_id": pid, "cantidad": cant} for pid, cant in items],
    }
    r = requests.post(f"{BASE_URL}/pedidos", json=datos, timeout=TIMEOUT)
    return procesar_respuesta(r, 201)


def listar_pedidos_usuario(usuario_id):
    r = requests.get(f"{BASE_URL}/usuarios/{usuario_id}/pedidos", timeout=TIMEOUT)
    return procesar_respuesta(r, 200)


# ----------------------------------------------------------------------
# Flujo de prueba
# ----------------------------------------------------------------------

def main():
    print(f"Usando la API en: {BASE_URL}\n")

    # Sufijo para que el email sea unico y el script se pueda repetir
    sufijo = int(time.time())

    # 1. Crear un usuario
    print("1) Crear usuario")
    usuario = crear_usuario(
        "Amy", f"amy{sufijo}@planetexpress.com", "cliente", "Calle Marte 3"
    )
    print(f"  Creado: {usuario['nombre']} (id={usuario['id']})\n")

    # 2. Consultar la lista de usuarios
    print("2) Listar usuarios")
    for u in listar_usuarios():
        rol = "admin" if u["es_admin"] else "cliente"
        print(f"  - {u['nombre']:<10} {u['email']:<35} [{rol}]")
    print()

    # 3. Crear varios productos
    print("3) Crear productos")
    tablet = crear_producto(tipo="electronico", nombre="Tablet", precio=299.5, stock=8, meses_garantia=24)
    sudadera = crear_producto(tipo="ropa", nombre="Sudadera", precio=35.0, stock=20, talla="L", color="Gris")
    taza = crear_producto(tipo="generico", nombre="Taza", precio=7.95, stock=100)
    for p in (tablet, sudadera, taza):
        print(f"  Creado: {p['nombre']} ({p['tipo']}) id={p['id']}")
    print()

    # 4. Consultar la lista de productos
    print("4) Listar productos")
    for p in listar_productos():
        print(f"  - {p['nombre']:<10} {p['precio']:>8.2f} EUR  stock={p['stock']:<4} ({p['tipo']})")
    print()

    # 5. Crear un pedido para el usuario creado
    print("5) Crear pedido")
    pedido = crear_pedido(usuario["id"], [(tablet["id"], 1), (taza["id"], 2)])
    print(f"  Pedido {pedido['id'][:8]} creado. Total: {pedido['total']:.2f} EUR\n")

    # 6. Consultar los pedidos del usuario
    print(f"6) Pedidos de {usuario['nombre']}")
    for p in listar_pedidos_usuario(usuario["id"]):
        print(f"  Pedido {p['id'][:8]} ({p['fecha'][:19]}) total {p['total']:.2f} EUR")
        for item in p["items"]:
            print(f"     - {item['nombre']} x{item['cantidad']} = {item['subtotal']:.2f} EUR")
    print()

    # Comprobacion extra: el stock de la tablet ha bajado
    print("Extra) Comprobar errores y stock")
    stock_tablet = next(p for p in listar_productos() if p["id"] == tablet["id"])["stock"]
    print(f"  Stock de la tablet tras el pedido: {stock_tablet} (antes 8)")

    # Comprobacion extra: un pedido sin stock suficiente devuelve 409
    try:
        crear_pedido(usuario["id"], [(tablet["id"], 999)])
    except ErrorAPI as e:
        print(f"  Error esperado: {e}")

    print("\nFlujo completado correctamente.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1].rstrip("/")
    try:
        main()
    except requests.exceptions.ConnectionError:
        print(f"\nNo se pudo conectar con {BASE_URL}. "
              "Comprueba que el servidor esta arrancado y que la IP/puerto son correctos.")
        sys.exit(1)
    except ErrorAPI as e:
        print(f"\nError de la API: {e}")
        sys.exit(1)
