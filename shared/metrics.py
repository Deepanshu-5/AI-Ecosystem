import json
from pathlib import Path
from datetime import datetime

METRICS_FILE = Path(
    "data/metrics.json"
)

def record_metric(
    name,
    value
):
    METRICS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = []

    if METRICS_FILE.exists():
        with open(
            METRICS_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

    data.append(
        {
            "timestamp": datetime.now().isoformat(),
            "metric": name,
            "value": value
        }
    )

    with open(
        METRICS_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            indent=2
        )