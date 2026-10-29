# HU-2: Consultar memoria de reglas aprobadas y preferencias

Como usuario, quiero que el agente recuerde mis preferencias (framework, exclusiones de reglas) y no repita instrucciones ya dadas en sesiones previas.

## Especificación funcional de flujo de datos
1. Usuario declara preferencia o regla (ej. "No reportar variables no usadas en tests").
2. `memory_store` extractor asíncrono de hechos genera tripla semántica.
3. Tripla se guarda en colección persistente (perfil de usuario).
4. En auditorías posteriores, `memory_consult` recupera el perfil y aplica exclusiones.
5. Short-term (episódica): checkpointer de grafo retiene estado de sesión activa.

## Criterios de aceptación
- [ ] Preferencia declarada se persiste como tripla semántica.
- [ ] Regla se aplica en auditorías subsiguientes (exclusión respetada).
- [ ] Estado de sesión activa retenido en checkpointer.
- [ ] Almacenamiento: sqlite3 para checkpoints + almacén KV/vectorial para perfiles.

## Relación
Especificación específica: docs/especificaciones/especificacion-fase-1.md (sección 2.2 nodo memory_consult).
Subproyecto 3: modules/memory_store.
