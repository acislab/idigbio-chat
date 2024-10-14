def test_import_tools():
    from chat.tools.tool import all_tools
    tool_names = {tool.schema["name"] for tool in all_tools}

    assert "ask_an_expert" in tool_names
    assert "search_species_occurrence_records" in tool_names
