# Plan de trabajo: JOOG Forge / FRG

## Estado confirmado

- Entorno operativo con `.venv`, Bleak 1.1.1 y `pip check` correcto.
- Reloj detectado como `FRG`, identificador Windows `41:88:11:E2:88:31`.
- Firmware: `MOY-8QJ4-2.0.8`; software: `MOYOUNG-V2`.
- GATT: 9 servicios, 21 characteristics, 11 `READ`, 7 `NOTIFY`, 1 `INDICATE`.
- La conexión, enumeración, safe READ y suscripciones NOTIFY funcionan.
- Tras vincular con Da Fit, dos capturas de 90 s no recibieron datos en `00002a37` (Heart Rate Measurement); solo llegó batería en `00002a19`.
- No se ha enviado ningún WRITE, OTA, DFU, reset, comando desconocido ni actualización.

## Decisión técnica

No se implementará una capa de comandos BLE basándose en nombres de UUID o en
suposiciones. Las characteristics `FEE2`, `FEE5`, `FEE6`, `190E/00000004` y
`AE00/AE01` quedan catalogadas como canales potenciales, no como comandos
utilizables.

## Fase 1 — congelar y mejorar la evidencia

Objetivo: obtener observaciones repetibles antes de interpretar bytes.

1. Mantener `allow_write=false` y ejecutar exclusivamente scan, connect, READ y NOTIFY.
2. Registrar capturas idle de 60–120 s.
3. Repetir, por separado, pasos, cronómetro, botón, pantalla, batería, HR y SpO2.
4. Anotar siempre la acción exacta y la hora aproximada en el reloj.
5. Añadir al analizador una tabla por UUID, longitud, frecuencia, cambios y calidad de evidencia.

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

Salida: mapa de comandos de Da Fit con bytes observados, characteristic, respuesta,
contador/checksum candidato y confianza. Esta fase es de captura/análisis; no
reproduciremos los writes automáticamente.

### Ruta para iPhone / multi-OS

iOS no ofrece un equivalente público y general al archivo Android HCI snoop para
extraer todo el tráfico BLE de Da Fit desde el teléfono. Por eso el diseño será
multi-OS con dos entradas de evidencia:

- `pcap`/HCI snoop cuando el teléfono sea Android;
- captura aérea BLE con un sniffer compatible, o trazas de una herramienta de
  diagnóstico de iOS, cuando el teléfono sea iPhone.

El núcleo de análisis será independiente del sistema operativo: recibirá paquetes
ATT/GATT normalizados y producirá la misma matriz de comandos, respuestas,
contadores y checksums. La conexión directa continuará usando Bleak en Windows,
macOS y Linux; una futura app iOS podrá usar CoreBluetooth como cliente read-only,
pero no será necesaria para analizar capturas.

No se intentará mantener Da Fit y el cliente de investigación conectados al mismo
tiempo: el reloj puede aceptar una sola conexión útil o cambiar su estado según el
central que lo controle. Cada experimento debe registrar qué central estaba activo.

## Fase 3 — cliente read-only robusto

Objetivo: convertir las observaciones en una herramienta usable.

- Reconexión controlada y diagnóstico de `Unreachable`.
- Selección por nombre, dirección y cache de identificador Windows.
- Suscripciones explícitas por UUID y timestamps monotónicos.
- Decodificadores únicamente para formatos confirmados o estándar.
- Exportación JSON/JSONL/CSV y reporte de sesión.
- API/PWA read-only para estado, batería, capturas y eventos.

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
sola acción, idealmente sincronización o medición de HR. Mientras no exista esa
captura, seguiremos con experimentos pasivos y mejoras del cliente, no con bytes
inventados.
