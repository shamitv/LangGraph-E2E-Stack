"""Command-line runner for the HealthcareAgent."""
from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Any

from agent_demo_framework.agents.healthcare_agent import HealthcareAgent
from agent_demo_framework.schemas.stream import PlanEvent, StatusEvent, MessageEvent, ErrorEvent


def _event_type(event: Any) -> str | None:
    if hasattr(event, "type"):
        return getattr(event, "type")
    if isinstance(event, dict):
        return event.get("type")
    return None


async def _run_streaming(message: str) -> int:
    agent = HealthcareAgent()
    history = []

    try:
        async for event in agent.astream_events(message, history):
            event_type = _event_type(event)

            if isinstance(event, PlanEvent) or event_type == "plan":
                steps = event.steps if isinstance(event, PlanEvent) else event.get("steps", [])
                print("\nExecution Plan:")
                for step in steps:
                    if isinstance(step, dict):
                        print(f"- {step.get('description')} [{step.get('status')}]")
                    else:
                        print(f"- {step.description} [{step.status}]")

            elif isinstance(event, StatusEvent) or event_type == "status":
                step_id = event.step_id if isinstance(event, StatusEvent) else event.get("step_id")
                status = event.status if isinstance(event, StatusEvent) else event.get("status")
                details = event.details if isinstance(event, StatusEvent) else event.get("details")
                details_msg = f" - {details}" if details else ""
                print(f"[{step_id}] {status}{details_msg}")

            elif isinstance(event, MessageEvent) or event_type == "message":
                content = event.content if isinstance(event, MessageEvent) else event.get("content", "")
                is_final = event.is_final if isinstance(event, MessageEvent) else event.get("is_final", False)
                if content:
                    print(content, end="", flush=True)
                if is_final:
                    print()

            elif isinstance(event, ErrorEvent) or event_type == "error":
                err_msg = event.error if isinstance(event, ErrorEvent) else event.get("error")
                print(f"Error: {err_msg}", file=sys.stderr)
                return 1

    except Exception as exc:  # pragma: no cover - top-level safeguard
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


async def _run_once(message: str) -> int:
    agent = HealthcareAgent()
    try:
        result = await agent.process(message, history=[])
        print(result.get("content", ""))
    except Exception as exc:  # pragma: no cover - top-level safeguard
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run HealthcareAgent from the command line.")
    parser.add_argument(
        "--message",
        "-m",
        default="I am patient PT-1001. I have been having bad back pain and need an MRI.",
        help="User message to send to the HealthcareAgent.",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming and return a single response.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.no_stream:
        return asyncio.run(_run_once(args.message))
    return asyncio.run(_run_streaming(args.message))


if __name__ == "__main__":
    raise SystemExit(main())
