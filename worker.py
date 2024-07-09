import asyncio
from temporalio import worker, client

# Import your workflow and activities
from workflows import dashboard_workflow
from services import dashboard_activity

async def main():
    # Create a Temporal client
    temporal_client = await client.Client.connect("localhost:7233")

    # Create and start a worker
    worker_instance = worker.Worker(
        temporal_client,
        task_queue="DashboardTaskQueue",  # Ensure this matches the workflow's task queue
        workflows=[dashboard_workflow.Dashboard],
        activities=[dashboard_activity.fetch_news],
    )

    # Run the worker
    await worker_instance.run()

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
