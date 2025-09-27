# Memory Service

A Python-based service responsible for storing long-term and short-term conversation context for users.

---

## Overview

This service manages two types of data:

- **Public data**: Business-related information (e.g., loan amount, name, surname) that can safely be shared with agents.  
- **Private data**: Sensitive or temporary information (e.g., JWTs, access tokens, external IDs like Telegram username, email, or phone number).

All data is stored and exchanged as **JSON**. Nested JSON structures are supported.

---

## Features

- **RESTful API** following the **OpenAPI 3.0** specification  
- **Deep merge functionality** for updating JSON documents  
- **Separation of concerns** between public and private data  
- **Correlation IDs** for request tracing and debugging  
- **In-memory storage** by default (pluggable backend possible)  
- **Comprehensive test suite** with pytest  

---

## API Endpoints

### Public Data Management

- `GET /v1/conversations/{conversation_id}/public-data`  
  Retrieve public conversation data.  

- `POST /v1/conversations/{conversation_id}/public-data`  
  Update public conversation data (deep merge).  

- `DELETE /v1/conversations/{conversation_id}/public-data`  
  Delete all public conversation data for a conversation.  

---

### Private Data Management

- `GET /v1/conversations/{conversation_id}/private-data`  
  Retrieve private conversation data.  

- `POST /v1/conversations/{conversation_id}/private-data`  
  Update private conversation data (deep merge).  

- `DELETE /v1/conversations/{conversation_id}/private-data`  
  Delete all private conversation data for a conversation.  

---

### Health Check

- `GET /healthcheck`  
  Returns service health status. Example:  
  ```json
  {"status": "ok"}

## Headers

- **`aplm-correlation-id`**: Correlation/tracing ID.  
  If provided, it will be echoed back in the response headers and included in logs for easier debugging.

---

## Data Merge Behavior

`POST` updates behave as **deep merges**:

- Override existing keys at any level.  
- Preserve unrelated keys.  
- Arrays are **fully replaced** (no concatenation).  
- `null` values are allowed and explicitly overwrite existing values.  

### Example

Updating:

```json
{
  "foo": "bar",
  "k2": {
    "sk3": 15,
    "sk4": null
  },
  "k3": [1, 2, 3, "foo"]
}
```
with:

```json
{
  "k2": {
    "sk4": "val4",
    "sk5": 42
  },
  "k3": null,
  "k10": "val10"
}
```
results in:

```json
{
  "foo": "bar",
  "k2": {
    "sk3": 15,
    "sk4": "val4",
    "sk5": 42
  },
  "k3": null,
  "k10": "val10"
}
```
Running the Service
-------------------

### Requirements

-   Python 3.10+

-   Dependencies: FastAPI, Uvicorn, Pydantic

Install with:

`pip install -r requirements.txt`

### Start the server

`uvicorn main:app --reload --port 8000`

Visit Swagger UI at: <http://localhost:8000/docs>

* * * * *

Testing
-------

Run the full test suite with:

`pytest -q`

### Tests cover:

-   Healthcheck (`healthcheck.py`)

-   Public/private data lifecycle (`api_test.py`)

-   Header handling (`headers_test.py`)

-   Deep merge behavior (`mergetest.py`)

-   Error handling (`test_errors.py`)

