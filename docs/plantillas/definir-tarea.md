Eres un analista de software. A partir de la HU {{hu_id}} ({{contenido_hu}}), define las tareas necesarias para implementarla.

Para cada tarea define:
- id (T1, T2, ...)
- título
- descripción
- tipo: base_de_datos | logica_negocio | frontend | ci_cd | pruebas | configuracion
- tamaño: pequena (<3h) | mediana (3-6h) | grande (>6h, partir si es posible)
- dependencias: ids de tareas previas
- validaciones de campo (si aplica)
- librerias o métodos utilitarios a utilizar
- interfaz de usuario (si aplica)
- estructura de datos (si aplica)
- enlace a su HU: docs/historias/hu-<n>.md
- enlace a su diseño: docs/disenos/... (si aplica)

Regla de tamaño: si una tarea es grande (>6h), sugiere partirla. Solo aceptar >8h si es absolutamente necesario.

Genera un archivo por tarea en docs/tareas/tarea-<n>.md con checkbox [ ] pendiente.
Incluye una lista ordenada de tareas y sus dependencias, además de un check para ir marcando cuáles ya se realizaron.