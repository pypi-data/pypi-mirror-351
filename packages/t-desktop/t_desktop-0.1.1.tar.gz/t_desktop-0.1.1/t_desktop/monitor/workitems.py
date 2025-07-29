from RPA.Robocorp.WorkItems import WorkItems
import os

LOCAL_RUN = os.environ.get("RC_PROCESS_RUN_ID") is None

if not LOCAL_RUN:
    work_items = WorkItems()
    work_items.get_input_work_item()
    work_item = work_items.get_work_item_variables()
    fabric_variables = work_item.get("variables", dict())
    metadata = work_item.get("metadata", {})
    run_number = metadata.get("processRunUrl", "").split("/")[-1]

    rc_run_link = (
        f"https://cloud.robocorp.com/organizations/{os.environ.get('RC_ORGANIZATION_ID', '')}"
        f"/workspaces/{os.environ.get('RC_WORKSPACE_ID')}/processes"
        f"/{os.environ.get('RC_PROCESS_ID')}/runs/{os.environ.get('RC_PROCESS_RUN_ID', '')}/"
        f"stepRuns/{os.environ.get('RC_ACTIVITY_RUN_ID')}/"
    )
    empower_url = metadata.get("processRunUrl", "") or fabric_variables.get("processRunUrl", "")
    empower_url_text = metadata.get("processRunId", "Empower")
    if empower_url_text != "Empower":
        current_env = "DEV" if "dev" in empower_url else "PROD"
    else:
        current_env = "PROD" if fabric_variables.get("environment", "") == "production" else "DEV"
else:
    rc_run_link = "https://cloud.robocorp.com"
    empower_url = "https://app.thoughtful-dev.ai"
    empower_url_text = "Empower"
    current_env = "DEV"
    run_number = "0000"
OUTPUT_FOLDER = os.path.join(os.getcwd(), "output")
