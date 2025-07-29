import json

from pytest_bdd import parsers, then, when

from llm_mcp.schema import ServerConfig


@when(
    "I convert the output to a server config object",
    target_fixture="server_config",
)
def server_config(cli_result) -> ServerConfig:
    return ServerConfig.model_validate_json(cli_result.stdout)


@then(parsers.parse("the server config has {tool_count:d} tools"))
def check_tool_count(server_config: ServerConfig, tool_count: int):
    assert len(server_config.tools) == tool_count


@then(parsers.parse('"{tool_name}" has an input schema of "{input_schema}"'))
def check_tool_name_input_schema(
    server_config: ServerConfig,
    tool_name: str,
    input_schema: str,
):
    tool = server_config.get_tool(tool_name)
    assert tool.inputSchema == json.loads(input_schema)


@then(
    parsers.parse('"{tool_name}" has "{field_name}" as a required parameter')
)
def check_search_llm_documentation(
    server_config: ServerConfig, tool_name: str, field_name: str
):
    tool = server_config.get_tool(tool_name)
    assert field_name in tool.inputSchema.get("required", [])
