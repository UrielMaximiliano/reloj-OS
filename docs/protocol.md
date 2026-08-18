# Protocol analysis

> This report is observational. It does not prove command semantics or firmware compatibility.

- Packets analyzed: **4**
- Confidence labels: **CONFIRMED** is reserved for repeated byte-level facts; **LIKELY**, **POSSIBLE**, **HYPOTHESIS** and **UNKNOWN** do not authorize writes.

## Characteristic `00002a19-0000-1000-8000-00805f9b34fb`

- Packets: **4**
- Packet lengths: `[1]`
- Variable offsets: `[0]`.
- offset 0: values 18, 19, 2b, 67 (POSSIBLE discriminator/command ID; semantics UNKNOWN)

No packet meaning, command ID, timestamp field or checksum is promoted to CONFIRMED without repeated controlled captures.
