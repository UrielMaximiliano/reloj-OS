# JOOG Forge reverse-engineering report

> Generated from local GATT, safe-read and capture evidence. No BLE write is performed by report generation.

## Device

- Name: `FRG`
- Identifier: `41:88:11:E2:88:31`
- Firmware: `MOY-8QJ4-2.0.8`
- Software/manufacturer: `MOYOUNG-V2`
- SoC: `JL7012F6` (reported hardware context)

## GATT map

- Services: **9**
- Custom/unknown services: **4**
- Characteristics: **21**
- READ: **11**; WRITE: **6**; NOTIFY: **7**; INDICATE: **1**
- Detailed map: [docs/ble-map.md](ble-map.md)

## Safe-read evidence

- Snapshot: `safe_read_after_heart_rate_01_20260818_194137.json`
- Read values: **11**
- Writes attempted: **false**

## Observed traffic

- Notification packets across local JSONL captures: **4**
- Characteristics with packets: `['00002a19-0000-1000-8000-00805f9b34fb']`
- Protocol analysis: [docs/protocol.md](protocol.md)

## Candidate protocol channels

- `0000feea-0000-1000-8000-00805f9b34fb` — TX candidates `['0000fee2-0000-1000-8000-00805f9b34fb', '0000fee5-0000-1000-8000-00805f9b34fb', '0000fee6-0000-1000-8000-00805f9b34fb']`; RX candidates `['0000fee1-0000-1000-8000-00805f9b34fb', '0000fee3-0000-1000-8000-00805f9b34fb']` — **POSSIBLE / UNCONFIRMED**
- `0000190e-0000-1000-8000-00805f9b34fb` — TX candidates `['00000004-0000-1000-8000-00805f9b34fb']`; RX candidates `['00000003-0000-1000-8000-00805f9b34fb']` — **POSSIBLE / UNCONFIRMED**
- `0000ae00-0000-1000-8000-00805f9b34fb` — TX candidates `['0000ae01-0000-1000-8000-00805f9b34fb']`; RX candidates `['0000ae02-0000-1000-8000-00805f9b34fb']` — **POSSIBLE / UNCONFIRMED**

## External research

- [docs/external-protocol-research.md](external-protocol-research.md)
- FEEA layout and MOYOUNG-V2 identity have a strong family-level match to Gadgetbridge, but no real command packet has been captured.
- AE00 and 190E remain unknown for this watch.

## OTA assessment

- [docs/ota-analysis.md](ota-analysis.md)
- Status: **UNKNOWN**; no write or OTA channel has been exercised.

## Open questions

- Which notifications appear when the watch itself starts HR or SpO2?
- Do FEEA FEE1/FEE3 packets appear spontaneously during steps or measurement?
- Are 190E and AE00 active protocol channels or unrelated/vendor helper services?
- Is the public Moyoung V2 frame format identical on this firmware?

## Next safe experiments

- Repeat idle for 30 seconds.
- Run HR and SpO2 three times each with manual event timestamps.
- Compare safe-read snapshots before/after each measurement.
- Do not enable WRITE until a real request/response trace or independently verified matching implementation exists.

## Capture index

- [captures/index.json](../captures/index.json)
