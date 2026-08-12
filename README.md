# Notifications API
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/MicaVillalobos/notifications-api/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/MicaVillalobos/notifications-api/tree/main)
[![Coverage Status](https://coveralls.io/repos/github/MicaVillalobos/notifications-api/badge.svg?branch=main)](https://coveralls.io/github/MicaVillalobos/notifications-api?branch=main)
[![Python](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED)](https://www.docker.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

API REST para la gestión de notificaciones de usuarios autenticados, con envío por múltiples canales (email, SMS, push). Cada usuario gestiona únicamente sus propias notificaciones.

El envío por cada canal está **simulado** (registrado vía logging), con la lógica específica de cada uno según lo pedido en la consigna.

---

## Stack técnico

- **Lenguaje / framework:** Python 3.14, FastAPI
- **Base de datos / ORM:** PostgreSQL, SQLAlchemy, Alembic (migraciones)
- **Validación:** Pydantic v2
- **Autenticación:** JWT (python-jose) + bcrypt
- **Testing:** pytest (integración), SQLite in-memory
- **Tooling:** uv (gestor de paquetes), Ruff (linter + formatter)
- **Infraestructura:** Docker + Docker Compose
- **CI:** CircleCI (lint + tests + coverage)

---

## Cómo levantarlo (Docker)

Requisitos: Docker y Docker Compose.

1. Clonar el repositorio.
2. Copiar el archivo de ejemplo de variables de entorno:
   ```bash
   cp .env.example .env
   ```
   Los valores por defecto sirven para desarrollo local.
3. Levantar el sistema completo (app + base de datos):
   ```bash
   docker compose up --build
   ```

La API queda disponible en `http://localhost:8000` y la documentación interactiva (Swagger UI) en `http://localhost:8000/docs`.

El contenedor de la app corre las migraciones de Alembic automáticamente antes de arrancar, así que la base queda con sus tablas creadas sin pasos manuales.

---

## Endpoints

Todos los endpoints de notificaciones y `/auth/me` requieren un token de acceso válido en el header `Authorization: Bearer <token>`.

| Método | Ruta | Descripción | Requiere auth |
|--------|------|-------------|:---:|
| POST | `/auth/register` | Registro de usuario (email + password) | No |
| POST | `/auth/login` | Login; devuelve access + refresh token | No |
| POST | `/auth/refresh` | Renueva el access token con el refresh token | No |
| GET | `/auth/me` | Datos del usuario autenticado | Sí |
| POST | `/notifications` | Crea una notificación y ejecuta el envío | Sí |
| GET | `/notifications` | Lista las notificaciones propias | Sí |
| GET | `/notifications/{id}` | Obtiene una notificación propia | Sí |
| PUT | `/notifications/{id}` | Actualiza una notificación propia (parcial) | Sí |
| DELETE | `/notifications/{id}` | Elimina una notificación propia | Sí |
| GET | `/health` | Health check | No |

---

## Decisiones técnicas

### Arquitectura en capas (router → service → repository → model)

La lógica de negocio vive en los *services*, el acceso a datos en los *repositories*, y los modelos son anémicos (solo datos). Cada capa tiene una única responsabilidad y es testeable de forma aislada. El router nunca accede a la base directamente: se limita a recibir el request, delegar y traducir el resultado a HTTP.

### Sistema de canales: patrón Strategy + registry

Cada canal (email, SMS, push) es una estrategia que implementa una interfaz común (`Canal`, una clase base abstracta con el método `enviar`). Un *registry* (diccionario `CanalTipo → Canal`) traduce el tipo de canal —que viaja por HTTP y se persiste como un enum— a la instancia que sabe enviar.

Este diseño cumple el **Open/Closed Principle**: agregar un canal nuevo es crear una clase con su `enviar` e inscribirla en el registry, **sin modificar** el service ni los canales existentes. Es la respuesta directa al requisito "agregar un nuevo canal no debe implicar modificar la lógica existente".

El service orquesta (busca la estrategia y dispara el envío) pero no conoce la lógica concreta de cada canal: esa responsabilidad vive dentro de cada estrategia.

### Autorización derivada del token, no del request

El `user_id` dueño de una notificación **nunca** viene en el body: se deriva del JWT autenticado. Las queries filtran por dueño combinando `id` y `user_id`, de modo que un usuario no puede leer, modificar ni borrar notificaciones ajenas.

Un recurso de otro usuario devuelve **404, no 403**: así no se revela que el recurso existe. La autorización es estructural (está en la query), no un chequeo posterior que se pueda olvidar.

### Flujo persistir-luego-enviar

Al crear una notificación se persiste primero con estado `pendiente`, luego se intenta el envío, y finalmente se actualiza el estado a `enviado` o `fallido`. De esta forma queda trazabilidad aunque el envío falle: la notificación no se pierde y su estado refleja el resultado. Crear el recurso y enviarlo son dos eventos distintos, y el campo `status` representa esa diferencia.

### Autenticación JWT (access + refresh)

Access token de vida corta (30 min) para autenticar cada request, y refresh token (7 días) para renovar sin re-login. Los passwords se hashean con bcrypt (que incluye salt y es deliberadamente lento contra fuerza bruta). El payload del JWT no lleva datos sensibles: es Base64 (no encriptado), y solo garantiza integridad vía la firma.

### Enums de canal y estado

El canal y el estado de envío se modelan como enums (`StrEnum`), validados en el borde por Pydantic: un canal inválido se rechaza con un 422 antes de tocar la lógica. Esto hace imposible representar un estado inválido y documenta los valores válidos en la API automáticamente.

---

## Tests

```bash
uv run pytest --cov=app
```

Los tests son de **integración**: prueban el flujo completo por HTTP (router → service → repository → base). Usan **SQLite en memoria** vía `dependency_overrides`, de modo que corren aislados de la base de desarrollo y sin necesitar infraestructura externa (esto también mantiene el CI simple).

Incluyen tests de **aislamiento entre usuarios**, que verifican que un usuario no puede acceder a recursos de otro en ninguna operación (get, update, delete, list).

Cobertura actual: ~97%. Lo no cubierto son bordes deliberados (el `get_db` de producción, sustituido en los tests por diseño; el health check; defensas internas que la validación de Pydantic ya previene aguas arriba).

---

## Estructura del proyecto

```
app/
├── main.py            # crea la app e incluye los routers
├── database.py        # engine, sesión, Base, get_db
├── dependencies.py    # get_current_user (auth)
├── core/              # config (settings) y security (JWT, bcrypt)
├── models/            # entidades ORM (anémicas) y enums
├── schemas/           # DTOs Pydantic (entrada/salida)
├── repositories/      # acceso a datos
├── services/          # lógica de negocio
├── channels/          # Strategy de canales + registry
└── routers/           # endpoints HTTP
tests/                 # tests de integración
alembic/               # migraciones
```

---

## Decisiones de scope y mejoras futuras

Cosas dejadas afuera **a propósito** por el alcance del ejercicio, con la nota de cómo se resolverían:

- **Envío real por los canales.** Hoy el envío está simulado (log). Un envío real integraría un proveedor por canal (SMTP/SendGrid para email, Twilio para SMS, FCM/APNs para push), detrás de la misma interfaz `Canal` —sin tocar el resto del sistema, gracias al diseño Strategy.
- **Validación del destinatario real.** El email del destinatario vive en `users` y el token de dispositivo (para push) requeriría un subsistema de registro de dispositivos por usuario. Ambos exceden el scope; el paso de validación queda representado en cada canal.
- **Refresh token rotation completa.** El endpoint de refresh emite un par nuevo, pero no invalida el refresh anterior. La rotation con invalidación requeriría persistir los refresh tokens (o una blacklist en Redis) para detectar reuso.
- **Envío asíncrono / en segundo plano.** Hoy el envío es sincrónico dentro del request. Para volumen real convendría encolarlo (por ejemplo con una cola de tareas) y procesarlo aparte, dejando el request más rápido.
- **Borrado lógico (soft delete).** Se usa hard delete. Si se necesitara auditoría o recuperación, un flag `is_deleted` mantendría el historial.