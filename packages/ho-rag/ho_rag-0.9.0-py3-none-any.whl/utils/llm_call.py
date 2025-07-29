import os
import httpx
from typing import Any
import json
from motor.motor_asyncio import AsyncIOMotorClient

mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URI"))

def create_req_body (patient_name:str, query:str) -> Any:
    return json.dumps({
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": os.getenv("AI_SEARCH_ENDPOINT"),
                    "index_name": f"index-{patient_name.replace(" ", "").lower()}",
                    "semantic_configuration": "default",
                    "query_type": "semantic",
                    "fields_mapping": {},
                    "in_scope": True,
                    "filter": None,
                    "strictness": 3,
                    "top_n_documents": 5,
                    "authentication": {
                        "type": "api_key",
                        "key": os.getenv("AI_SEARCH_KEY")
                    },
                    "key": os.getenv("AI_SEARCH_KEY")
                }
            }
        ],
        "messages": [
            {
                "role":"system",
                "content":"You are an exceptional medical assistant. Your job is to analyse the queries asked by the doctor and respond!"
            },
            {
                "role":"user",
                "content":query
            }
        ], 
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 12000,
        "stop": None,
        "stream": False,
        "frequency_penalty": 0,
        "presence_penalty": 0
    })

async def make_llm_request(patient_name: str, query: str) -> str:
    """
        This function makes a call to Open AI to receive resolution for a query raised by a user
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(f"{os.getenv('GPT_ENDPOINT')}&api-key={os.getenv('GPT_KEY')}", content=create_req_body(patient_name, query))
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            raise e
        
async def get_details_mongo(start_range: int, end_range: int, units: str, query_string: str) -> Any:
    """
        This function returns all the documents from mongo db given an age range and age units (months/ years)
    """
    db = mongo_client[os.getenv("DB_NAME")]
    collection = db[os.getenv("COLLECTION")]
    pipeline = [
        {
            "$search": {
                "index": "default",
                "text": {
                    "query": query_string,
                    "path": "condition",
                    "fuzzy": {}
                }
            }
        },
        {
            "$match": {
                "age": {"$gte": start_range, "$lte": end_range},
                "unit": units
            }
        }
    ]
    cursor = collection.aggregate(pipeline)
    return await cursor.to_list(length=None)