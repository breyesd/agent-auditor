# T12: Implementar CLI de entrada y validación Pydantic

- **id**: T12
- **título**: Implementar CLI de entrada y validación Pydantic
- **descripción**: CLI que acepta ruta de archivo o diff staged, normaliza la entrada y valida esquema `AuditorRequest`.
- **tipo**: logica_negocio
- **tamaño**: mediana
- **dependencias**: [T10]
- **validaciones de campo**: entrada de archivo o diff aceptada; `AuditorRequest` válido
- **librerias o métodos utilitarios**: `typer`/`click`, `pydantic v2`
- **interfaz de usuario**: CLI
- **estructura de datos**: `AuditorRequest`
- **enlace a su HU**: docs/historias/hu-1.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 5)
- **estado**: [ ]
