# forge-research

Toolkit de investigación BLE, seguro y de solo lectura, para el smartwatch JOOG Forge / FRG basado —según la información disponible— en JieLi JL7012F6 y ecosistema Moyoung / Da Fit.

La primera etapa permite escanear, conectar, enumerar GATT, leer únicamente characteristics con `READ`, suscribirse a `NOTIFY` y guardar capturas crudas para compararlas offline. No intenta flashear, actualizar, borrar, resetear ni escribir bytes en el reloj.

## Seguridad

- `allow_write` es `false` por defecto.
- La primera entrega no expone ninguna función de escritura BLE.
- No se ejecutan comandos OTA/DFU, factory reset ni comandos desconocidos.
- Las notificaciones se guardan como bytes crudos; no se inventan comandos ni significados.
- La detección OTA solo etiqueta evidencia nominal en UUID, nombre o descripción; el estado real sigue siendo `UNKNOWN` hasta contar con evidencia.

## Instalación en Windows 11

Desde PowerShell, ubicado en la raíz del repositorio:

```powershell
.\bootstrap.ps1
```

Si PowerShell bloquea la activación del entorno, puede usarse directamente `.\.venv\Scripts\python.exe` o ajustarse la política de ejecución de forma consciente en el entorno del usuario.

## Primera base nativa para iOS

El paquete local `ios/ForgeIOS` agrega un cliente CoreBluetooth para iPhone:
escaneo, conexión, enumeración GATT, lecturas explícitas y exportación JSONL
`ble-capture/v1`. Incluye una vista SwiftUI mínima en
`ios/ForgeIOS/Sources/ForgeIOS/ForgeDashboardView.swift`.

Para integrarlo, abre Xcode, crea una app SwiftUI y añade `ios/ForgeIOS` como
paquete local. Copia las claves Bluetooth de
`ios/ForgeIOS/Info.plist.example`. Las suscripciones NOTIFY están apagadas por
defecto; no hay `writeValue`, OTA, DFU, reset ni replay.

La guía completa está en [ios/README.md](ios/README.md). iOS no ofrece HCI snoop
crudo desde la API pública, por lo que esta primera versión captura observaciones
a nivel de aplicación y deja el análisis de protocolo para el núcleo portable.

## Diagnostico y ejecucion reproducible

El error `ModuleNotFoundError: No module named 'bleak'` aparece cuando `python`
apunta a la instalacion global. Usa el interprete local directamente:

```powershell
.\bootstrap.ps1
.\.venv\Scripts\python.exe scripts\doctor.py
```

`bootstrap.ps1` reutiliza un `.venv` funcional, instala `requirements.txt` y
ejecuta `pip check`. Si encuentra un entorno roto, lo mueve a
`.venv.broken_<timestamp>` en vez de eliminarlo. Python 3.12/3.13 tiene
preferencia; `-InstallPython` permite solicitar Python 3.12 mediante `winget`.

```powershell
.\bootstrap.ps1 -InstallPython
.\run.ps1 doctor
.\run.ps1 scan
.\run.ps1 inspect
.\run.ps1 read
.\run.ps1 monitor heart_rate_01 50
```

## Configuración

`config.json` es local y está ignorado por Git. El valor inicial recomendado es:

```json
{
  "device_name": "FRG",
  "device_address": null,
  "known_firmware": "MOY-8QJ4-2.0.8",
  "known_display": "360x360",
  "soc": "JL7012F6",
  "allow_write": false
}
```

En Windows, Bleak puede entregar un `address`/identifier distinto de la MAC que el reloj muestra físicamente. La resolución por nombre es preferible durante la exploración inicial.

## Comandos de la primera etapa

Escanear durante 15 segundos:

```powershell
.\.venv\Scripts\python.exe scripts\scan.py
```

Cambiar duración, filtrar y exportar advertising data:

```powershell
.\.venv\Scripts\python.exe scripts\scan.py --timeout 20 --name FRG --json captures\scan.json
```

Inspeccionar GATT y actualizar `docs/ble-map.md`:

```powershell
.\.venv\Scripts\python.exe scripts\inspect.py --device FRG
.\.venv\Scripts\python.exe scripts\inspect.py --address "<BLE_IDENTIFIER>"
```

Leer solo characteristics `READ`:

```powershell
.\.venv\Scripts\python.exe scripts\read_safe.py --device FRG
```

Monitorizar todas las characteristics `NOTIFY` y capturar una sesión:

```powershell
.\.venv\Scripts\python.exe scripts\monitor.py --device FRG --label baseline --all
```

Para una prueba acotada, usar `--duration 60`. Sin duración, detener con `Ctrl+C`; el archivo JSONL se cierra en la limpieza de la sesión.

Comparar dos sesiones:

```powershell
.\.venv\Scripts\python.exe scripts\compare_capture.py captures\idle.jsonl captures\heart_rate.jsonl
```

## Fase 2: snapshots y experimentos controlados

Snapshots READ antes/después de una medición:

```powershell
.\.venv\Scripts\python.exe scripts\read_safe.py --device FRG --label before_hr
.\.venv\Scripts\python.exe scripts\read_safe.py --device FRG --label after_hr
.\.venv\Scripts\python.exe scripts\compare_reads.py captures\safe_read_before_hr_<timestamp>.json captures\safe_read_after_hr_<timestamp>.json
```

Experimentos disponibles como plantillas en `docs/experiments/`. Durante cada sesión, la persona debe ejecutar la acción desde el reloj y anotar el resultado mostrado; el monitor no enviará comandos.

Actualizar el índice y el reporte:

```powershell
.\.venv\Scripts\python.exe scripts\index_captures.py
.\.venv\Scripts\python.exe scripts\generate_report.py
```

## Archivos generados

- `captures/gatt_<timestamp>.json`: mapa completo de servicios, characteristics, propiedades y descriptors.
- `captures/safe_read_<timestamp>.json`: valores legibles y decodificaciones numéricas básicas.
- `captures/<label>_<timestamp>.jsonl`: eventos de una sesión `NOTIFY`.
- `docs/ble-map.md`: mapa GATT actualizado automáticamente por `inspect.py`.
- `logs/forge.log`: log de ejecución.

## Arquitectura

```text
JOOG Forge
    │ BLE
    ▼
forge/ble (scanner, connector, GATT, reader, notifier)
    │ raw observations
    ▼
forge/capture + forge/protocol (JSON/JSONL y análisis offline)
    │ posteriormente
    ▼
FastAPI read-only / PWA experimental
```

La PWA queda deliberadamente para una etapa posterior; la API local read-only se habilitó después de verificar la conexión y revisar los primeros resultados reales del reloj.

## API local read-only

La conexión inicial ya fue verificada, por lo que también está disponible una API local sin endpoints de escritura:

```powershell
.\.venv\Scripts\python.exe -m uvicorn forge.api.app:app --reload
```

Swagger: `http://localhost:8000/docs`

Endpoints: `GET /devices`, `GET /devices/{id}`, `GET /devices/{id}/services`, `GET /devices/{id}/characteristics`, `GET /devices/{id}/battery`, `GET /captures` y `GET /captures/{id}`.

## Limitaciones conocidas

- No todos los adaptadores Bluetooth o drivers de Windows exponen RSSI y advertising data del mismo modo.
- Un servicio custom no demuestra por sí solo que sea un canal de comandos.
- Una característica `WRITE` o un servicio cuyo nombre contenga `OTA` no debe ejercitarse automáticamente.
- No se incluyen firmwares descargados ni investigación externa no verificada en esta entrega.

## Próximo paso seguro

Ejecutar `scan.py`, luego `inspect.py`, `read_safe.py` y una sesión baseline de `monitor.py`. Revisar los JSON generados y compartir los resultados antes de implementar cualquier funcionalidad de escritura, OTA, firmware o Forge OS.
