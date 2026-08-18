import Combine
import CoreBluetooth
import Foundation

public final class ForgeBluetoothClient: NSObject, ObservableObject {
    @Published public private(set) var status: ForgeClientStatus = .idle
    @Published public private(set) var devices: [ForgeDiscoveredDevice] = []
    @Published public private(set) var services: [ForgeServiceSnapshot] = []
    @Published public private(set) var events: [ForgeCaptureEvent] = []
    @Published public private(set) var lastError: String?
    @Published public private(set) var notificationsEnabled = false

    private var central: CBCentralManager!
    private var peripherals: [UUID: CBPeripheral] = [:]
    private var activePeripheral: CBPeripheral?
    private var pendingCharacteristicDiscovery = Set<CBUUID>()
    private var pendingReads = Set<CBUUID>()
    private let isoFormatter: ISO8601DateFormatter

    public override init() {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        isoFormatter = formatter
        super.init()
        central = CBCentralManager(delegate: self, queue: DispatchQueue.main)
    }

    public func startScan() {
        guard central.state == .poweredOn else {
            status = .unavailable
            lastError = "Bluetooth no está disponible o no está autorizado."
            return
        }

        devices.removeAll()
        lastError = nil
        status = .scanning
        central.scanForPeripherals(
            withServices: nil,
            options: [CBCentralManagerScanOptionAllowDuplicatesKey: false]
        )
    }

    public func stopScan() {
        central.stopScan()
        if status == .scanning {
            status = activePeripheral == nil ? .idle : .ready
        }
    }

    public func connect(to device: ForgeDiscoveredDevice) {
        guard let peripheral = peripherals[device.id] else {
            lastError = "El periférico ya no está disponible; vuelve a escanear."
            return
        }

        stopScan()
        activePeripheral = peripheral
        peripheral.delegate = self
        status = .connecting
        lastError = nil
        central.connect(peripheral, options: nil)
    }

    public func disconnect() {
        guard let peripheral = activePeripheral else { return }
        stopNotificationSubscriptions()
        central.cancelPeripheralConnection(peripheral)
    }

    /// Reads only characteristics whose properties explicitly include read.
    public func refreshReadOnlyValues() {
        guard let peripheral = activePeripheral else { return }
        for service in peripheral.services ?? [] {
            for characteristic in service.characteristics ?? [] {
                guard characteristic.properties.contains(.read) else { continue }
                pendingReads.insert(characteristic.uuid)
                peripheral.readValue(for: characteristic)
            }
        }
    }

    /// Notification subscriptions are disabled by default because enabling them
    /// changes the peripheral's CCCD state. Call this only for an explicit
    /// observation experiment.
    public func setNotificationSubscriptions(enabled: Bool) {
        guard let peripheral = activePeripheral else { return }
        notificationsEnabled = enabled

        for service in peripheral.services ?? [] {
            for characteristic in service.characteristics ?? [] {
                guard characteristic.properties.contains(.notify) else { continue }
                peripheral.setNotifyValue(enabled, for: characteristic)
            }
        }
    }

    public func stopNotificationSubscriptions() {
        setNotificationSubscriptions(enabled: false)
        notificationsEnabled = false
    }

    public func currentGattSnapshot() -> ForgeGattSnapshot? {
        guard let peripheral = activePeripheral else { return nil }
        return ForgeGattSnapshot(
            capturedAt: isoFormatter.string(from: Date()),
            deviceName: peripheral.name,
            deviceIdentifier: peripheral.identifier.uuidString,
            services: services
        )
    }

    public func eventsJSONL() throws -> String {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys]
        return try events
            .map { try encoder.encode($0) }
            .map { String(decoding: $0, as: UTF8.self) }
            .joined(separator: "\n")
    }

    private func record(
        operation: String,
        serviceUUID: String?,
        characteristicUUID: String?,
        data: Data
    ) {
        events.append(
            ForgeCaptureEvent(
                timestampUTC: isoFormatter.string(from: Date()),
                operation: operation,
                serviceUUID: serviceUUID,
                characteristicUUID: characteristicUUID,
                payloadHex: data.map { String(format: "%02x", $0) }.joined(separator: " ")
            )
        )
    }

    private func upsertService(_ service: CBService) {
        let characteristics = (service.characteristics ?? []).map {
            ForgeCharacteristicSnapshot(
                serviceUUID: service.uuid.uuidString.lowercased(),
                uuid: $0.uuid.uuidString.lowercased(),
                properties: propertyNames($0.properties)
            )
        }
        let snapshot = ForgeServiceSnapshot(
            uuid: service.uuid.uuidString.lowercased(),
            characteristics: characteristics
        )

        if let index = services.firstIndex(where: { $0.uuid == snapshot.uuid }) {
            services[index] = snapshot
        } else {
            services.append(snapshot)
        }
        services.sort { $0.uuid < $1.uuid }
    }

    private func propertyNames(_ properties: CBCharacteristicProperties) -> [String] {
        var names: [String] = []
        if properties.contains(.broadcast) { names.append("broadcast") }
        if properties.contains(.read) { names.append("read") }
        if properties.contains(.writeWithoutResponse) { names.append("write-without-response") }
        if properties.contains(.write) { names.append("write") }
        if properties.contains(.notify) { names.append("notify") }
        if properties.contains(.indicate) { names.append("indicate") }
        if properties.contains(.authenticatedSignedWrites) { names.append("authenticated-signed-writes") }
        if properties.contains(.extendedProperties) { names.append("extended-properties") }
        if properties.contains(.notifyEncryptionRequired) { names.append("notify-encryption-required") }
        if properties.contains(.indicateEncryptionRequired) { names.append("indicate-encryption-required") }
        return names
    }

    private func isCandidate(name: String?) -> Bool {
        guard let normalized = name?.lowercased() else { return false }
        return normalized.contains("frg")
            || normalized.contains("joog")
            || normalized.contains("forge")
            || normalized.contains("moy")
    }
}

extension ForgeBluetoothClient: CBCentralManagerDelegate {
    public func centralManagerDidUpdateState(_ central: CBCentralManager) {
        switch central.state {
        case .poweredOn:
            if status == .unavailable { status = .idle }
        case .unauthorized, .unsupported, .poweredOff, .resetting, .unknown:
            status = .unavailable
        @unknown default:
            status = .unavailable
        }
    }

    public func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String: Any],
        rssi RSSI: NSNumber
    ) {
        peripherals[peripheral.identifier] = peripheral
        let advertisedName = advertisementData[CBAdvertisementDataLocalNameKey] as? String
        let name = advertisedName ?? peripheral.name
        let device = ForgeDiscoveredDevice(
            id: peripheral.identifier,
            name: name,
            rssi: RSSI.intValue,
            isCandidate: isCandidate(name: name)
        )

        if let index = devices.firstIndex(where: { $0.id == device.id }) {
            devices[index] = device
        } else {
            devices.append(device)
            devices.sort { ($0.name ?? "") < ($1.name ?? "") }
        }
    }

    public func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        activePeripheral = peripheral
        status = .discovering
        services.removeAll()
        events.removeAll()
        peripheral.delegate = self
        peripheral.discoverServices(nil)
    }

    public func centralManager(
        _ central: CBCentralManager,
        didFailToConnect peripheral: CBPeripheral,
        error: Error?
    ) {
        status = .failed
        lastError = error?.localizedDescription ?? "No se pudo conectar."
    }

    public func centralManager(
        _ central: CBCentralManager,
        didDisconnectPeripheral peripheral: CBPeripheral,
        error: Error?
    ) {
        if activePeripheral?.identifier == peripheral.identifier {
            activePeripheral = nil
            notificationsEnabled = false
            status = .disconnected
        }
        if let error {
            lastError = error.localizedDescription
        }
    }
}

extension ForgeBluetoothClient: CBPeripheralDelegate {
    public func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard error == nil, let discoveredServices = peripheral.services else {
            status = .failed
            lastError = error?.localizedDescription ?? "No se pudieron descubrir los servicios."
            return
        }

        pendingCharacteristicDiscovery = Set(discoveredServices.map(\.uuid))
        peripheral.discoverCharacteristics(nil, for: discoveredServices)
    }

    public func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverCharacteristicsFor service: CBService,
        error: Error?
    ) {
        if let error {
            lastError = error.localizedDescription
        }
        upsertService(service)
        pendingCharacteristicDiscovery.remove(service.uuid)

        if pendingCharacteristicDiscovery.isEmpty {
            status = .ready
            if notificationsEnabled {
                setNotificationSubscriptions(enabled: true)
            }
        }
    }

    public func peripheral(
        _ peripheral: CBPeripheral,
        didUpdateValueFor characteristic: CBCharacteristic,
        error: Error?
    ) {
        pendingReads.remove(characteristic.uuid)
        guard let value = characteristic.value else {
            if let error { lastError = error.localizedDescription }
            return
        }

        let operation = characteristic.isNotifying ? "notify" : "read"
        let serviceUUID = characteristic.service?.uuid.uuidString.lowercased()
        record(
            operation: operation,
            serviceUUID: serviceUUID,
            characteristicUUID: characteristic.uuid.uuidString.lowercased(),
            data: value
        )
        if let error { lastError = error.localizedDescription }
    }

    public func peripheral(
        _ peripheral: CBPeripheral,
        didUpdateNotificationStateFor characteristic: CBCharacteristic,
        error: Error?
    ) {
        if let error {
            lastError = error.localizedDescription
        }
    }
}
