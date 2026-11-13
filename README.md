# Tienda online – API REST con FastAPI

**Autor:** Hugo Hernández

## Descripción

Aplicación Python que implementa una **tienda online** expuesta como servicio REST.

- **API REST** (FastAPI + Pydantic) que gestiona usuarios (clientes y administradores),
  productos (genéricos, electrónicos y de ropa) y pedidos, con control de stock.
- **Cliente Python** (`requests`) que consume la API sin importar nada del servidor.
- **Frontend web** (HTML + JavaScript) que permite usar la tienda desde el navegador.

Los datos se guardan en memoria: al reiniciar el servidor vuelven los datos de ejemplo.

## Estructura del proyecto

```
.
├── src/
│   ├── Tienda_online/          ← API REST (servidor FastAPI)
│   │   ├── main.py             ← endpoints (punto de entrada de la API)
│   │   ├── schemas.py          ← esquemas Pydantic (Create / Read)
│   │   ├── demo_consola.py     ← demo por consola (Práctica 1)
│   │   ├── models/             ← Producto, Usuario, Pedido
│   │   └── services/
│   │       └── tienda_service.py
│   ├── cliente/
│   │   └── cliente.py          ← cliente Python con requests
│   └── frontend/
│       └── index.html          ← frontend web
├── requirements.txt
└── README.md
```

## Ejecución en local (sin Docker)

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

cd src/Tienda_online
uvicorn main:app --reload
```

- Documentación interactiva: http://localhost:8000/docs
- Cliente de prueba (en otra terminal): `python src/cliente/cliente.py`
- Frontend: abrir `src/frontend/index.html` en el navegador.

## Endpoints

| Método | Ruta | Respuesta correcta | Errores |
|---|---|---|---|
| POST | `/usuarios` | 201 | 403 administrador sin clave válida, 409 email repetido, 422 datos no válidos |
| GET | `/usuarios` | 200 | |
| GET | `/usuarios/{usuario_id}` | 200 | 404 |
| POST | `/productos` | 201 | 422 (p. ej. ropa sin talla/color o talla no válida) |
| GET | `/productos` | 200 | |
| GET | `/productos/{producto_id}` | 200 | 404 |
| DELETE | `/productos/{producto_id}` | 204 | 404 |
| POST | `/pedidos` | 201 | 404 cliente/producto, 400 no es cliente, 409 sin stock |
| GET | `/usuarios/{cliente_id}/pedidos` | 200 | 404 |

## Validaciones y permisos

- **Crear administradores** requiere enviar una clave en la cabecera HTTP `X-Admin-Token`. La
  clave se define con la variable de entorno `ADMIN_TOKEN` y **no está escrita en el código**.
  Si la variable no está definida, nadie puede crear administradores (403).
- **Talla:** solo `XS`, `S`, `M`, `L`, `XL` o `XXL` (se aceptan minúsculas).
- **Atributos por tipo:** `meses_garantia` solo en electrónicos; `talla` y `color` solo en ropa.
