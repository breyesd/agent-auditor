# T8: Configurar sqlite3 para checkpoints de memoria episódica

- **id**: T8
- **título**: Configurar sqlite3 para checkpoints de memoria episódica
- **descripción**: Almacén local sqlite3 para checkpointer de grafo que retiene estado de sesión activa (mensajes, llamadas a tools, respuestas).
- **tipo**: base_de_datos
- **tamaño**: pequena
- **dependencias**: []
- **validaciones de campo**: checkpoints se guardan y recuperan por sesión
- **librerias o métodos utilitarios**: `sqlite3`, `langgraph` checkpointer
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: tabla checkpoints {session_id, estado, timestamp}
- **enlace a su HU**: docs/historias/hu-2.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 3)
- **estado**: [ ]
