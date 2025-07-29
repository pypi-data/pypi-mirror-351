from typing import Any, Dict, List

from serpapi import GoogleSearch

from wyn_agent_s.helper import register_function


# Register the google_search function
@register_function("google_search")
def google_search(
    payload: Dict[str, str], secrets: Dict[str, str], event_stream: list
) -> Dict[str, Any]:
    """
    Simulate a Google search using the SerpAPI and return the results formatted as a Markdown table.

    Args:
        payload (Dict[str, str]): A dictionary containing the search parameters:
                                  - query: The search query string.
                                  - location: The location for the search.
        secrets (Dict[str, str]): Contains the SerpAPI key for API authentication.
        event_stream (list): A list used to log events and responses.

    Returns:
        Dict[str, Any]: A dictionary with the status of the API call and a Markdown table of search results.
    """

    # Extract Secrets
    serpapi_key = secrets["serpapi_key"]

    # Extract search parameters from the payload
    engine = payload.get("engine", "google")
    query = payload.get("query", "")
    location = payload.get("location", "")
    num = payload.get("num", "50")
    num = int(num)
    num = num if type(num) == int else 50

    # Checkpoint
    print(f"Run google search API using: \nquery={query}, \nlocation={location}")

    try:
        # Perform the Google Search using SerpAPI
        search = GoogleSearch(
            {
                "engine": engine,
                "q": query,
                "location": location,
                "api_key": serpapi_key,
                "num": num,
            }
        )
        results = search.get_dict()

        # Extract relevant results
        organic_results = results.get("organic_results", [])

        # Convert search results to a Markdown table
        md_table = "| Title | Link | Snippet |\n| :--- | :--- | :--- |\n"
        for item in organic_results:
            title = item.get("title", "N/A")
            link = item.get("link", "#")
            snippet = item.get("snippet", "N/A")
            md_table += f"| {title} | [Link]({link}) | {snippet} |\n"
        print(f"👀 Results: \n{md_table}")

        # Prepare the response
        response = {"status": "success", "model_name": "None", "results": md_table}

        # Append the result to the event stream
        event_stream.append(
            {
                "event": "api_call",
                "api_name": "google_search",
                "response": {"text": response, "status": "200 success"},
            }
        )

    except Exception as e:
        # Handle any exceptions that occur during the API call
        response = {"status": f"error: {str(e)}", "model_name": "None"}
        event_stream.append(
            {"event": "api_call", "api_name": "google_search", "response": response}
        )

    return response
