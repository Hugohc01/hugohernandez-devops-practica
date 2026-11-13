from services.tienda_service import TiendaService


def main() -> None:
    tienda = TiendaService()

    # Registro de usuarios
    cliente1 = tienda.registrar_usuario(
        "cliente", "Fry", "fry@futurama.com", direccion="Calle Bender 23"
    )
    cliente2 = tienda.registrar_usuario(
        "cliente", "Teo", "Losada@brothers.com", direccion="Calle bb 69"
    )
    cliente3 = tienda.registrar_usuario(
        "cliente", "Bender", "bender@planetexpress.com", direccion="Calle Delivery 3"
    )
    admin = tienda.registrar_usuario(
        "administrador", "diosito", "jesus@divino.com"
    )

    print("Usuarios registrados")
    for usuario in [cliente1, cliente2, cliente3, admin]:
        print(f"{usuario} | is_admin: {usuario.is_admin()}")

    # Alta de productos
    portatil = tienda.anadir_producto(
        "electronico", "Portatil", 899.99, 10, meses_garantia=24
    )
    movil = tienda.anadir_producto(
        "electronico", "Movil", 499.99, 15, meses_garantia=12
    )
    camiseta = tienda.anadir_producto(
        "ropa", "Camiseta", 19.99, 50, talla="M", color="Negro"
    )
    pantalon = tienda.anadir_producto(
        "ropa", "Pantalon", 39.99, 30, talla="L", color="Azul"
    )
    mochila = tienda.anadir_producto("generico", "Mochila", 29.99, 20)

    print("\nInventario tras el alta de productos")
    for producto in tienda.listar_productos():
        print(producto)

    # Simulacion de pedidos 
    print("\nRealizando pedidos")
    pedido1 = tienda.realizar_pedido(
        cliente1.id, [(portatil.id, 1), (camiseta.id, 2)]
    )
    print(pedido1)

    pedido2 = tienda.realizar_pedido(
        cliente2.id, [(movil.id, 1), (mochila.id, 1)]
    )
    print(pedido2)

    pedido3 = tienda.realizar_pedido(
        cliente3.id, [(pantalon.id, 3)]
    )
    print(pedido3)

    # Historico de pedidos de un cliente
    print(f"\nHistorico de pedidos de {cliente1.nombre}")
    for pedido in tienda.listar_pedidos_usuario(cliente1.id):
        print(pedido)

    # Stock actualizado tras los pedidos
    print("\nInventario tras los pedidos (stock actualizado)")
    for producto in tienda.listar_productos():
        print(producto)


if __name__ == "__main__":
    main()
