import requests
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from uainepydat import datatransform

haupt_url = "https://www.data.gov.au/api/"

def build_action_url(action_name):
    return f"{haupt_url}/action/{action_name}"

def try_request(url, max_limit = 10):
    for attempt in range(max_limit):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            pass  # Optionally log the exception
        if attempt == 0 and max_limit > 1:
            # If the first attempt fails and more attempts are allowed, show tqdm for the rest
            for attempt in tqdm(range(1, max_limit), desc="Trying requests", unit="attempt"):
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        return response.json()
                except Exception as e:
                    pass
            break
    print(f"Failed to fetch organization list after {max_limit} attempts.")
    return None

#https://www.data.gov.au/api/action/organization_list
def get_organization_list():
    url = build_action_url("organization_list")
    return try_request(url)

#https://www.data.gov.au/api/action/current_package_list_with_resources?limit=100&offset=0
def get_package_list(chunk_size = 50, max_workers=2):
    baseurl = build_action_url("current_package_list_with_resources")
    return read_all_chunks(baseurl, chunk_size=chunk_size, max_workers=max_workers)

#define a chunk read method
def read_chunk(baseurl, chunk_size = 50, chunk_number = 0):
    offset = chunk_number * chunk_size #0 to begin with
    sub_query = f"{baseurl}?limit={chunk_size}&offset={offset}"
    return try_request(sub_query)

def chunks_to_dataframes(json_chunks):
    """
    Converts a list of JSON chunks to a list of DataFrames.
    """
    return [datatransform.json_to_dataframe(chunk) for chunk in json_chunks]

def read_all_chunks(baseurl, chunk_size=50, max_workers=2):
    chunk_number = 0
    hard_limit = 20000
    all_results = []
    if not max_workers or max_workers == 1:
        # Sequential version
        with tqdm(desc="Reading chunks", unit="") as pbar:
            while chunk_number < hard_limit:
                chunk = read_chunk(baseurl, chunk_size, chunk_number)
                if not chunk or not chunk.get('result'):
                    break
                all_results.append(chunk['result'])  # Append each chunk's result as a separate list
                chunk_number += 1
                pbar.update(1)
        return all_results
    # Parallel version
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        with tqdm(desc="Reading chunks", unit="") as pbar:
            futures = {}
            # Submit the first batch of futures
            for i in range(max_workers):
                futures[executor.submit(read_chunk, baseurl, chunk_size, chunk_number)] = chunk_number
                chunk_number += 1
            while futures:
                for future in as_completed(list(futures)):
                    current_chunk_number = futures[future]
                    try:
                        chunk = future.result()
                    except Exception:
                        chunk = None
                    pbar.update(1)
                    if not chunk or not chunk.get('result'):
                        # Stop submitting new futures if no more results
                        futures.pop(future)
                        continue
                    all_results.append(chunk['result'])  # Append each chunk's result as a separate list
                    # Submit the next chunk if we haven't hit the hard limit
                    if chunk_number < hard_limit:
                        futures[executor.submit(read_chunk, baseurl, chunk_size, chunk_number)] = chunk_number
                        chunk_number += 1
                    futures.pop(future)
    return all_results

def remove_api_header(json_string):
    """
    Takes a JSON string, dict, or list from the API and returns only the 'result' field if present.
    If input is already a list, returns it as-is.
    """
    if isinstance(json_string, str):
        data = json.loads(json_string)
    else:
        data = json_string
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get('result', None)
    return None
