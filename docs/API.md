# 📝 API Documentation

## Available Endpoints

This documentation describes the endpoints available in the boilerplate. Your project's specific endpoints will vary based on your needs.

## Interactive Documentation

Once the server is running, you can access the interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Structure

### Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

### Versioning

The API uses URL versioning:

```
/api/v1/...
```

## Base Endpoints

### Health Check

#### `GET /health`

Checks the API status.

**Response**

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-01-30T10:00:00Z"
}
```

**Status Codes**
- `200 OK`: API working correctly
- `503 Service Unavailable`: API with issues

## Example Endpoints

### Projects

#### `GET /api/v1/projects`

Lists all projects.

**Query Parameters**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records (default: 100)

**Response**

```json
{
  "projects": [
    {
      "id": "uuid-here",
      "name": "Project Name",
      "description": "Project description",
      "created_at": "2026-01-30T10:00:00Z",
      "updated_at": "2026-01-30T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### `POST /api/v1/projects`

Creates a new project.

**Request Body**

```json
{
  "name": "New Project",
  "description": "Project description"
}
```

**Response** (201 Created)

```json
{
  "id": "uuid-here",
  "name": "New Project",
  "description": "Project description",
  "created_at": "2026-01-30T10:00:00Z",
  "updated_at": "2026-01-30T10:00:00Z"
}
```

#### `GET /api/v1/projects/{project_id}`

Gets a specific project.

**Path Parameters**
- `project_id` (string): Project ID

**Response**

```json
{
  "id": "uuid-here",
  "name": "Project Name",
  "description": "Project description",
  "created_at": "2026-01-30T10:00:00Z",
  "updated_at": "2026-01-30T10:00:00Z"
}
```

**Status Codes**
- `200 OK`: Project found
- `404 Not Found`: Project doesn't exist

#### `PUT /api/v1/projects/{project_id}`

Updates a project.

**Path Parameters**
- `project_id` (string): Project ID

**Request Body**

```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```

**Response**

```json
{
  "id": "uuid-here",
  "name": "Updated Name",
  "description": "Updated description",
  "created_at": "2026-01-30T10:00:00Z",
  "updated_at": "2026-01-30T12:00:00Z"
}
```

#### `DELETE /api/v1/projects/{project_id}`

Deletes a project.

**Path Parameters**
- `project_id` (string): Project ID

**Response** (204 No Content)

No body.

**Status Codes**
- `204 No Content`: Project deleted
- `404 Not Found`: Project doesn't exist

## Data Models

### Project

```python
{
  "id": str,              # Project UUID
  "name": str,            # Project name (required)
  "description": str,     # Description (optional)
  "created_at": datetime, # Creation date
  "updated_at": datetime  # Update date
}
```

### Experiment

```python
{
  "id": str,              # Experiment UUID
  "name": str,            # Experiment name
  "project_id": str,      # Parent project ID
  "status": str,          # Status: pending, running, completed, failed
  "created_at": datetime,
  "updated_at": datetime
}
```

## Pagination

Endpoints returning lists support pagination:

```
GET /api/v1/projects?skip=0&limit=10
```

**Response**

```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 10
}
```

## Filters

Endpoints can support filters via query parameters:

```
GET /api/v1/projects?name=search&status=active
```

## Sorting

Sorting via query parameter:

```
GET /api/v1/projects?order_by=created_at&order=desc
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Status Codes

- `200 OK`: Successful operation
- `201 Created`: Resource created successfully
- `204 No Content`: Successful operation with no response content
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error

### Validation Errors (422)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Authentication

*Note: The base boilerplate doesn't include authentication. Here's an example of how you could implement it.*

### JWT Bearer Token

```http
GET /api/v1/projects
Authorization: Bearer <token>
```

### Login Endpoint

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Rate Limiting

*Note: Not implemented in the base boilerplate.*

Example rate limiting headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## CORS

The boilerplate is configured for CORS. Configure origins in `.env`:

```env
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com
```

## Webhooks

*Not implemented in the base boilerplate.*

## WebSockets

*Not implemented in the base boilerplate.*

If you need WebSockets, FastAPI supports them:

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message: {data}")
```

## Examples

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# List projects
curl http://localhost:8000/api/v1/projects

# Create project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "New Project", "description": "Description"}'

# Get project
curl http://localhost:8000/api/v1/projects/{project_id}

# Update project
curl -X PUT http://localhost:8000/api/v1/projects/{project_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Delete project
curl -X DELETE http://localhost:8000/api/v1/projects/{project_id}
```

### Python Client Example

```python
import httpx

# Base client
client = httpx.Client(base_url="http://localhost:8000")

# Create project
response = client.post(
    "/api/v1/projects",
    json={
        "name": "New Project",
        "description": "Description"
    }
)
project = response.json()
print(project)

# List projects
response = client.get("/api/v1/projects")
projects = response.json()
print(projects)
```

### JavaScript/TypeScript Example

```javascript
// Using fetch
const response = await fetch('http://localhost:8000/api/v1/projects', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'New Project',
    description: 'Description'
  })
});

const project = await response.json();
console.log(project);
```

## OpenAPI Schema

The OpenAPI schema is available at:

```
GET /openapi.json
```

You can use this to automatically generate clients with tools like:
- [openapi-generator](https://github.com/OpenAPITools/openapi-generator)
- [swagger-codegen](https://github.com/swagger-api/swagger-codegen)

## Monitoring

### Health Check

```
GET /health
```

Returns the API status and its dependencies.

### Metrics

*Not implemented in the base boilerplate.*

To add metrics, consider using:
- [Prometheus](https://prometheus.io/)
- [OpenTelemetry](https://opentelemetry.io/)

## Best Practices

### 1. Always use proper HTTP methods

- `GET`: Retrieve data
- `POST`: Create new resources
- `PUT`: Update entire resources
- `PATCH`: Partial updates
- `DELETE`: Remove resources

### 2. Use proper status codes

Return appropriate HTTP status codes.

### 3. Version your API

Use URL versioning: `/api/v1/...`

### 4. Document your endpoints

Use docstrings and OpenAPI descriptions:

```python
@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all projects.
    
    Parameters:
    - skip: Number of records to skip
    - limit: Maximum number of records to return
    
    Returns list of projects with pagination info.
    """
    ...
```

### 5. Validate input

Use Pydantic models for automatic validation.

### 6. Handle errors gracefully

```python
try:
    result = service.operation()
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [REST API Best Practices](https://restfulapi.net/)
