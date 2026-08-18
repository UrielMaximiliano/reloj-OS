# JOOG Forge iOS

Esta carpeta agrega una base nativa para iOS usando CoreBluetooth. El objetivo
actual es conectar, enumerar GATT, hacer READ explícitos y guardar eventos
normalizados. No contiene `writeValue`, OTA, DFU, reset ni replay de paquetes.

## Integración en Xcode

1. Crea una app iOS SwiftUI en Xcode.
2. Añade el paquete local `ios/ForgeIOS` con **Add Local Package**.
3. Añade las claves de `ForgeIOS/Info.plist.example` al `Info.plist` de la app.
4. Usa `ForgeDashboardView()` como vista inicial:

```swift
import ForgeIOS
import SwiftUI

@main
struct ForgeApp: App {
    var body: some Scene {
        WindowGroup {
            ForgeDashboardView()
        }
    }
}
```

## Seguridad del primer prototipo

- El escaneo y las lecturas usan CoreBluetooth.
- Antes de conectar desde esta app, cierra Da Fit y cualquier otro cliente BLE;
  el reloj puede aceptar una sola conexión útil a la vez.
- Las suscripciones NOTIFY están desactivadas por defecto porque cambian el
  estado CCCD del periférico. Solo deben habilitarse para un experimento
  explícito llamando `setNotificationSubscriptions(enabled: true)`.
- iOS no entrega una dirección MAC ni un HCI snoop crudo; el identificador
  disponible es el UUID local de `CBPeripheral`.
- Los eventos se exportan como JSONL `ble-capture/v1`, compatible con el plan
  portable del proyecto.
- Los bytes se conservan en crudo y `decodeConfidence` queda en cero hasta
  tener una captura correlacionada con una acción de Da Fit.

Esta implementación permite empezar con el iPhone 16 Pro sin inventar comandos.
Para conocer el tráfico que Da Fit ya intercambia internamente se seguirá
necesitando una captura aérea BLE o una fuente HCI externa.
