# OTA / DFU analysis

Estado: **UNKNOWN**. La enumeracion real encontro informacion de firmware, pero no un canal OTA/DFU identificado con suficiente evidencia. Esta primera entrega no escribe BLE y no inicia actualizacion alguna.

`scripts\inspect.py` hace unicamente una pantalla conservadora sobre UUID, nombre y descripcion de servicios/characteristics ya expuestos por GATT. Si encuentra palabras como `OTA`, `DFU`, `Firmware`, `Update`, `JieLi`, `JL`, `Moyoung`, `CRP` o `Da Fit`, las reporta como posible evidencia nominal, no como canal verificado.

Para cada candidato futuro se debe documentar, sin ejercitarlo:

| Elemento | Estado | Evidencia | Accion permitida ahora |
|---|---|---|---|
| Possible OTA service | UNKNOWN | Enumeracion GATT real aun no concluyente | Enumerar y documentar |
| Possible OTA control characteristic | UNKNOWN | No identificada por nombre/UUID | Enumerar propiedades |
| Possible OTA data characteristic | UNKNOWN | No identificada por nombre/UUID | Enumerar propiedades |
| Firmware/software revision | OBSERVED | `READ` en Device Information | Safe reader |

## Evidencia actual del JOOG Forge

- Device Information / Firmware Revision String (`00002a26`): `JLQFNIMG1.9`.
- Device Information / Software Revision String (`00002a28`): `MOY-8QJ4-2.0.8`.
- Device Information / Manufacturer Name String (`00002a29`): `MOYOUNG-V2`.
- Servicios custom/unknown con estructura WRITE + NOTIFY/INDICATE: `0000feea-...`, `0000190e-...`, `0000ae00-...`.
- Interpretacion: **POSSIBLE COMMAND CHANNEL / UNCONFIRMED**, no OTA. Las properties no prueban la semantica del canal.

## External comparison, not device evidence

Gadgetbridge documents a Moyoung/Da Fit protocol family in which FEEA is the main data service and also mentions a static DFU-status query based on Device Information. Our watch matches the FEEA family layout and exposes firmware/software strings, but it does not expose a readable Model Number String in the captured GATT map, and no OTA characteristic was identified. Therefore the assessment remains **UNKNOWN**, not `POSSIBLE OTA`.

The public Da Fit constants also contain a commented/uncertain `HS_DFU` command in the family code. That is external protocol documentation, not a packet captured from FRG. It is recorded as **POSSIBLE FAMILY-LEVEL OTA/DFU REFERENCE**, never as permission to send it.

No se debe usar `WRITE`, `WRITE WITHOUT RESPONSE`, reset, borrado, cambio de particiones ni actualizacion hasta tener un mecanismo de recuperacion verificado.
