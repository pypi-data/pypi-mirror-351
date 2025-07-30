from mcp.server.fastmcp.prompts import Prompt, PromptManager


class BundlePromptManager(PromptManager):
    def get_all_prompts(self) -> dict[str, Prompt]:
        return self._prompts
