import os
import llm
import json
from llm_tools_kiwix import kiwix_search_and_collect, kiwix_search, kiwix_read


def test_invalid_path_tool():
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps(
            {
                "tool_calls": [
                    {
                        "name": "kiwix_search_and_collect",
                        "arguments": {
                            "zim_file_path": "./test.zim",
                            "search_string": "search_string",
                        },
                    }
                ]
            }
        ),
        tools=[kiwix_search_and_collect],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    assert tool_results == [
        {
            "name": "kiwix_search_and_collect",
            "output": "No results found for 'search_string' in './test.zim'.",
            "tool_call_id": None,
        }
    ]


def test_happy_path_kiwix_search():
    os.environ["KIWIX_HOME"] = "./tests/data"
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps(
            {
                "tool_calls": [
                    {
                        "name": "kiwix_search",
                        "arguments": {
                            "zim_file_path": "./tests/data/devdocs_en_sqlite_2025-04.zim",
                            "search_string": "wall pragma",
                        },
                    }
                ]
            }
        ),
        tools=[kiwix_search_and_collect, kiwix_search, kiwix_read],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    assert tool_results == [
        {
            "name": "kiwix_search",
            "output": '[4, ["faq", "testing", "changes"]]',
            "tool_call_id": None,
        }
    ]


def test_happy_path_kiwix_read():
    os.environ["KIWIX_HOME"] = "./tests/data"
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps(
            {
                "tool_calls": [
                    {
                        "name": "kiwix_read",
                        "arguments": {
                            "zim_file_path": "./tests/data/devdocs_en_sqlite_2025-04.zim",
                            "article_path": "faq",
                        },
                    }
                ]
            }
        ),
        tools=[kiwix_search_and_collect, kiwix_search, kiwix_read],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"][0]
    assert tool_results["name"] == "kiwix_read"
    assert tool_results["output"].startswith(
        "SQLite Frequently Asked Questions Frequently Asked Que"
    )


def test_happy_path_kiwix_search_and_collect():
    os.environ["KIWIX_HOME"] = "./tests/data"
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps(
            {
                "tool_calls": [
                    {
                        "name": "kiwix_search_and_collect",
                        "arguments": {
                            "zim_file_path": "./tests/data/devdocs_en_sqlite_2025-04.zim",
                            "search_string": "wall pragma",
                        },
                    }
                ]
            }
        ),
        tools=[kiwix_search_and_collect, kiwix_search, kiwix_read],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"][0]
    assert tool_results["name"] == "kiwix_search_and_collect"
    assert tool_results["output"].startswith(
        "There are an estimated 4 matches for 'wall pragma'. Showing content for up to 3 articles:\n\n\n## article: faq\nSQLite Frequently Asked Questions "
    )
