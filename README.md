# Sistema Inteligente de Atencion al Cliente con OpenAI API

Backend local desarrollado en Python y FastAPI para atencion automatizada de clientes, ventas, soporte, CRM, cotizaciones, inventario, auditoria, metricas y uso controlado de OpenAI API.

## Funcionalidades principales

- Atencion al cliente por API.
- Clasificacion de intencion.
- Base de conocimiento local.
- Reglas de negocio y seguridad.
- Orquestador de decisiones.
- Integracion controlada con OpenAI API.
- Modo mock para no gastar creditos.
- Persistencia con SQLite.
- Leads comerciales.
- Tickets de soporte.
- Cotizaciones comerciales.
- Inventario y reservas.
- CRM basico de clientes.
- Metricas operativas.
- Auditoria.
- Panel administrativo por API.

## Requisitos

- Windows 11
- Python 3.13 o superior
- Git
- PowerShell

## Instalacion en Windows 11

Ejecutar en PowerShell dentro de la carpeta del proyecto:

python -m venv .venv

.\.venv\Scripts\python.exe -m pip install --upgrade pip

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

## Configuracion

Crear un archivo .env tomando como base .env.example.

Modo seguro sin gastar creditos:

AI_MODE=mock
OPENAI_API_KEY=
AI_USE_OPENAI_ANALYSIS=false
AI_USE_OPENAI_REPLY=false

Para usar OpenAI real:

AI_MODE=openai
OPENAI_API_KEY=TU_API_KEY
AI_USE_OPENAI_ANALYSIS=true
AI_USE_OPENAI_REPLY=false

Importante: no subir el archivo .env al repositorio.

## Ejecutar servidor local

.\run_dev.bat

Servidor local:

http://127.0.0.1:3001

## Verificar estado

Invoke-RestMethod -Uri "http://127.0.0.1:3001/health" -Method Get

## Ejecutar pruebas

.\.venv\Scripts\python.exe -m pytest tests -q

Resultado esperado:

48 passed

## Endpoints principales

Chat:
POST /api/chat

IA:
GET  /api/ai/status
POST /api/ai/analyze
POST /api/ai/smoke-test
GET  /api/ai/logs

Administracion:
GET /api/admin/dashboard
GET /api/admin/conversations
GET /api/admin/leads
GET /api/admin/tickets
GET /api/admin/quote-drafts

Clientes CRM:
GET   /api/customers
GET   /api/customers/{customer_id}
PATCH /api/customers/{customer_id}
GET   /api/customers/{customer_id}/commercial-summary

Cotizaciones:
GET   /api/quotes
POST  /api/quotes/from-draft/{quote_draft_id}
PATCH /api/quotes/{quote_id}/approve
PATCH /api/quotes/{quote_id}/send

Inventario:
GET  /api/inventory
POST /api/inventory/adjust
POST /api/inventory/reserve-from-quote/{quote_id}

## Seguridad

El archivo .env esta ignorado por Git para evitar subir llaves privadas de OpenAI.

## Estado del proyecto

Proyecto funcional hasta CAPA 12.
