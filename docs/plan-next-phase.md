# Plan de trabajo: JOOG Forge / FRG

## Estado confirmado

- Entorno operativo con `.venv`, Bleak 1.1.1 y `pip check` correcto.
- Reloj detectado como `FRG`, identificador Windows `41:88:11:E2:88:31`.
- Firmware: `MOY-8QJ4-2.0.8`; software: `MOYOUNG-V2`.
- GATT: 9 servicios, 21 characteristics, 4 servicios custom, 11 `READ`, 6 `WRITE`, 7 `NOTIFY`, 1 `INDICATE`.
- La conexión, enumeración, safe READ y suscripciones NOTIFY funcionan.
- Tras vincular con Da Fit, las dos sesiones de HR duraron aproximadamente 62 s y 92 s; ninguna recibió datos en `00002a37` (Heart Rate Measurement). En las sesiones auditadas solo aparecieron notificaciones de batería en `00002a19`.
- No se ha enviado ningún WRITE, OTA, DFU, reset, comando desconocido ni actualización.

La evidencia actual demuestra transporte GATT y batería, pero todavía no demuestra
HR, SpO2, pasos ni un comando Moyoung. Las asociaciones `FEEA`, `FEE7`, `190E` y
`AE00` siguen siendo hipótesis de familia/estructura hasta observar bytes de este
FRG y este firmware.

## Decisión técnica

No se implementará una capa de comandos BLE basándose en nombres de UUID o en
suposiciones. Las characteristics `FEE2`, `FEE5`, `FEE6`, `190E/00000004` y
`AE00/AE01` quedan catalogadas como canales potenciales, no como comandos
utilizables.

## Fase 1 — congelar y mejorar la evidencia

Objetivo: obtener observaciones repetibles antes de interpretar bytes.

1. Mantener `allow_write=false` y ejecutar exclusivamente scan, connect, READ y NOTIFY.
2. Registrar capturas idle de 60–120 s.
3. Repetir HR tres veces con el mismo diseño: safe READ inmediatamente antes y
   después, hora exacta de inicio, valor mostrado en el reloj y captura separada.
4. Repetir el mismo diseño para SpO2; después hacer pasos con una caminata de
   20–50 pasos y valores antes/después.
5. Anotar siempre la acción exacta, la hora aproximada y el central activo.
6. Añadir al analizador una tabla por UUID, longitud, frecuencia, cambios y calidad de evidencia.

Salida: matriz `acción -> UUID -> paquetes -> interpretación -> confianza`.

## Fase 2 — capturar el tráfico real de Da Fit

Objetivo: descubrir qué envía la aplicación sin que el proyecto escriba al reloj.

Ruta recomendada si el teléfono es Android:

1. Activar temporalmente `Bluetooth HCI snoop log` en Opciones de desarrollador.
2. Iniciar la captura antes de abrir Da Fit.
3. Abrir Da Fit, sincronizar y ejecutar una sola acción por captura.
4. Detener la captura y exportar `btsnoop_hci.log`.
5. Convertirla a `.pcap`/`.pcapng` si hace falta y filtrar por la dirección del reloj.
6. Correlacionar operaciones ATT Write/Notify con la acción observada.

La documentación oficial de Android indica que HCI snoop guarda los paquetes en
`/sdcard/btsnoop_hci.log`; Microsoft documenta que GATT expone servicios,
characteristics, descriptors, lecturas, escrituras y eventos de cambio de valor.
La captura debe conservar el archivo bruto inmutable y generar un archivo
normalizado aparte. Una captura debe corresponder a una sola acción: sincronizar,
HR, SpO2, pasos, etc.

Salida: mapa de comandos de Da Fit con bytes observados, characteristic, respuesta,
contador/checksum candidato y confianza. Esta fase es de captura/análisis; no
reproduciremos los writes automáticamente.

### Ruta para iPhone / multi-OS

iOS no ofrece un equivalente público y general al archivo Android HCI snoop para
extraer todo el tráfico BLE de Da Fit desde el teléfono; CoreBluetooth es una API
de cliente a nivel de aplicación. Por eso el diseño será multi-OS con dos entradas
de evidencia:

- `pcap`/HCI snoop cuando el teléfono sea Android;
- captura aérea BLE con un sniffer compatible cuando el teléfono sea iPhone;
- trazas de diagnóstico de iOS solo si la herramienta conserva suficiente contexto
  ATT/GATT.

Una captura aérea puede quedar cifrada después del emparejamiento. No se usará
MITM, reemparejamiento forzado, replay ni modificación del reloj para obtener
claves.

El núcleo de análisis será independiente del sistema operativo: recibirá paquetes
ATT/GATT normalizados y producirá la misma matriz de comandos, respuestas,
contadores y checksums. La conexión directa continuará usando Bleak en Windows,
macOS y Linux; una futura app iOS podrá usar CoreBluetooth como cliente read-only,
pero no será necesaria para analizar capturas.

No se intentará mantener Da Fit y el cliente de investigación conectados al mismo
tiempo: el reloj puede aceptar una sola conexión útil o cambiar su estado según el
central que lo controle. Cada experimento debe registrar qué central estaba activo.

Formato normalizado mínimo, conservando siempre el bruto original:

~~~json
{
  "schema": "ble-capture/v1",
  "timestamp_utc": "...",
  "source": "android_hci|nrf_sniffer|corebluetooth",
  "platform": "android|ios|windows|macos|linux",
  "direction": "central_to_peripheral|peripheral_to_central",
  "layer": "att|gatt|l2cap|hci|advertising",
  "operation": "read|write|notify|indicate|unknown",
  "service_uuid": "optional",
  "characteristic_uuid": "optional",
  "handle": "optional",
  "payload_hex": "...",
  "encrypted": false,
  "raw_ref": "source-file#frame-123",
  "decode_confidence": 0.0
}
~~~

Se deben anonimizar dirección, cuenta y datos de salud cuando se compartan
capturas. Se conservan dirección hash, firmware, versiones de OS/app, UUIDs,
dirección de tráfico y referencias al frame bruto.

## Fase 3 — cliente read-only robusto

Objetivo: convertir las observaciones en una herramienta usable.

- Reconexión controlada y diagnóstico de `Unreachable`.
- Selección por nombre, dirección y cache de identificador Windows.
- Suscripciones explícitas por UUID y timestamps monotónicos.
- Decodificadores únicamente para formatos confirmados o estándar.
- Exportación JSON/JSONL/CSV y reporte de sesión.
- API/PWA read-only para estado, batería, capturas y eventos.
- Núcleo de parsing portable y pruebas con las mismas capturas en Windows, macOS y Linux.

Criterio de salida: todas las funciones read-only funcionan sin Da Fit conectada,
con logs reproducibles y sin ninguna llamada de escritura.

## Fase 4 — posible control, solo con una compuerta explícita

No comienza automáticamente. Requiere:

- captura reproducida varias veces;
- identificación inequívoca de characteristic, framing y checksum;
- prueba en una acción reversible y de bajo riesgo;
- respaldo de configuración y plan de recuperación;
- confirmación expresa antes de añadir cada operación WRITE.

OTA, DFU, firmware, bootloader, reset y comandos desconocidos quedan fuera de
esta fase.

## Siguiente acción concreta

La próxima evidencia de mayor valor es un `btsnoop_hci.log` de Da Fit durante una
sola acción, idealmente sincronización o medición de HR. Como el teléfono principal
es un iPhone 16 Pro, para conseguirlo necesitaremos temporalmente un Android con
Da Fit o un sniffer BLE externo. Mientras no exista esa captura, seguiremos con
experimentos pasivos y mejoras del cliente, no con bytes inventados.
