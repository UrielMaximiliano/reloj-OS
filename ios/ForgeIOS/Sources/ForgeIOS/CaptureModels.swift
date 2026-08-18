import Foundation

public struct ForgeDiscoveredDevice: Identifiable, Hashable, Sendable {
    public let id: UUID
    public let name: String?
    public let rssi: Int
    public let isCandidate: Bool

    public init(id: UUID, name: String?, rssi: Int, isCandidate: Bool) {
        self.id = id
        self.name = name
        self.rssi = rssi
        self.isCandidate = isCandidate
    }

    public var displayName: String {
        name ?? "BLE \(id.uuidString.prefix(8))"
    }
}

public enum ForgeClientStatus: String, Sendable {
    case idle
    case scanning
    case connecting
    case discovering
    case ready
    case disconnected
    case unavailable
    case failed
}

public struct ForgeCharacteristicSnapshot: Identifiable, Codable, Sendable {
    public let serviceUUID: String
    public let uuid: String
    public let properties: [String]

    public var id: String {
        "\(serviceUUID)/\(uuid)"
    }
}

public struct ForgeServiceSnapshot: Identifiable, Codable, Sendable {
    public let uuid: String
    public let characteristics: [ForgeCharacteristicSnapshot]

    public var id: String { uuid }
}

public struct ForgeCaptureEvent: Identifiable, Codable, Sendable {
    public let id: UUID
    public let schema: String
    public let timestampUTC: String
    public let source: String
    public let platform: String
    public let direction: String
    public let layer: String
    public let operation: String
    public let serviceUUID: String?
    public let characteristicUUID: String?
    public let handle: String?
    public let payloadHex: String
    public let encrypted: Bool
    public let rawRef: String?
    public let decodeConfidence: Double

    public init(
        id: UUID = UUID(),
        timestampUTC: String,
        operation: String,
        serviceUUID: String?,
        characteristicUUID: String?,
        payloadHex: String,
        rawRef: String? = nil
    ) {
        self.id = id
        self.schema = "ble-capture/v1"
        self.timestampUTC = timestampUTC
        self.source = "corebluetooth"
        self.platform = "ios"
        self.direction = "peripheral_to_central"
        self.layer = "gatt"
        self.operation = operation
        self.serviceUUID = serviceUUID
        self.characteristicUUID = characteristicUUID
        self.handle = nil
        self.payloadHex = payloadHex
        self.encrypted = false
        self.rawRef = rawRef
        self.decodeConfidence = 0.0
    }

    enum CodingKeys: String, CodingKey {
        case id
        case schema
        case timestampUTC = "timestamp_utc"
        case source
        case platform
        case direction
        case layer
        case operation
        case serviceUUID = "service_uuid"
        case characteristicUUID = "characteristic_uuid"
        case handle
        case payloadHex = "payload_hex"
        case encrypted
        case rawRef = "raw_ref"
        case decodeConfidence = "decode_confidence"
    }
}

public struct ForgeGattSnapshot: Codable, Sendable {
    public let capturedAt: String
    public let deviceName: String?
    public let deviceIdentifier: String
    public let services: [ForgeServiceSnapshot]

    enum CodingKeys: String, CodingKey {
        case capturedAt = "captured_at"
        case deviceName = "device_name"
        case deviceIdentifier = "device_identifier"
        case services
    }
}
