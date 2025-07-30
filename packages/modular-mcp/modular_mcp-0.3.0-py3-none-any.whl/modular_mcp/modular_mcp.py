from mcp.server.fastmcp.server import FastMCP

from modular_mcp.bundle import Bundle


class ModularFastMCP(FastMCP):
    def include_bundle(self, bundle: Bundle) -> None:
        """Add bundle of resources, tools and prompts to the server."""
        bundle_tools = bundle.get_tools()
        for tool_name, tool in bundle_tools.items():
            self.add_tool(tool.fn, tool_name, tool.description, tool.annotations)

        bundle_resources, bundle_templates = bundle.get_resources()
        for resource in bundle_resources.values():
            self.add_resource(resource)
        for template_name, template in bundle_templates.items():
            self._resource_manager.add_template(
                template.fn,
                template.uri_template,
                template_name,
                template.description,
                template.mime_type,
            )

        bundle_prompts = bundle.get_prompts()
        for prompt in bundle_prompts.values():
            self.add_prompt(prompt)
