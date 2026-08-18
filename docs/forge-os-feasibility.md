# Forge OS — feasibility

Estado general: **investigación inicial**. No se implementa firmware propio en esta etapa.

| Componente | Estado | Evidencia | Bloqueante |
|---|---|---|---|
| SoC | Reportado | `JL7012F6` proporcionado por el usuario | NO confirmado por dump |
| Display resolution | Reportado | `360x360` proporcionado por el usuario | NO |
| BLE API | Pendiente | Requiere mapa GATT y capturas | SÍ para control compatible |
| Toolchain | Pendiente | No hay SDK verificado | SÍ |
| SDK | Pendiente | No hay documentación primaria verificada | SÍ |
| Bootloader | Pendiente | No se ha extraído ni identificado | SÍ |
| Firmware format | Pendiente | No hay archivo de este reloj | SÍ |
| OTA format | Investigando | Aún sin GATT real | SÍ |
| Memory map | Pendiente | No hay dump ni documentación del modelo | SÍ |
| Display controller | Desconocido | No hay teardown ni documentación específica | SÍ |
| Touch controller | Desconocido | No hay evidencia específica | SÍ |
| Accelerometer | Desconocido | No identificado | SÍ |
| Flash | Desconocido | No identificado | SÍ |
| Recovery mechanism | Desconocido | No verificado | SÍ |

Conclusión actual: no hay base suficiente para modificar firmware. La prioridad es observar BLE de forma segura y conseguir evidencia específica del modelo.
