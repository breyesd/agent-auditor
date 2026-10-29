# T6: Implementar pipeline de chunking semántico/markdown-aware

- **id**: T6
- **título**: Implementar pipeline de chunking semántico/markdown-aware
- **descripción**: Chunking de normativas de arquitectura y guías de estilo (tamaño 512 tokens, 10% overlap).
- **tipo**: logica_negocio
- **tamaño**: mediana
- **dependencias**: [T5]
- **validaciones de chunk**: chunks de 512 tokens con 10% overlap; respeta límites de markdown
- **librerias o métodos utilitarios**: `langchain-text-splitters`, `tiktoken`
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: lista de chunks {texto, metadata, token_count}
- **enlace a su HU**: docs/historias/hu-3.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 2)
- **estado**: [ ]
