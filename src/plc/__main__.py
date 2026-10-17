import asyncio
import json
import sys
from dataclasses import asdict

from dotenv import load_dotenv

from .agents import build_workflow
from .events import generate_match


async def main(audience: str):
    load_dotenv()
    events = json.dumps([asdict(e) for e in generate_match()])
    result = await build_workflow(audience).run(events)
    print(result)


asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "fan"))
