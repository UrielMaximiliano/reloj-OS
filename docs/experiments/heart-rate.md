# Experiment: heart rate

Command:

```powershell
.\.venv\Scripts\python.exe scripts\monitor.py --device FRG --label heart_rate --duration 50 --all
```

Timeline: 0-10 s idle; at 10 s open heart-rate measurement from the watch; 10-40 s wait; 40-50 s idle.

## Run record

- Date/time UTC:
- Firmware:
- Displayed BPM:
- Approximate result time:
- Capture:
- UUIDs involved:
- Packets:
- Differences versus idle:
- Interpretation:
- Confidence: `UNKNOWN` until repeated captures support a relationship

## Run record: heart_rate_01

- Date/time UTC: `2026-08-18 22:40:10` to `22:41:12`
- Firmware: `MOY-8QJ4-2.0.8`
- Displayed BPM: not recorded
- Approximate result time: not recorded
- Capture: `captures/heart_rate_01_20260818_194010.jsonl`
- UUIDs involved: `00002a37` subscribed; only `00002a19` emitted a notification
- Packets: battery `00002a19`, raw `67` (one packet)
- Differences versus idle: no Heart Rate Measurement packet observed
- Interpretation: connection and NOTIFY subscription succeeded, but this run does not prove that the watch publishes heart rate over BLE; the manual measurement action was not observed in the capture
- Confidence: `UNKNOWN`; repeat while visibly starting the measurement on the watch

## Run record: heart_rate_after_dafit

- Date/time UTC: `2026-08-18 22:50:38` to `22:52:09`
- Firmware: `MOY-8QJ4-2.0.8`
- Displayed BPM: not recorded
- Approximate result time: not recorded
- Capture: `captures/heart_rate_after_dafit_20260818_195038.jsonl`
- UUIDs involved: `00002a37` subscribed; `00002a19` emitted two notifications
- Packets: battery `00002a19`, raw `19` and `18`
- Differences versus idle: no Heart Rate Measurement packet observed
- Interpretation: after Da Fit pairing, the PC connected and subscribed successfully, but the standard Heart Rate Measurement characteristic still emitted no packet during the 90-second window
- Confidence: `MEDIUM` for “no HR packet in this session”; `UNKNOWN` for whether the watch requires a Da Fit-owned command or another UI state
