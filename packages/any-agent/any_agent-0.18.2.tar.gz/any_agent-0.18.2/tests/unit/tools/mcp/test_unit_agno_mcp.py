from collections.abc import Generator, Sequence
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agno.tools.mcp import MCPTools as AgnoMCPTools

from any_agent.config import AgentFramework, MCPParams, MCPSse, MCPStdio, Tool
from any_agent.tools import _get_mcp_server


@pytest.fixture
def agno_mcp_tools() -> Generator[AgnoMCPTools]:
    with patch("any_agent.tools.mcp.frameworks.agno.AgnoMCPTools") as mock_mcp_tools:
        yield mock_mcp_tools


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    "enter_context_with_transport_and_session",
)
async def test_agno_mcp_sse_integration(
    mcp_sse_params_with_tools: MCPSse,
    session: Any,
    tools: Sequence[Tool],
    agno_mcp_tools: AgnoMCPTools,
) -> None:
    mcp_server = _get_mcp_server(mcp_sse_params_with_tools, AgentFramework.AGNO)

    await mcp_server._setup_tools()

    session.initialize.assert_called_once()

    agno_mcp_tools.assert_called_once_with(session=session, include_tools=tools)  # type: ignore[attr-defined]


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    "enter_context_with_transport_and_session",
)
async def test_agno_mcp_no_tools(
    mcp_params_no_tools: MCPParams,
    agno_mcp_tools: AgnoMCPTools,
) -> None:
    """Regression test:"""
    mcp_server = _get_mcp_server(mcp_params_no_tools, AgentFramework.AGNO)

    await mcp_server._setup_tools()

    assert agno_mcp_tools.call_args_list[0].kwargs["include_tools"] is None  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_agno_mcp_env() -> None:
    mcp_server = _get_mcp_server(
        MCPStdio(command="print('Hello MCP')", args=[], env={"FOO": "BAR"}),
        AgentFramework.AGNO,
    )
    mocked_class = MagicMock()
    mocked_cm = AsyncMock()
    mocked_cm.__aenter__.return_value = "foo"
    mocked_class.return_value = mocked_cm

    with patch("any_agent.tools.mcp.frameworks.agno.AgnoMCPTools", mocked_class):
        await mcp_server._setup_tools()
        assert mocked_class.call_args_list[0][1]["env"] == {"FOO": "BAR"}
