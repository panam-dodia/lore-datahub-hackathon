"""In-memory state shared between routes.py and websocket.py.

Fine for hackathon scale (single process, no persistence needed) — see
section 9 of the spec. A real deployment would move this to Redis/DB and
use a pub/sub layer for progress streaming instead of per-job asyncio.Queues.

Note: written-back knowledge is NOT tracked here — /api/knowledge reads it
straight from DataHub's custom properties instead, since that's durable
across backend restarts and reflects writes from anywhere, not just jobs
this process happened to run.
"""

import asyncio

from models.schemas import ExcavationJob

jobs: dict[str, ExcavationJob] = {}
job_queues: dict[str, asyncio.Queue] = {}
