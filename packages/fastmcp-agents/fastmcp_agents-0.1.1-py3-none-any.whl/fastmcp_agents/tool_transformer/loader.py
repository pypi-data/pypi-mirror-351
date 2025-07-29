from pathlib import Path

import yaml
from fastmcp.server.server import FastMCP
from fastmcp.tools.tool import Tool as FastMCPTool
from pydantic import BaseModel, Field

from fastmcp_agents.tool_transformer.tool_transformer import transform_tool
from fastmcp_agents.tool_transformer.types import ToolParameterOverride


class ToolOverride(BaseModel):
    """A set of overrides for a tool."""

    name: str | None = None
    description: str | None = None
    parameter_overrides: dict[str, ToolParameterOverride] = Field(default_factory=dict)


class ToolOverrides(BaseModel):
    """A set of overrides for a tool."""

    tools: dict[str, ToolOverride] = Field(default_factory=dict)

    @classmethod
    def from_yaml(cls, string: str) -> "ToolOverrides":
        as_dict = yaml.safe_load(string)
        return cls.model_validate(as_dict)

    @classmethod
    def from_yaml_file(cls, path: Path) -> "ToolOverrides":
        with path.open("r") as f:
            return cls.model_validate(**yaml.safe_load(f))


async def transform_tools_from_server(
    source_server: FastMCP,
    target_server: FastMCP,
    *,
    overrides: ToolOverrides,
) -> list[FastMCPTool]:
    transformed_tools: list[FastMCPTool] = []

    for tool_name, tool in (await source_server.get_tools()).items():
        tool_override = overrides.tools.get(tool_name)

        transformed_tool = (
            transform_tool(
                tool,
                target_server,
                name=tool_override.name,
                description=tool_override.description,
                parameter_overrides=tool_override.parameter_overrides,
            )
            if tool_override
            else transform_tool(
                tool,
                target_server,
            )
        )

        transformed_tools.append(transformed_tool)

    return transformed_tools
