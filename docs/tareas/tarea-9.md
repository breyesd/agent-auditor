# T9: Implementar extractor de hechos semánticos y almacén KV de perfiles

- **id**: T9
- **título**: Implementar extractor de hechos semánticos y almacén KV de perfiles
- **descripción**: Extractor asíncrono de hechos (triplas semánticas) desde declaraciones de usuario y almacén clave-valor indexado para perfiles de usuario (reglas aprobadas, exclusiones).
- **tipo**: base_de_datos
- **tamaño**: mediana
- **dependencias**: [T8]
- **validaciones de campo**: tripla semántica persistida; regla de exclusión aplicada en auditorías posteriores
- **librerias o métodos utilitarios**: `sqlite3` o almacén KV/vectorial
- **interfaz de usuario**: no aplica (interno)
- **estructura de datos**: perfil_usuario {preferencias, reglas_aprobadas, exclusiones}
- **enlace a su HU**: docs/historias/hu-2.md
- **enlace a su diseño**: docs/disenos/arquitectura.md (Subproyecto 3)
- **estado**: [ ]
