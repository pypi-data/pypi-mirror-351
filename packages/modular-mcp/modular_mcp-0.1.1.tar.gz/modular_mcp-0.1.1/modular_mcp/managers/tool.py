from mcp.server.fastmcp.tools import Tool, ToolManager


class BundleToolManager(ToolManager):
    def get_all_tools(self) -> dict[str, Tool]:
        return self._tools
