import os
from glob import glob
from pathlib import Path
from typing import List, Tuple  # Added Tuple

import llm

# Import all the required libzim modules
from libzim.reader import Archive
from libzim.search import (
    Query,
    Searcher,
)  # SearchResultSet not directly used in final code but good for context
from strip_tags import strip_tags


def find_zim_files(root_dir: str = ".") -> List[str]:
    """Finds ZIM archive files in a specified directory.

    Args:
        root_dir (str): Directory to search. Default is current directory (".").

    Returns:
        List[str]: A list of paths to .zim files found.
                   Example: ["./wikipedia_en_all_nopic_2023-10.zim", "./wiktionary_en_2024-01.zim"]
    """
    zim_files = list(glob(f"{root_dir}/*.zim"))
    kiwix_home_env = os.environ.get("KIWIX_HOME")
    if kiwix_home_env:
        zim_files += list(glob(f"{kiwix_home_env}/*.zim"))
    return zim_files


ZIM_FILES = find_zim_files()
ZIM_FILES_DOC_PREFIX = f"Available ZIM files for 'zim_file_path' argument: {', '.join(ZIM_FILES) if ZIM_FILES else 'None found in default directory.'}\n\n"


def kiwix_read(zim_file_path: str, article_path: str) -> str:
    """Reads and returns plain text content of an article from a ZIM archive.

    Args:
        zim_file_path (str): Path to the .zim archive file.
                             Example: "./wikipedia_en_all_nopic_2023-10.zim"
        article_path (str): Path to the article within the ZIM file.
                            This is typically obtained from search results.
                            Example: "A/Albert_Einstein.html" or "Wiktionary"

    Returns:
        str: Plain text content of the article. HTML tags are stripped,
             and text is minified with blank lines removed.
             If an error occurs, a descriptive error message string is returned.
    """
    try:
        zim = Archive(Path(zim_file_path))
        entry = zim.get_entry_by_path(article_path)
        html_content = bytes(entry.get_item().content).decode("UTF-8")
        plain_text = strip_tags(html_content, minify=True, remove_blank_lines=True)
        return plain_text.strip()
    except RuntimeError as e:  # More specific ZIM errors
        return f"Error reading article '{article_path}' from ZIM file ('{zim_file_path}'): {e}"
    except FileNotFoundError:  # Should not happen if zim_file_path is validated before or by Archive constructor
        return f"Error: ZIM file not found at '{zim_file_path}' when trying to read article '{article_path}'."
    except Exception as e:  # Catch-all for other unexpected issues
        return f"An unexpected error occurred while reading article '{article_path}' from ZIM file ('{zim_file_path}'): {e}"


def kiwix_search(zim_file_path: str, search_string: str) -> Tuple[int, List[str]]:
    """Performs a full-text search within a ZIM file, returning metadata and paths.

    Args:
        zim_file_path (str): Path to the .zim archive file.
                             Example: "./wikipedia_en_all_nopic_2023-10.zim"
        search_string (str): Text to search for.
                             Example: "theory of relativity"

    Returns:
        Tuple[int, List[str]]: A tuple containing:
            - int: Estimated total number of matches for the search_string.
            - List[str]: A list of up to 3 article paths (IDs/URLs) that match the query.
                         Example: ["A/Theory_of_relativity.html", "A/General_relativity.html"]
                         Returns (0, []) if no matches are found or if an error occurs
                         (e.g., ZIM file not found, search error).
    """
    try:
        zim = Archive(Path(zim_file_path))
        query = Query().set_query(search_string)
        searcher = Searcher(zim)
        search = searcher.search(query)
        search_count = search.getEstimatedMatches()

        article_paths: List[str] = []
        if search_count == 0:
            return 0, []

        # Limit the number of paths returned to keep the list manageable
        results_limit = min(search_count, 3)  # Kept at 3 as per original function logic
        search_results_objects = list(search.getResults(0, results_limit))

        # Extract the paths from the Result objects
        article_paths = [result for result in search_results_objects]

        return search_count, article_paths

    except FileNotFoundError:
        # Considered an error condition leading to no results.
        # print(f"Debug: ZIM file not found at '{zim_file_path}' during search.")
        return 0, []
    except Exception as e:
        # General error during search, also leads to no results.
        # print(f"Debug: An unexpected error occurred during full text search in '{zim_file_path}': {e}")
        return 0, []


def kiwix_search_and_collect(zim_file_path: str, search_string: str) -> str:
    """Searches a ZIM file and returns content of matching articles.

    This tool performs a full-text search for `search_string` within the specified `zim_file_path`.
    It then retrieves and returns the plain text content for up to the first 3 matching articles.

    Args:
        zim_file_path (str): Path to the .zim archive file.
                             Example: "./wikipedia_en_all_nopic_2023-10.zim"
        search_string (str): Text to search for within the ZIM file's content.
                             Example: "history of generative models"

    Returns:
        str: A string summarizing the search and containing the content.
             Format:
             "There are an estimated X matches for 'search_string'. Showing content for up to Y articles:

             ## article: path/to/article1.html
             Content of article 1...

             ## article: path/to/article2.html
             Content of article 2..."
             If the ZIM file is not found, or no matches are found for the search_string,
             it returns: "No results found for 'search_string' in 'zim_file_path'."
             If other unexpected errors occur, it returns a generic error message.
    """
    try:
        search_count, result_paths = kiwix_search(zim_file_path, search_string)

        if not result_paths:  # This implies search_count could be 0 or paths list is empty due to errors/no match
            return f"No results found for '{search_string}' in '{zim_file_path}'."

        output_parts = [
            f"There are an estimated {search_count} matches for '{search_string}'. "
            f"Showing content for up to {len(result_paths)} articles:\n"
        ]

        for result_path in result_paths:
            output_parts.append(f"\n## article: {result_path}")
            content = kiwix_read(zim_file_path, result_path)
            # kiwix_read returns error messages as strings if reading fails for an article
            output_parts.append(content.strip() + "\n")

        return "\n".join(output_parts).strip()

    except Exception as e:
        # This catch-all is for truly unexpected errors in this function's logic,
        # as kiwix_search and kiwix_read are designed to return error states/messages.
        return (
            f"An unexpected error occurred while searching and collecting content: {e}"
        )


@llm.hookimpl
def register_tools(register):
    # Prepend the list of available ZIM files to the tool's description for the LLM's context.

    # For kiwix_search_and_collect
    if kiwix_search_and_collect.__doc__:
        kiwix_search_and_collect.__doc__ = (
            ZIM_FILES_DOC_PREFIX + kiwix_search_and_collect.__doc__
        )
    register(kiwix_search_and_collect, "kiwix_search_and_collect")

    # For kiwix_search
    if kiwix_search.__doc__:
        kiwix_search.__doc__ = ZIM_FILES_DOC_PREFIX + kiwix_search.__doc__
    register(kiwix_search, "kiwix_search")

    # For kiwix_read
    if kiwix_read.__doc__:
        kiwix_read.__doc__ = ZIM_FILES_DOC_PREFIX + kiwix_read.__doc__
    register(kiwix_read, "kiwix_read")
