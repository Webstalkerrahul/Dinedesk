from tools import resource
from workflows import dashboard_workflow

async def start_dashboard_workflow(work_id):
    temporal_client = await resource.create_client_connection()
    await temporal_client.start_workflow(
        dashboard_workflow.Dashboard.run,
        args=[work_id],
        id=work_id,
        task_queue="DashboardTaskQueue"  # Ensure this matches the worker's task queue
    )
