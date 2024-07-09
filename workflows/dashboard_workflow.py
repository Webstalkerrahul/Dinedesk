from temporalio import workflow
import asyncio
from datetime import timedelta
from services import dashboard_activity

@workflow.defn
class Dashboard:
    @workflow.run
    async def run(self, work_id):
        result = await workflow.execute_activity(
            dashboard_activity.fetch_news,
            args=[work_id],
            start_to_close_timeout=timedelta(seconds=300),  # Use timedelta for timeout
        )
        # print(result)
        return result
