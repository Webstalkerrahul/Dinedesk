# import aiohttp
# from temporalio import activity

# @activity.defn
# async def fetch_news(work_id):
#     url = ('https://newsapi.org/v2/top-headlines?'
#            'country=us&'
#            'apiKey=65c0825495bd47498fc5f20264951c22')

#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             if response.status == 200:
#                 data = await response.json()
#                 return data
#             else:
#                 return {"error": "no data"}
