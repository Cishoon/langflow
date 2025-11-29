# Langflow Project Structure

```
langflow/
├── src/
│   ├── backend/
│   │   ├── base/                    # langflow-base package
│   │   │   └── langflow/
│   │   │       ├── api/             # FastAPI routes (v1, v2)
│   │   │       ├── components/      # Core components (minimal)
│   │   │       ├── services/        # Business logic services
│   │   │       │   └── database/    # Database models & service
│   │   │       ├── alembic/         # Database migrations
│   │   │       ├── graph/           # Flow graph execution
│   │   │       ├── schema/          # Pydantic schemas
│   │   │       ├── settings.py      # Configuration
│   │   │       └── main.py          # FastAPI app factory
│   │   └── tests/                   # Backend tests
│   │       ├── unit/
│   │       └── integration/
│   │
│   ├── frontend/                    # React frontend
│   │   └── src/
│   │       ├── components/          # React components
│   │       ├── pages/               # Route pages
│   │       ├── stores/              # Zustand stores
│   │       ├── controllers/         # API controllers
│   │       ├── hooks/               # Custom React hooks
│   │       ├── types/               # TypeScript types
│   │       ├── contexts/            # React contexts
│   │       └── modals/              # Modal components
│   │
│   └── lfx/                         # lfx executor package
│       └── src/lfx/
│           ├── components/          # All flow components
│           ├── graph/               # Graph execution engine
│           ├── cli/                 # CLI commands (serve, run)
│           ├── services/            # Runtime services
│           └── custom/              # Custom component support
│
├── docs/                            # Docusaurus documentation
│   └── docs/                        # MDX documentation files
│
├── scripts/                         # Build & CI scripts
├── docker/                          # Docker configurations
├── deploy/                          # Deployment configs
│
├── pyproject.toml                   # Main Python project config
├── Makefile                         # Development commands
└── package.json                     # Root Node.js config
```

## Key Directories

### Backend (`src/backend/base/langflow/`)
- `api/v1/`, `api/v2/`: REST API endpoints
- `services/`: Core services (auth, database, cache, tracing)
- `initial_setup/starter_projects/`: Default flow templates (JSON)

### Frontend (`src/frontend/src/`)
- `components/core/`: Core UI components
- `CustomNodes/`: Flow canvas node components
- `CustomEdges/`: Flow canvas edge components
- `controllers/API/`: API client code

### Components (`src/lfx/src/lfx/components/`)
Components are organized by category:
- `agents/`: Agent components
- `models/`: LLM model components
- `embeddings/`: Embedding model components
- `vectorstores/`: Vector database components
- `tools/`: Tool components
- `data/`: Data processing components
- `input_output/`: Chat I/O components

## Configuration Files

- `pyproject.toml`: Python dependencies, ruff/mypy config
- `src/frontend/biome.json`: Frontend linting rules
- `src/frontend/tailwind.config.mjs`: Tailwind CSS config
- `.env`: Environment variables (local)
