# llm-tools-kiwix

[![PyPI](https://img.shields.io/pypi/v/llm-tools-kiwix.svg)](https://pypi.org/project/llm-tools-kiwix/)
[![Changelog](https://img.shields.io/github/v/release/mozanunal/llm-tools-kiwix?include_prereleases&label=changelog)](https://github.com/mozanunal/llm-tools-kiwix/releases)
[![Tests](https://github.com/mozanunal/llm-tools-kiwix/actions/workflows/test.yml/badge.svg)](https://github.com/mozanunal/llm-tools-kiwix/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/mozanunal/llm-tools-kiwix/blob/main/LICENSE)

Expose offline Kiwix ZIM archives (like Wikipedia, Stack Exchange, DevDocs) to Large Language Models (LLMs) via the [LLM](https://llm.datasette.io/) CLI tool and Python library. This plugin allows LLMs to search and read content from your local ZIM files.

## Key Features

*   **Automatic ZIM File Discovery**: Finds `.zim` files in the current working directory and in the directory specified by the `KIWIX_HOME` environment variable.
*   **Dynamic Tool Descriptions**: Tool descriptions are automatically updated with the list of discovered ZIM files, guiding the LLM on what's available.
*   **Offline Content Access**: Enables LLMs to access information from ZIM archives without an internet connection.
*   **Multiple Tools**:
    *   `kiwix_search_and_collect`: Searches a ZIM file and returns the content of matching articles. (Most commonly used)
    *   `kiwix_search`: Performs a search and returns metadata and article paths.
    *   `kiwix_read`: Reads the content of a specific article path.

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).

```bash
llm install llm-tools-kiwix
```

## Usage

1.  **Download ZIM Files**: Obtain ZIM files from [Kiwix Downloads](https://download.kiwix.org/zim/) or other sources. For example, you might download:
    *   `wikipedia_en_all_nopic_2023-10.zim`
    *   `devdocs_en_docker_2025-04.zim`
    *   `askubuntu.com_en_all_2024-10.zim`

2.  **Place ZIM Files**: Put the downloaded `.zim` files in:
    *   The directory where you'll be running your `llm` commands or Python scripts (current working directory).
    *   The directory specified by the `KIWIX_HOME` environment variable, if set.
    The plugin will automatically detect files from these locations.

    Example (based on your provided snippet):
    ```bash
    # In your project directory
    ls *.zim
    # Expected output (if files are in current directory):
    # askubuntu.com_en_all_2024-10.zim  devdocs_en_docker_2025-04.zim  devdocs_en_scala_2025-04.zim
    ```

3.  **Discovering Tools and Available ZIMs**:
    You can see the tools provided by this plugin and which ZIM files they've detected by running:
    ```bash
    llm tools list
    ```
    This will show entries like `kiwix_search_and_collect`, and its description will include a line similar to:
    `Available ZIM files for 'zim_file_path' argument: ./askubuntu.com_en_all_2024-10.zim, ./devdocs_en_docker_2025-04.zim, ...`
    The tool's full description will also detail the format of its output.

### Command-Line Interface (CLI) Example

You can instruct an LLM to use these tools directly from the command line. For example, if you want to find information about fixing a rootless Docker installation error using your `devdocs_en_docker_2025-04.zim` file:

```bash
llm -m gpt-4o-mini --tool kiwix_search_and_collect \
  "I'm getting a permission error while trying to run Docker in rootless mode. \
  Please search and provide relevant information from the Docker devdocs." \
  --tools-debug
```

*   Replace `gpt-4o-mini` with your desired model.
*   The LLM will use the prompt to identify that it needs to call the `kiwix_search_and_collect` tool.
*   It will extract `zim_file_path: "devdocs_en_docker_2025-04.zim"` (or another relevant ZIM file from the available list) and `search_string: "docker rootless permission error"` (or similar) as arguments for the tool.
*   `--tools-debug` (optional) shows the tool calls and responses.

The LLM will then receive the search results (content from the ZIM file) and use that to formulate its answer.


## Development

To set up this plugin locally, first check out the code. Then create a new virtual environment:

```bash
cd llm-tools-kiwix
python -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
python -m pytest
```

Make sure you have some `.zim` files in the project root, or in a directory specified by `KIWIX_HOME`, or mock the ZIM interactions appropriately for tests to run against.
