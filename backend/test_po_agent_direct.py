import asyncio
import sys
import os

# Add backend to path so imports work
sys.path.append(os.getcwd())

# Mock settings before importing agent
from agent_demo_framework.core import config
# config.settings.OPENAI_API_KEY = "sk-..." # Assuming env var is set or handled

from agent_demo_framework.agents.po_preapproval_agent import POPreApprovalAgent
from agent_demo_framework.schemas.stream import PlanEvent, StatusEvent, MessageEvent

async def run_test():
    print("--- Initializing POPreApprovalAgent ---")
    try:
        agent = POPreApprovalAgent()
    except Exception as e:
        print(f"Failed to init agent: {e}")
        return

    print("--- Sending Message ---")
    message = "Submit PO for IT Services worth $120k from Vendor V12345."
    history = []
    
    print(f"User: {message}\n")

    print("--- Stream Output ---")
    try:
        async for event in agent.astream_events(message, history):
            if isinstance(event, PlanEvent):
                print(f"[PLAN] {len(event.steps)} steps")
                for s in event.steps:
                    print(f"  - {s.id}")
            elif isinstance(event, StatusEvent):
                print(f"[STATUS] {event.step_id}: {event.status} ({event.details})")
            elif isinstance(event, MessageEvent):
                print(f"[MSG] {event.content}", end="", flush=True)
                if event.is_final:
                    print("\n[END]")
            else:
                print(f"[UNKNOWN] {event}")
    except Exception as e:
        print(f"\n[EXCEPTION] {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
