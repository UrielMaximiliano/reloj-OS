# Research log

## 2026-08-13 - Bootstrap del proyecto

- Se creo el toolkit Python/Bleak para Windows y Linux.
- Se fijo `allow_write=false` como configuracion predeterminada.
- Se implementaron scanner, conexion, enumeracion GATT, safe reader, monitor `NOTIFY`, recorder JSONL y comparacion offline.
- No se inventaron UUIDs, comandos ni formatos.

## 2026-08-13 - Primeras observaciones BLE del dispositivo real

- Scanner BLE: candidato confirmado por nombre `FRG`, identifier `41:88:11:E2:88:31`, RSSI observado `-49`.
- Advertising: manufacturer data con company ID `61679` y bytes `41 88 11 e2 88 31`; service data `0000feea-0000-1000-8000-00805f9b34fb`.
- GATT enumerado: 9 servicios, 21 characteristics, 11 `READ`, 6 `WRITE`/`WRITE WITHOUT RESPONSE`, 7 `NOTIFY`, 1 `INDICATE`.
- Servicios SIG reconocidos: Generic Access, Generic Attribute, Heart Rate, Battery Service y Device Information.
- Servicios no reconocidos por el registro conservador: `0000feea-...`, `0000fee7-...`, `0000190e-...`, `0000ae00-...`; se clasifican como `CUSTOM/UNKNOWN`, no como protocolo confirmado.
- Lecturas seguras: firmware `MOY-8QJ4-2.0.8`, software `MOYOUNG-V2`, fabricante `MOYOUNG-V2`, serial `F92BA4F5`, bateria `43`.
- Canales estructuralmente candidatos `WRITE + NOTIFY/INDICATE`: servicios `0000feea-...`, `0000190e-...` y `0000ae00-...`. No se escribio ningun byte.
- OTA/DFU: `UNKNOWN`; no aparecio una characteristic custom inequivocamente etiquetada OTA/DFU y no se ejercito ningun canal de escritura.
- Monitor baseline de 10 s: se suscribieron 7 characteristics `NOTIFY`; no llegaron notificaciones durante la ventana de reposo. Captura: `captures/baseline_20260813_115243.jsonl`.

## 2026-08-13 - Fase 2: idle de 30 segundos

- Captura: `captures/idle_20260813_121040.jsonl`.
- Se suscribieron 7 characteristics `NOTIFY`.
- Se observo un unico evento: `00002a19-0000-1000-8000-00805f9b34fb` / Battery Level, `2b` = 43%, a `2026-08-13T15:11:01.632034Z`.
- No se observaron notificaciones en FEEA, FEE7, 190E ni AE00 durante idle.
- Interpretacion: **CONFIRMED** como observacion de esta ventana; no demuestra que los servicios custom esten inactivos en todos los estados.

## 2026-08-13 - Fase 2: comparacion publica

- Gadgetbridge documents the Moyoung V2 family with FEEA as the main service, FEE2 as data-out and FEE3 as data-in; it also documents the FEE7/FEA1/FEC9 secondary layout.
- Our GATT and `MOYOUNG-V2` manufacturer string match that family at the structural level.
- AE00/AE01/AE02 has public examples in unrelated sensors, printers and actuators; no watch-specific meaning was transferred.
- 190E produced no relevant Da Fit/Moyoung implementation in the exact-UUID search.
- Exact public artifacts for `MOY-8QJ4-2.0.8`, `MOY-8QJ4` or `8QJ4` were not found.
- Details and URLs: `docs/external-protocol-research.md`.
