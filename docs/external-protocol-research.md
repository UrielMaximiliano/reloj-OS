# External protocol research

Research is comparative only. No command from an external project has been sent to the JOOG Forge.

## 1. Gadgetbridge Moyoung protocol documentation

- Repository/site: [Gadgetbridge Moyoung protocol](https://gadgetbridge.org/internals/specifics/moyoung-protocol/)
- Relevant evidence: identifies a Moyoung V1/V2 family used by Da Fit-managed watches; uses manufacturer `MOYOUNG` versus `MOYOUNG-V2` to distinguish protocol variants; documents a V2 frame beginning `FE EA` and a data-out write characteristic plus data-in notify characteristic.
- Match to our watch: **STRONG / PARTIAL**. Our GATT exposes full UUID service `0000feea-0000-1000-8000-00805f9b34fb`, `MOYOUNG-V2`, and FEE2/FEE3 properties matching the documented direction. No packet exchange has been captured yet.
- Confidence: `LIKELY` for FEEA being the main Moyoung data service; `UNKNOWN` for any command semantics on this specific watch.

## 2. Gadgetbridge Da Fit constants and reverse-engineering notes

- Repository/file: [DaFitConstants.java, Gadgetbridge Gitea](https://gitea.it/Freeyourgadget/Gadgetbridge/src/commit/ee0c95fb71de37a0a5165470a0ae387b3dbdec0d/app/src/main/java/nodomain/freeyourgadget/gadgetbridge/devices/dafit/DaFitConstants.java)
- Relevant evidence: maps FEEA to the Da Fit service, FEE1 to steps, FEE2 to data-out, FEE3 to data-in; documents FEE7 with FEA1/FEC9 as another custom service and marks several endpoints as uncertain or unsupported on the author's watch.
- Match to our watch: **STRONG / PARTIAL**. Our GATT has the same FEEA/FEE1-FEE6 layout and the same FEE7/FEA1/FEC9 layout. The property pattern agrees. This does not prove our FRG uses every command in that file.
- Confidence: `LIKELY` for structural role mapping; `UNKNOWN` for packet format until real notifications are captured.

## 3. Gadgetbridge device support

- Source: [Moyoung / Da Fit support](https://gadgetbridge.org/gadgets/wearables/moyoung/)
- Relevant evidence: supports battery, historical/live activity, heart rate, SpO2, sleep and many controls across multiple Moyoung devices, while warning that individual watches may expose different feature subsets.
- Match to our watch: **PARTIAL**. The firmware prefix `MOY-`, manufacturer `MOYOUNG-V2`, Da Fit app and FEEA layout fit the family. JOOG Forge / FRG is not identified as a tested Gadgetbridge model in the page consulted.
- Confidence: `LIKELY` for ecosystem membership; `UNKNOWN` for feature support on FRG.

## 4. Community DaFitDesktop implementation

- Source: [DaFitDesktop reverse-engineering article](https://arijitk.in/posts/dafit-desktop-reverse-engineering-ble-smart-bands/)
- Relevant evidence: describes FEEA/FEE1/FEE2/FEE3 roles and a community MOYOUNG-V2 packet model.
- Match to our watch: **PARTIAL**. The GATT layout agrees, but this is a different community device and source implementation. It is not sufficient authorization to transmit packets.
- Confidence: `POSSIBLE` as a cross-check only.

## 5. CRREPA / SN60-Plus search hit

- Source: [CRREPA reverse-engineering page](https://x-noname.ru/prochee/reverse-ble-protocol-for-sn60-plus-crrepa)
- Relevant evidence: search results associate a CRREPA watch with FEEA.
- Match to our watch: **UNKNOWN**. The page was rate-limited during retrieval and a UUID match alone cannot establish firmware or protocol compatibility.
- Confidence: `UNKNOWN`.

## 6. AE00 / AE01 / AE02 results

- Sources: [Fox protocol](https://buttplug.io/stpihkal/protocols/fox/), [Waveshare 10 DOF BLE](https://www.waveshare.com/wiki/10_DOF_ROS_IMU_%28A%29), [BLE thermal-printer reverse engineering](https://parzivail.github.io/ble-thermal-printer/)
- Relevant evidence: AE01/AE02 and AE00 appear in unrelated devices such as actuators, sensors and printers; roles vary by service and product.
- Match to our watch: **NO direct match established**. The FRG AE00/AE01/AE02 structural pairing is a candidate only and must not inherit meanings from these unrelated devices.
- Confidence: `UNKNOWN`.

## 7. 190E search

- Search result: exact UUID searches did not produce a relevant Da Fit/Moyoung/Gadgetbridge protocol implementation.
- Match to our watch: **UNKNOWN**.
- Confidence: `UNKNOWN`.

## 8. JL7012F6 and firmware searches

- Public product pages and manuals show JL7012F6 watches frequently paired with Da Fit and advertise OTA support, for example [JL7012F6 watch specification](https://manuals.plus/m/9c0b262f504b7cebfb958744a5c148d8c26940955b3fbe6c2abcf36cce8e3a67) and [JL7012 watch manual](https://manuals.plus/relogio/jl7012-smart-watches-manual).
- Match to our watch: **PARTIAL**. They support the ecosystem hypothesis, not the identity of the Forge firmware or OTA format.
- `MOY-8QJ4-2.0.8`, `MOY-8QJ4`, and `8QJ4`: no exact public firmware artifact was found in this search.
- Confidence: `UNKNOWN` for firmware compatibility.

## Safety conclusion

The strongest safe conclusion is that FRG is very likely a Moyoung V2 / Da Fit-family device and that FEEA is the leading candidate for its main data channel. That is enough to guide observation and capture analysis, not enough to enable WRITE. AE00 and 190E remain unknown.
