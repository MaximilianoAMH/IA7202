# IA7202 - Laboratorio de Programación Científica para Ciencia de Datos

Repositorio del curso IA7202 (Primavera 2026), Facultad de Ciencias Físicas y Matemáticas, Universidad de Chile.

## Integrantes

| Nombre | GitHub |
|--------|--------|
| Maximiliano Morales | [@MaximilianoAMH](https://github.com/MaximilianoAMH) |
| Guillermo Escobar | [@usuario2](https://github.com/guillermoescobar202) |

## Estructura del repositorio

.
├── .github/
│   ├── workflows/
│   │   └── lint.yml
│   └── pull_request_template.md
├── labs/
│   ├── lab_1/
│   └── ...
├── pyproject.toml
├── .github/
├── .pre-commit-config.yaml
└── README.md

## Configuración del entorno

uv sync --locked --all-groups
uv run pre-commit install
