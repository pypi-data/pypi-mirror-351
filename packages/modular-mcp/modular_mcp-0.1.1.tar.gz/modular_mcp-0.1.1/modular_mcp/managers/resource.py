from mcp.server.fastmcp.resources import (
    Resource,
    ResourceManager,
    ResourceTemplate,
)


class BundleResourceManager(ResourceManager):
    def get_all_resources(
        self,
    ) -> tuple[dict[str, Resource], dict[str, ResourceTemplate]]:
        return self._resources, self._templates
