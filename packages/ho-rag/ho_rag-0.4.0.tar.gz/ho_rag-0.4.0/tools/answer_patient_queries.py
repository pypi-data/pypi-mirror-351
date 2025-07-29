from server import mcp
import asyncio
import httpx
import random
from utils.llm_call import make_llm_request, get_details_mongo, get_decision
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

query = "Give me all the information that is available for the patient"
semaphore = asyncio.Semaphore(5)
# Retry config for 429 handling (with exponential backoff)
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.HTTPStatusError)
)

@mcp.tool()
async def answer_doctor_queries(patient_name:str, query:str) -> str:
    """
        Answers a medical query for a specific patient using a Retrieval-Augmented Generation (RAG) system powered by the OpenAI Chat Completions API.

        This function takes in the name of a patient and a natural language query related to that patient. 
        It then interacts with an OpenAI language model integrated with an indexer and data source 
        (commonly known as a Retrieval-Augmented Generation setup). The indexer retrieves relevant 
        context-specific medical data or notes about the patient, which are combined with the query to 
        generate a precise and context-aware response from the LLM.

        Parameters:
        -----------
        patient_name : str
            The name of the patient for whom the query is being made. This is used to identify and retrieve 
            relevant patient-specific information from the external data source.
        
        query : str
            A natural language question or statement about the patient. This could involve medical history, 
            treatment details, medications, lab reports, or any other patient-related information.

        Returns:
        --------
        str
            The AI-generated response to the query, informed by both the retrieved patient-specific data 
            and the language model's reasoning.

        Example:
        --------
        >>> answer_doctor_queries("John Doe", "What were the symptoms of John Doe?")
        'John Doe has back pain.'
    """
    return await make_llm_request(patient_name, query)

async def safe_get_decision(details, condition):
    async with semaphore:
        await asyncio.sleep(random.uniform(0.2, 0.5))  # small jitter
        result = await get_decision(details, condition)
        return result

@mcp.tool()
async def get_patient_analytics(start_range_age: int, end_range_age: int, units: str, condition: str):
    """
    Retrieves patient records from a MongoDB collection filtered by age range and units,
    then asynchronously processes each patient’s data to determine if they meet a specified condition.

    The function performs the following steps:
    1. Queries the MongoDB collection for patients whose age is between `start_range_age` and `end_range_age`
       and whose age unit matches `units` ("years" or "months").
    2. Converts the MongoDB cursor to a list of patient documents.
    3. For each patient document, calls a synchronous function to extract details relevant to a medical query.
    4. Calls an asynchronous decision function (`safe_get_decision`) to evaluate the condition for each patient,
       managing concurrency to avoid API rate limits.
    5. Collects and returns a list of patient names where the condition evaluation returned "Yes".

    Args:
        start_range_age (int): The minimum age (inclusive) for filtering patients.
        end_range_age (int): The maximum age (inclusive) for filtering patients.
        units (str): The age unit to filter by, typically "years" or "months".
        condition (str): The medical condition query to evaluate for each patient.

    Returns:
        list[str]: A list of patient names who meet the specified condition.
    """
    target_patients = await get_details_mongo(start_range_age, end_range_age, units)
    target_patients_cleaned = []

    async def process_patient(doc):
        details = answer_doctor_queries(doc.name, query)
        try:
            decision = await safe_get_decision(details, condition)
            if decision == "Yes":
                target_patients_cleaned.append(doc.name)
        except Exception as e:
            print(f"Failed for {doc.name}: {e}")

    await asyncio.gather(*(process_patient(doc) for doc in target_patients))

    return target_patients_cleaned
