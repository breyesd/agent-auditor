# T15: Implementar nodo memory_consult

- **id**: T15
- **título**: Implementar nodo memory_consult
- **descripción**: Nodo que lee perfil de usuario y reglas aprobadas de `memory_store` (short-term y long-term).
- **tipo**: logica_negocio
- **tamaño**: pequena
- **dependencias**: [T8, T9]
- **validaciones de campo**: retorna perfil y reglas aplicables; excluye reglas marcadas
- **librerias o métodos utilitarios**: `sqlite3`, almacén KV
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: {perfil, reglas_aprobadas, exclusiones}
- **enlace a su HU**: docs/historias/hu-2.md, docs/historias/hu-1.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 3, 5)
- **estado**: [ ]
