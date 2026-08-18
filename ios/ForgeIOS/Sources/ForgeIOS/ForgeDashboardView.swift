#if canImport(SwiftUI)
import SwiftUI

public struct ForgeDashboardView: View {
    @StateObject private var client: ForgeBluetoothClient

    public init(client: ForgeBluetoothClient = ForgeBluetoothClient()) {
        _client = StateObject(wrappedValue: client)
    }

    public var body: some View {
        NavigationStack {
            List {
                Section("Estado") {
                    LabeledContent("Bluetooth", value: client.status.rawValue)
                    if let lastError = client.lastError {
                        Text(lastError)
                            .foregroundStyle(.red)
                    }
                    Button("Leer characteristics READ") {
                        client.refreshReadOnlyValues()
                    }
                    .disabled(client.status != .ready)
                }

                Section("Dispositivos") {
                    if client.devices.isEmpty {
                        Text("Pulsa Escanear para buscar FRG/JOOG.")
                            .foregroundStyle(.secondary)
                    }
                    ForEach(client.devices) { device in
                        Button {
                            client.connect(to: device)
                        } label: {
                            HStack {
                                VStack(alignment: .leading) {
                                    Text(device.displayName)
                                    Text(device.id.uuidString)
                                        .font(.caption2)
                                        .foregroundStyle(.secondary)
                                }
                                Spacer()
                                Text("\(device.rssi) dBm")
                                    .font(.caption)
                                if device.isCandidate {
                                    Image(systemName: "checkmark.seal")
                                        .foregroundStyle(.green)
                                }
                            }
                        }
                    }
                }

                Section("GATT") {
                    ForEach(client.services) { service in
                        VStack(alignment: .leading) {
                            Text(service.uuid)
                                .font(.caption)
                            Text("\(service.characteristics.count) characteristics")
                                .foregroundStyle(.secondary)
                        }
                    }
                }

                Section("Eventos") {
                    if client.events.isEmpty {
                        Text("Sin eventos todavía.")
                            .foregroundStyle(.secondary)
                    }
                    ForEach(client.events.suffix(50)) { event in
                        VStack(alignment: .leading) {
                            Text("\(event.operation) · \(event.characteristicUUID ?? "unknown")")
                            Text(event.payloadHex.isEmpty ? "(vacío)" : event.payloadHex)
                                .font(.caption.monospaced())
                            Text(event.timestampUTC)
                                .font(.caption2)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
            .navigationTitle("JOOG Forge iOS")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Escanear") {
                        client.startScan()
                    }
                }
                ToolbarItem(placement: .topBarLeading) {
                    Button("Desconectar") {
                        client.disconnect()
                    }
                    .disabled(client.status == .idle || client.status == .disconnected)
                }
            }
        }
    }
}
#endif
