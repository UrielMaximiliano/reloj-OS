# BLE map

> Generated from a live GATT enumeration. No BLE writes are performed by the exporter.

- Captured: `2026-08-18T22:49:26.248082Z`
- Device: `FRG`
- Address/identifier: `41:88:11:E2:88:31`

## Summary

- Services: **9**
- Custom services: **4**
- Characteristics: **21**
- READ values captured: **11**

## Service `00001800-0000-1000-8000-00805f9b34fb`

- Name: Generic Access
- Type: **STANDARD**
- Description: Generic Access Profile

| Characteristic UUID | Properties | Descriptors | Current readable value | Notification observed | Write available | Interpretation | Confidence |
|---|---|---:|---|---|---|---|---|
| `00002a00-0000-1000-8000-00805f9b34fb` | `read, write` | 0 | `46 52 47` | NO | YES | TX candidate (PC -> watch) | POSSIBLE |

### Characteristic `00002a00-0000-1000-8000-00805f9b34fb`

- Description: Device Name
- Properties: `read, write`
- Descriptors: 0
- Interpretation: **TX candidate (PC -> watch)**
- Confidence: **POSSIBLE**

- Current readable value: `46 52 47`
- UTF-8: `FRG`
- Numeric: uint8=`70`, uint16 LE=`21062`, uint16 BE=`18002`, uint32 LE=`—`, uint32 BE=`—`
- Notification observed: **NO / not observed in this session**
- Write available: **YES**


## Service `00001801-0000-1000-8000-00805f9b34fb`

- Name: Generic Attribute
- Type: **STANDARD**
- Description: Generic Attribute Profile

| Characteristic UUID | Properties | Descriptors | Current readable value | Notification observed | Write available | Interpretation | Confidence |
|---|---|---:|---|---|---|---|---|
| `00002a05-0000-1000-8000-00805f9b34fb` | `indicate` | 1 | `not read` | NO | NO | RX candidate (watch -> PC) | POSSIBLE |

### Characteristic `00002a05-0000-1000-8000-00805f9b34fb`

- Description: Service Changed
- Properties: `indicate`
- Descriptors: 1
- Interpretation: **RX candidate (watch -> PC)**
- Confidence: **POSSIBLE**

- Current readable value: `not read in this inspection`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**

  - Descriptor `00002902-0000-1000-8000-00805f9b34fb`: Client Characteristic Configuration

## Service `0000180d-0000-1000-8000-00805f9b34fb`

- Name: Heart Rate
- Type: **STANDARD**
- Description: Heart Rate

| Characteristic UUID | Properties | Descriptors | Current readable value | Notification observed | Write available | Interpretation | Confidence |
|---|---|---:|---|---|---|---|---|
| `00002a37-0000-1000-8000-00805f9b34fb` | `notify` | 1 | `not read` | NO | NO | RX candidate (watch -> PC) | POSSIBLE |
| `00002a38-0000-1000-8000-00805f9b34fb` | `read` | 0 | `01` | NO | NO | readable state | UNKNOWN |

### Characteristic `00002a37-0000-1000-8000-00805f9b34fb`

- Description: Heart Rate Measurement
- Properties: `notify`
- Descriptors: 1
- Interpretation: **RX candidate (watch -> PC)**
- Confidence: **POSSIBLE**

- Current readable value: `not read in this inspection`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**

  - Descriptor `00002902-0000-1000-8000-00805f9b34fb`: Client Characteristic Configuration

### Characteristic `00002a38-0000-1000-8000-00805f9b34fb`

- Description: Body Sensor Location
- Properties: `read`
- Descriptors: 0
- Interpretation: **readable state**
- Confidence: **UNKNOWN**

- Current readable value: `01`
- UTF-8: `—`
- Numeric: uint8=`1`, uint16 LE=`—`, uint16 BE=`—`, uint32 LE=`—`, uint32 BE=`—`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**


## Service `0000180f-0000-1000-8000-00805f9b34fb`

- Name: Battery Service
- Type: **STANDARD**
- Description: Battery Service

| Characteristic UUID | Properties | Descriptors | Current readable value | Notification observed | Write available | Interpretation | Confidence |
|---|---|---:|---|---|---|---|---|
| `00002a19-0000-1000-8000-00805f9b34fb` | `notify, read` | 1 | `76` | NO | NO | telemetry candidate (watch -> PC) | POSSIBLE |

### Characteristic `00002a19-0000-1000-8000-00805f9b34fb`

- Description: Battery Level
- Properties: `notify, read`
- Descriptors: 1
- Interpretation: **telemetry candidate (watch -> PC)**
- Confidence: **POSSIBLE**

- Current readable value: `76`
- UTF-8: `v`
- Numeric: uint8=`118`, uint16 LE=`—`, uint16 BE=`—`, uint32 LE=`—`, uint32 BE=`—`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**

  - Descriptor `00002902-0000-1000-8000-00805f9b34fb`: Client Characteristic Configuration

## Service `0000180a-0000-1000-8000-00805f9b34fb`

- Name: Device Information
- Type: **STANDARD**
- Description: Device Information

| Characteristic UUID | Properties | Descriptors | Current readable value | Notification observed | Write available | Interpretation | Confidence |
|---|---|---:|---|---|---|---|---|
| `00002a25-0000-1000-8000-00805f9b34fb` | `read` | 0 | `46 39 32 42 41 34 46 35` | NO | NO | readable state | UNKNOWN |
| `00002a26-0000-1000-8000-00805f9b34fb` | `read` | 0 | `4a 4c 51 46 4e 49 4d 47 31 2e 39` | NO | NO | readable state | UNKNOWN |
| `00002a28-0000-1000-8000-00805f9b34fb` | `read` | 0 | `4d 4f 59 2d 38 51 4a 34 2d 32 2e 30 2e 38` | NO | NO | readable state | UNKNOWN |
| `00002a29-0000-1000-8000-00805f9b34fb` | `read` | 0 | `4d 4f 59 4f 55 4e 47 2d 56 32` | NO | NO | readable state | UNKNOWN |

### Characteristic `00002a25-0000-1000-8000-00805f9b34fb`

- Description: Serial Number String
- Properties: `read`
- Descriptors: 0
- Interpretation: **readable state**
- Confidence: **UNKNOWN**

- Current readable value: `46 39 32 42 41 34 46 35`
- UTF-8: `F92BA4F5`
- Numeric: uint8=`70`, uint16 LE=`14662`, uint16 BE=`17977`, uint32 LE=`1110587718`, uint32 BE=`1178153538`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**


### Characteristic `00002a26-0000-1000-8000-00805f9b34fb`

- Description: Firmware Revision String
- Properties: `read`
- Descriptors: 0
- Interpretation: **readable state**
- Confidence: **UNKNOWN**

- Current readable value: `4a 4c 51 46 4e 49 4d 47 31 2e 39`
- UTF-8: `JLQFNIMG1.9`
- Numeric: uint8=`74`, uint16 LE=`19530`, uint16 BE=`19020`, uint32 LE=`1179733066`, uint32 BE=`1246515526`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**


### Characteristic `00002a28-0000-1000-8000-00805f9b34fb`

- Description: Software Revision String
- Properties: `read`
- Descriptors: 0
- Interpretation: **readable state**
- Confidence: **UNKNOWN**

- Current readable value: `4d 4f 59 2d 38 51 4a 34 2d 32 2e 30 2e 38`
- UTF-8: `MOY-8QJ4-2.0.8`
- Numeric: uint8=`77`, uint16 LE=`20301`, uint16 BE=`19791`, uint32 LE=`760827725`, uint32 BE=`1297045805`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**


### Characteristic `00002a29-0000-1000-8000-00805f9b34fb`

- Description: Manufacturer Name String
- Properties: `read`
- Descriptors: 0
- Interpretation: **readable state**
- Confidence: **UNKNOWN**

- Current readable value: `4d 4f 59 4f 55 4e 47 2d 56 32`
- UTF-8: `MOYOUNG-V2`
- Numeric: uint8=`77`, uint16 LE=`20301`, uint16 BE=`19791`, uint32 LE=`1331253069`, uint32 BE=`1297045839`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**


## Service `0000feea-0000-1000-8000-00805f9b34fb`

- Name: Unknown
- Type: **CUSTOM**
- Description: Swirl Networks: Inc.

| Characteristic UUID | Properties | Descriptors | Current readable value | Notification observed | Write available | Interpretation | Confidence |
|---|---|---:|---|---|---|---|---|
| `0000fee1-0000-1000-8000-00805f9b34fb` | `notify, read` | 1 | `00 00 00 00 00 00 00 00 00` | NO | NO | telemetry candidate (watch -> PC) | POSSIBLE |
| `0000fee2-0000-1000-8000-00805f9b34fb` | `write-without-response` | 0 | `not read` | NO | YES | TX candidate (PC -> watch) | POSSIBLE |
| `0000fee3-0000-1000-8000-00805f9b34fb` | `notify` | 1 | `not read` | NO | NO | RX candidate (watch -> PC) | POSSIBLE |
| `0000fee4-0000-1000-8000-00805f9b34fb` | `read` | 0 | `` | NO | NO | readable state | UNKNOWN |
| `0000fee5-0000-1000-8000-00805f9b34fb` | `write-without-response` | 0 | `not read` | NO | YES | TX candidate (PC -> watch) | POSSIBLE |
| `0000fee6-0000-1000-8000-00805f9b34fb` | `write-without-response` | 0 | `not read` | NO | YES | TX candidate (PC -> watch) | POSSIBLE |

### Characteristic `0000fee1-0000-1000-8000-00805f9b34fb`

- Description: Anhui Huami Information Technology Co.
- Properties: `notify, read`
- Descriptors: 1
- Interpretation: **telemetry candidate (watch -> PC)**
- Confidence: **POSSIBLE**

- Current readable value: `00 00 00 00 00 00 00 00 00`
- UTF-8: `—`
- Numeric: uint8=`0`, uint16 LE=`0`, uint16 BE=`0`, uint32 LE=`0`, uint32 BE=`0`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**

  - Descriptor `00002902-0000-1000-8000-00805f9b34fb`: Client Characteristic Configuration

### Characteristic `0000fee2-0000-1000-8000-00805f9b34fb`

- Description: Anki: Inc.
- Properties: `write-without-response`
- Descriptors: 0
- Interpretation: **TX candidate (PC -> watch)**
- Confidence: **POSSIBLE**

- Current readable value: `not read in this inspection`
- Notification observed: **NO / not observed in this session**
- Write available: **YES**


### Characteristic `0000fee3-0000-1000-8000-00805f9b34fb`

- Description: Anki: Inc.
- Properties: `notify`
- Descriptors: 1
- Interpretation: **RX candidate (watch -> PC)**
- Confidence: **POSSIBLE**

- Current readable value: `not read in this inspection`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**

  - Descriptor `00002902-0000-1000-8000-00805f9b34fb`: Client Characteristic Configuration

### Characteristic `0000fee4-0000-1000-8000-00805f9b34fb`

- Description: Nordic Semiconductor ASA
- Properties: `read`
- Descriptors: 0
- Interpretation: **readable state**
- Confidence: **UNKNOWN**

- Current readable value: `empty`
- UTF-8: `—`
- Numeric: uint8=`—`, uint16 LE=`—`, uint16 BE=`—`, uint32 LE=`—`, uint32 BE=`—`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**


### Characteristic `0000fee5-0000-1000-8000-00805f9b34fb`

- Description: Nordic Semiconductor ASA
- Properties: `write-without-response`
- Descriptors: 0
- Interpretation: **TX candidate (PC -> watch)**
- Confidence: **POSSIBLE**

- Current readable value: `not read in this inspection`
- Notification observed: **NO / not observed in this session**
- Write available: **YES**


### Characteristic `0000fee6-0000-1000-8000-00805f9b34fb`

- Description: Seed Labs: Inc.
- Properties: `write-without-response`
- Descriptors: 0
- Interpretation: **TX candidate (PC -> watch)**
- Confidence: **POSSIBLE**

- Current readable value: `not read in this inspection`
- Notification observed: **NO / not observed in this session**
- Write available: **YES**


## Service `0000fee7-0000-1000-8000-00805f9b34fb`

- Name: Unknown
- Type: **CUSTOM**
- Description: Tencent Holdings Limited

| Characteristic UUID | Properties | Descriptors | Current readable value | Notification observed | Write available | Interpretation | Confidence |
|---|---|---:|---|---|---|---|---|
| `0000fec9-0000-1000-8000-00805f9b34fb` | `read` | 0 | `41 88 11 e2 88 31` | NO | NO | readable state | UNKNOWN |
| `0000fea1-0000-1000-8000-00805f9b34fb` | `notify, read` | 1 | `01 00 00 00` | NO | NO | telemetry candidate (watch -> PC) | POSSIBLE |

### Characteristic `0000fec9-0000-1000-8000-00805f9b34fb`

- Description: Apple: Inc.
- Properties: `read`
- Descriptors: 0
- Interpretation: **readable state**
- Confidence: **UNKNOWN**

- Current readable value: `41 88 11 e2 88 31`
- UTF-8: `—`
- Numeric: uint8=`65`, uint16 LE=`34881`, uint16 BE=`16776`, uint32 LE=`3792799809`, uint32 BE=`1099436514`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**


### Characteristic `0000fea1-0000-1000-8000-00805f9b34fb`

- Description: Intrepid Control Systems: Inc.
- Properties: `notify, read`
- Descriptors: 1
- Interpretation: **telemetry candidate (watch -> PC)**
- Confidence: **POSSIBLE**

- Current readable value: `01 00 00 00`
- UTF-8: `—`
- Numeric: uint8=`1`, uint16 LE=`1`, uint16 BE=`256`, uint32 LE=`1`, uint32 BE=`16777216`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**

  - Descriptor `00002902-0000-1000-8000-00805f9b34fb`: Client Characteristic Configuration

## Service `0000190e-0000-1000-8000-00805f9b34fb`

- Name: Unknown
- Type: **CUSTOM**
- Description: Vendor specific

| Characteristic UUID | Properties | Descriptors | Current readable value | Notification observed | Write available | Interpretation | Confidence |
|---|---|---:|---|---|---|---|---|
| `00000004-0000-1000-8000-00805f9b34fb` | `write-without-response` | 0 | `not read` | NO | YES | TX candidate (PC -> watch) | POSSIBLE |
| `00000003-0000-1000-8000-00805f9b34fb` | `notify` | 1 | `not read` | NO | NO | RX candidate (watch -> PC) | POSSIBLE |

### Characteristic `00000004-0000-1000-8000-00805f9b34fb`

- Description: Vendor specific
- Properties: `write-without-response`
- Descriptors: 0
- Interpretation: **TX candidate (PC -> watch)**
- Confidence: **POSSIBLE**

- Current readable value: `not read in this inspection`
- Notification observed: **NO / not observed in this session**
- Write available: **YES**


### Characteristic `00000003-0000-1000-8000-00805f9b34fb`

- Description: RFCOMM
- Properties: `notify`
- Descriptors: 1
- Interpretation: **RX candidate (watch -> PC)**
- Confidence: **POSSIBLE**

- Current readable value: `not read in this inspection`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**

  - Descriptor `00002902-0000-1000-8000-00805f9b34fb`: Client Characteristic Configuration

## Service `0000ae00-0000-1000-8000-00805f9b34fb`

- Name: Unknown
- Type: **CUSTOM**
- Description: Vendor specific

| Characteristic UUID | Properties | Descriptors | Current readable value | Notification observed | Write available | Interpretation | Confidence |
|---|---|---:|---|---|---|---|---|
| `0000ae01-0000-1000-8000-00805f9b34fb` | `write-without-response` | 0 | `not read` | NO | YES | TX candidate (PC -> watch) | POSSIBLE |
| `0000ae02-0000-1000-8000-00805f9b34fb` | `notify` | 1 | `not read` | NO | NO | RX candidate (watch -> PC) | POSSIBLE |

### Characteristic `0000ae01-0000-1000-8000-00805f9b34fb`

- Description: Vendor specific
- Properties: `write-without-response`
- Descriptors: 0
- Interpretation: **TX candidate (PC -> watch)**
- Confidence: **POSSIBLE**

- Current readable value: `not read in this inspection`
- Notification observed: **NO / not observed in this session**
- Write available: **YES**


### Characteristic `0000ae02-0000-1000-8000-00805f9b34fb`

- Description: Vendor specific
- Properties: `notify`
- Descriptors: 1
- Interpretation: **RX candidate (watch -> PC)**
- Confidence: **POSSIBLE**

- Current readable value: `not read in this inspection`
- Notification observed: **NO / not observed in this session**
- Write available: **NO**

  - Descriptor `00002902-0000-1000-8000-00805f9b34fb`: Client Characteristic Configuration

## Possible command channels

- Structural candidate only; no writes were attempted.

- Service `0000feea-0000-1000-8000-00805f9b34fb` — WRITE: `0000fee2-0000-1000-8000-00805f9b34fb, 0000fee5-0000-1000-8000-00805f9b34fb, 0000fee6-0000-1000-8000-00805f9b34fb`; NOTIFY/INDICATE: `0000fee1-0000-1000-8000-00805f9b34fb, 0000fee3-0000-1000-8000-00805f9b34fb` — **POSSIBLE / UNCONFIRMED**
- Service `0000190e-0000-1000-8000-00805f9b34fb` — WRITE: `00000004-0000-1000-8000-00805f9b34fb`; NOTIFY/INDICATE: `00000003-0000-1000-8000-00805f9b34fb` — **POSSIBLE / UNCONFIRMED**
- Service `0000ae00-0000-1000-8000-00805f9b34fb` — WRITE: `0000ae01-0000-1000-8000-00805f9b34fb`; NOTIFY/INDICATE: `0000ae02-0000-1000-8000-00805f9b34fb` — **POSSIBLE / UNCONFIRMED**

## OTA / DFU observation

- Status: **UNKNOWN unless the enumerated evidence below exists.**

- No service or characteristic name/UUID matched the conservative OTA keyword screen.
