# Langflow Tech Stack

## Backend (Python)

- **Framework**: FastAPI with Uvicorn
- **Python**: 3.10-3.13
- **Package Manager**: uv (Astral)
- **Database**: SQLModel + SQLAlchemy (SQLite default, PostgreSQL supported)
- **Migrations**: Alembic
- **LLM Framework**: LangChain ecosystem
- **Validation**: Pydantic v2
- **Logging**: Loguru + Structlog

## Frontend (TypeScript/React)

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Flow Visualization**: @xyflow/react (React Flow)
- **UI Components**: Radix UI primitives + Tailwind CSS
- **Forms**: React Hook Form + Zod
- **Linting/Formatting**: Biome

## Packages

- `langflow`: Main package with all integrations
- `langflow-base`: Core functionality without heavy dependencies
- `lfx`: Lightweight executor for running flows (CLI tool)

## Common Commands

### Development Setup
```bash
make init              # Install all dependencies + pre-commit hooks
make backend           # Run backend in dev mode (hot reload)
make frontend          # Run frontend in dev mode (hot reload)
```

### Building & Running
```bash
make run_cli           # Build and run full application
make run_clic          # Clean build and run (fresh frontend)
make build             # Build project for distribution
```

### Code Quality
```bash
make format            # Format all code (backend + frontend)
make format_backend    # Format Python code (ruff)
make lint              # Run linters (mypy)
```

### Testing
```bash
make unit_tests        # Run backend unit tests
make integration_tests # Run integration tests
make tests             # Run all tests + coverage
make lfx_tests         # Run lfx package tests
```

### Database Migrations
```bash
make alembic-revision message="Description"  # Create migration
make alembic-upgrade                         # Apply migrations
make alembic-downgrade                       # Rollback one version
```

### Component Development
```bash
LFX_DEV=1 make backend                      # Enable live component reloading
make build_component_index                  # Rebuild component index
```

### Cleanup
```bash
make clean_all         # Clean all caches and build artifacts
make clean_frontend_build  # Clean frontend build only
```
