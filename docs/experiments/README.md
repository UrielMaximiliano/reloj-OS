# Controlled experiments

Each experiment changes one observable variable and keeps the BLE client read-only. Run the monitor first, perform the manual action on the watch, then record the displayed result and approximate time in this document.

Required evidence per run:

- capture filename;
- firmware and software values from the latest safe-read snapshot;
- start/end UTC timestamps;
- manual event timestamps;
- displayed result, if any;
- UUIDs and raw packets involved;
- comparison against `idle`;
- interpretation and confidence: `CONFIRMED`, `LIKELY`, `POSSIBLE`, `UNKNOWN`.

Do not send a packet to the watch. Do not use a command inferred from public code.
