"""Event bus: every match event goes through here. In memory by default; Azure Event Hubs when configured.

The Event Hubs path is UNVERIFIED against a live namespace (written from the azure-eventhub API, not yet run). Fabric
Eventstream then reads the hub (see docs/ARCHITECTURE.md); locally, `activator.py` plays the Activator role on the same events.
"""
import json
import os
import sys
import time
from collections import deque

LOG: deque = deque(maxlen=500)  # recent events, newest last, for the UI and tests
_producer = None


def publish(kind: str, match: str, payload: dict) -> dict:
    event = {"kind": kind, "match": match, "ts": round(time.time(), 3), "payload": payload}
    LOG.append(event)
    ns, hub = os.environ.get("EVENTHUB_NAMESPACE"), os.environ.get("EVENTHUB_NAME")
    if ns and hub:
        try:
            _send(ns, hub, event)
        except Exception as e:  # the match must never stop because the cloud is unreachable
            print(f"event hub send failed ({e}), kept in memory only", file=sys.stderr)
    return event


def _send(ns: str, hub: str, event: dict) -> None:
    global _producer
    from azure.eventhub import EventData, EventHubProducerClient
    from azure.identity import DefaultAzureCredential

    _producer = _producer or EventHubProducerClient(fully_qualified_namespace=ns, eventhub_name=hub, credential=DefaultAzureCredential())
    batch = _producer.create_batch()
    batch.add(EventData(json.dumps(event)))
    _producer.send_batch(batch)
