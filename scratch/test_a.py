import requests
import time
import sys

def run_test():
    print("Starting Test A: Normal Workflow...")
    response = requests.post("http://127.0.0.1:8000/api/workflows", json={
        "objective": "Process the overdue invoices for Acme Corp."
    })
    
    if response.status_code != 200:
        print(f"Failed to start workflow: {response.text}")
        sys.exit(1)
        
    data = response.json()
    workflow_id = data.get("id")
    print(f"Started Workflow ID: {workflow_id}")
    
    events_url = f"http://127.0.0.1:8000/api/workflows/{workflow_id}/events"
    
    max_retries = 30
    seen_events = set()
    
    for i in range(max_retries):
        resp = requests.get(events_url)
        if resp.status_code == 200:
            events = resp.json()
            for event in events:
                event_id = event.get("id")
                if event_id not in seen_events:
                    seen_events.add(event_id)
                    print(f"[{event.get('timestamp')}] {event.get('event_type')}: {event.get('details')}")
        else:
            print(f"Failed to get events: {resp.text}")
            
        # check if workflow completed or failed based on events
        status_resp = requests.get(f"http://127.0.0.1:8000/api/workflows/{workflow_id}")
        if status_resp.status_code == 200:
            status = status_resp.json().get("status")
            if status in ["completed", "failed", "COMPLETED", "FAILED"]:
                print(f"Workflow finished with status: {status}")
                break
        
        time.sleep(2)
    else:
        print("Test timed out waiting for workflow to finish.")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
