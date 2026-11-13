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
├── Dockerfile                  ← imagen de la API
├── .dockerignore               ← ficheros excluidos al construir la imagen
├── requirements.txt            ← dependencias con versiones fijadas
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

## Docker

La API se puede ejecutar en un contenedor sin instalar Python ni dependencias.
La imagen usa `python:3.12-slim`, instala las versiones fijadas de `requirements.txt`
y ejecuta la aplicación con un usuario sin privilegios (`appuser`).

### Construir la imagen

Desde la raíz del repositorio (donde está el `Dockerfile`):

```bash
docker build -t tienda-api:1.0 .
```

### Ejecutar el contenedor

```bash
# Básico: la API queda en http://localhost:8000
docker run --rm -p 8000:8000 --name tienda-api tienda-api:1.0

# Con clave de administrador (permite crear administradores)
docker run --rm -p 8000:8000 -e ADMIN_TOKEN=mi-clave-secreta --name tienda-api tienda-api:1.0

# En segundo plano, publicando la API en el puerto 9000 del equipo
docker run -d -p 9000:8000 --name tienda-api tienda-api:1.0
docker logs tienda-api      # ver la salida
docker stop tienda-api      # parar
```

`-p PUERTO_EQUIPO:8000` conecta un puerto de tu ordenador con el puerto 8000 del contenedor.

### Variables de entorno

| Variable | Obligatoria | Descripción |
|---|---|---|
| `ADMIN_TOKEN` | No | Clave que hay que enviar en la cabecera `X-Admin-Token` para crear usuarios administradores. Si no se define, la creación de administradores queda desactivada (403). |

Nunca se escribe la clave en el código ni en el repositorio: se pasa al arrancar con `-e`.

### Salida esperada y pruebas

Al arrancar, el contenedor muestra:

```
AVISO: ADMIN_TOKEN no definida; la creacion de administradores esta desactivada.   (solo si no se pasa ADMIN_TOKEN)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Pasos de prueba con el contenedor en marcha:

1. Abrir http://localhost:8000/docs: debe aparecer la documentación de la API.
2. `GET /productos` devuelve los productos de ejemplo (código 200).
3. Ejecutar el cliente de prueba, que recorre todo el flujo (crear usuario, productos y pedido):
   ```bash
   pip install -r requirements.txt
   python src/cliente/cliente.py
   ```
   Debe terminar con `Flujo completado correctamente.`
4. Abrir `src/frontend/index.html` en el navegador: debe indicar **Conectado**.

### Publicar y descargar la imagen (Docker Hub)

La imagen está publicada en Docker Hub como `<usuario-dockerhub>/tienda-api`.

```bash
# Publicar (tras docker login)
docker tag tienda-api:1.0 <usuario-dockerhub>/tienda-api:1.0
docker tag tienda-api:1.0 <usuario-dockerhub>/tienda-api:latest
docker push <usuario-dockerhub>/tienda-api:1.0
docker push <usuario-dockerhub>/tienda-api:latest

# Descargar y ejecutar en cualquier equipo con Docker
docker pull <usuario-dockerhub>/tienda-api:1.0
docker run --rm -p 8000:8000 <usuario-dockerhub>/tienda-api:1.0
```
