# Hardware y alcance conocido

## Identidad reportada

| Campo | Valor | Estado |
|---|---|---|
| Marca | JOOG | Reportado por el usuario |
| Modelo comercial | Forge / FRG | Reportado por el usuario |
| Firmware visible | `MOY-8QJ4-2.0.8` | Reportado; debe verificarse por GATT si está expuesto |
| SoC | JieLi / Jerry `JL7012F6` | Reportado; no se infiere compatibilidad de firmware |
| Pantalla | `1.52"`, `360x360` | Reportado |
| Bluetooth | `5.3` | Reportado |
| App oficial | Da Fit | Reportado |
| Fabricante/ecosistema | aparentemente Moyoung / Da Fit | Hipótesis, no confirmada por el dispositivo |
| Sensor cardíaco | `VC30F-S` | Reportado |
| MAC visible | `41:88:11:E2:88:31` | No usar como único identificador en Windows |

## Cable

El cable magnético fue conectado a una notebook Windows y no apareció un dispositivo USB adicional. En esta investigación se asume únicamente como alimentación hasta contar con evidencia contraria; el canal de trabajo es BLE.

## Regla de identificación

En Windows, el backend de Bleak puede mostrar un identificador lógico o una dirección que no coincide con la MAC impresa o mostrada por el reloj. Registrar siempre nombre, identifier, RSSI, advertising data y fecha de captura.

## No inferir

El SoC, el nombre comercial o la aplicación Da Fit no bastan para inferir UUIDs propietarios, formato de paquetes, bootloader, mapa de memoria ni compatibilidad de un archivo `.ufw` de otro reloj.
