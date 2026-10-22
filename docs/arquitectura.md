# Arquitectura de microservicios — SGB Universidad de Madeira

```mermaid
flowchart LR
    U([Usuario / Bibliotecario]) --> FE["Frontend<br/>Vue 3 + Vite"]
    FE -- "HTTP /api/*" --> GW["API Gateway<br/>Nginx"]

    GW -- "/api/catalog/*" --> CAT["catalog-service<br/>Django + DRF<br/>Recursos y colecciones"]
    GW -- "/api/library/*" --> LOA["loans-service<br/>Django + DRF<br/>Usuarios, préstamos,<br/>renovaciones, reservas, multas"]

    CAT --> MDB[("MongoDB<br/>recursos")]
    LOA --> SUP[("Supabase<br/>PostgreSQL")]

    LOA -. "HTTP interno: validar y<br/>actualizar ejemplares" .-> CAT
```

## Secuencia del flujo End-to-End (crear un préstamo)

```mermaid
sequenceDiagram
    actor B as Bibliotecario
    participant FE as Vue
    participant GW as API Gateway
    participant L as loans-service
    participant C as catalog-service
    participant PG as Supabase (Postgres)
    participant MG as MongoDB

    B->>FE: Prestar recurso
    FE->>GW: POST /api/library/loans
    GW->>L: POST /api/loans
    L->>PG: ¿usuario con multas pendientes?
    L->>C: GET /api/resources/{code}
    C->>MG: find({code})
    MG-->>C: recurso
    C-->>L: recurso (ejemplares disponibles)
    L->>C: PATCH ejemplares - 1
    C->>MG: update_one
    L->>PG: INSERT préstamo (fecha devolución según colección)
    PG-->>L: préstamo
    L-->>GW: 201 + préstamo
    GW-->>FE: 201
    FE-->>B: Muestra el préstamo y su vencimiento
```

## Responsabilidades
| Componente | Responsabilidad | Persistencia |
|---|---|---|
| Frontend (Vue) | UI; solo habla con el gateway | — |
| API Gateway (Nginx) | Enrutamiento por prefijo, CORS | — |
| catalog-service | Libros, diccionarios, revistas, mapas, equipos; estados y ejemplares | MongoDB (documentos con campos distintos por colección) |
| loans-service | Usuarios, préstamos, renovaciones, reservas, multas y reglas de negocio | Supabase / PostgreSQL (relacional, integridad referencial) |

Justificación de bases de datos: las colecciones tienen atributos heterogéneos (dimensiones en cm vs pulgadas, mapas sin ejemplares, ISSN vs ISBN), lo que encaja con documentos en MongoDB. Los préstamos, usuarios y multas son relacionales y transaccionales, lo que encaja con PostgreSQL.
