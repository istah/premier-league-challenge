import asyncio
import json
import sys
from dataclasses import asdict

from dotenv import load_dotenv

from . import demo
from .events import generate_match

load_dotenv()
cmd = sys.argv[1] if len(sys.argv) > 1 else "demo"
if cmd == "dataset":  # uv run python -m plc dataset [seed]
    from pathlib import Path

    from .dataset import build

    print(build(Path("data/bronze"), int(sys.argv[2]) if len(sys.argv) > 2 else 0))
elif cmd == "bench":  # uv run python -m plc bench
    from .bench import run

    print(json.dumps(run(), indent=2))
elif cmd == "replay":  # uv run python -m plc replay [seeds=50]: none vs accept-all-AI vs scripted coach
    from .replay import report

    print(report(list(range(int(sys.argv[2]) if len(sys.argv) > 2 else 50))))
elif cmd == "demo":  # uv run python -m plc demo ["dictated coach command"]
    demo.run(dictation=sys.argv[2] if len(sys.argv) > 2 else None)
else:  # uv run python -m plc explain [fan|analyst]: needs Foundry env vars
    from .agents import build_workflow

    events = json.dumps([asdict(e) for e in generate_match()])
    print(asyncio.run(build_workflow(cmd).run(events)))
