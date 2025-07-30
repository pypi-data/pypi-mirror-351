from mcp.server.fastmcp.prompts import PromptManager, Prompt


class BundlePromptManager(PromptManager):
    def get_all_prompts(self) -> dict[str, Prompt]:
        return self._prompts
