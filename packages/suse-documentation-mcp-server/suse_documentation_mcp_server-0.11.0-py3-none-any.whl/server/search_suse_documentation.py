import requests
import re
import os
from dotenv import load_dotenv
from typing import Any
from mcp.server.fastmcp import FastMCP

load_dotenv()

base_url = os.getenv("OI_API_BASE", "") + "/api/v1/retrieval/process/web"
authorization_token = os.getenv("OI_API_TOKEN", "")

# Initialize FastMCP server
mcp = FastMCP("suse-documentation")

def clean_content(content):
    # Remove excessive blank lines
    cleaned_content = re.sub(r'\n\s*\n+', '\n\n', content.strip())
    # Replace multiple spaces with a single space
    cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)
    return cleaned_content

def get_web_search_results_from_oi(query):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {authorization_token}'
    }

    # Step 1: Get web search results (list of URLs)
    search_payload = {
        "query": query,
        "collection_name": "your_collection_name"
    }

    print("Inside get_web_search_results_from_oi:", query)
    search_response = requests.post(f"{base_url}/search", headers=headers, json=search_payload)
    if search_response.status_code != 200:
        raise Exception(f"Search API call failed: {search_response.status_code} - {search_response.text}")

    search_data = search_response.json()

    if not search_data.get("status"):
        raise Exception(f"Search API response indicates failure: {search_data}")

    filenames = search_data.get("filenames", [])
    if not filenames:
        return "No filenames found in the search response."

    combined_response = ""

    # Step 2: Loop through URLs to get page content
    for filename in filenames:
        process_payload = {
            "url": filename,
            "collection_name": search_data["collection_name"]
        }

        process_response = requests.post(base_url, headers=headers, json=process_payload)
        if process_response.status_code != 200:
            print(f"Failed to process URL {filename}: {process_response.status_code} - {process_response.text}")
            continue

        process_data = process_response.json()
        if not process_data.get("status"):
            print(f"Processing failed for URL {filename}: {process_data}")
            continue

        content = process_data.get("file", {}).get("data", {}).get("content", "No content available")

        # Append to get combined response
        cleaned_content = clean_content(content)
        combined_response += f"Source: {filename}\n\nContent:\n{cleaned_content}\n\n"

    return combined_response
    
@mcp.tool()
async def get_web_search_results(input_data: Any) -> str:
    """
    Search SUSE documentation using web search and return results.
    
    This function is designed to perform a web search on the SUSE documentation 
    for a given query and return the results. The function takes a search query as
    a string, JSON object, or dictionary, normalizes it, performs the web search, 
    and returns a formatted string containing the content from the search results.
    
    Args:
        input_data (Any): Web search query, either as a string, JSON object, or dictionary.
        Examples: 
            - "sriov in rke2"
            - {"query": "how to configure suse manager"}
            - {"queries": "latest rancher version"}
    
    Returns:
        str: Combined content from the search results, cleaned and formatted
    """
    try:
        # Normalize input to extract the query string
        if isinstance(input_data, str):
            query = input_data
        elif isinstance(input_data, dict):
            query = input_data.get("query") or input_data.get("queries")
            if not query:
                raise ValueError("Input dictionary must contain 'query' or 'queries' key.")
        else:
            raise TypeError("Input must be a string or a dictionary containing 'query' or 'queries'.")

        # Ensure query is a string
        if not isinstance(query, str):
            raise ValueError("The extracted query must be a string.")
        print("Before web search:", query)
        return get_web_search_results_from_oi(query)
    except Exception as e:
        return f"Error performing web search: {str(e)}\n\n{query}"
    

def main():
    """Main entry point for the script."""
    # Initialize and run the server
    mcp.run(transport='stdio')
    
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
        