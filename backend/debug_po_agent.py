import urllib.request
import json
import time

# Use the same port as the running backend (assuming localhost:8000)
url = "http://localhost:8000/api/v1/chat/stream"

# Scenario 1: PO Submission that triggers a block
# Vendor V12345 is on the restricted list (mock data)
payload = {
    "message": "Submit PO for IT Services worth $120k from Vendor V12345.",
    "agent_type": "po_preapproval"
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

print(f"--- Starting PO Agent Verification ---")
print(f"Target URL: {url}")
print(f"Payload: {payload}")

try:
    print(f"\nConnecting...")
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}")
        
        print("\n--- Event Stream ---")
        for line in response:
            if line:
                decoded = line.decode('utf-8')
                # Try to parse as JSON for pretty printing
                try:
                    data = json.loads(decoded)
                    event_type = data.get("type")
                    
                    if event_type == "plan":
                        print(f"\n[PLAN] Initial Plan: {len(data.get('steps', []))} steps")
                        for step in data.get("steps", []):
                            print(f"  - {step['id']}: {step['description']}")
                            
                    elif event_type == "status":
                        print(f"[STATUS] Step '{data.get('step_id')}': {data.get('status')} - {data.get('details')}")
                        
                    elif event_type == "message":
                        content = data.get('content')
                        site_content = content if content else ""
                        print(f"[MESSAGE] {site_content}", end="", flush=True)
                        if data.get("is_final"):
                            print("\n[END]")
                            
                    elif event_type == "error":
                        print(f"[ERROR] {data.get('error')}")
                        
                    else:
                        print(f"[RAW] {decoded}")
                        
                except json.JSONDecodeError:
                    print(f"[RAW] {decoded}")
                    
except Exception as e:
    print(f"\n[EXCEPTION] {e}")

print("\n--- Verification Complete ---")
