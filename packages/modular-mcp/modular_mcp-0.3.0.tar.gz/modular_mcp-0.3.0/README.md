# Modular MCP (Model Context Protocol Companion)

**Modular MCP** is a standalone Python package designed to extend and organize MCP servers in a clean and scalable way. It is **not a fork**, but a **modular companion** to the [Model Context Protocol SDK](https://github.com/modelcontextprotocol/python-sdk), developed and maintained by **Damyan Dimitrov** ([GitHub](https://github.com/DamyanBG)).

---

## ✨ Purpose

The purpose of this package is to enable **modular development of MCP servers** by introducing a `Bundle` system, similar in spirit to FastAPI's `APIRouter`. It provides:

- Clean separation of tools, resources, and prompts  
- Easy composition of multiple components  
- Scalable, maintainable codebases for MCP servers  

This package works **independently**, but when used together with the `mcp` SDK, it unlocks powerful features like `ModularFastMCP`.

---

## 📦 Installation

To install `modular-mcp`:

```bash
uv add modular-mcp
```

To use it with the official `mcp` SDK (as an optional dependency):

```bash
uv add "modular-mcp[mcp]"
```

---

## 🛠 Usage

Example of running a server using `uv`:

```bash
uv venv
uv add -e .[mcp]
uv run mcp
```

You can define and include multiple bundles to organize your project by domain or feature set.

---

## 📚 Learn More

For background on the MCP SDK and ecosystem:

👉 [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

## 📝 License

MIT License — same as the original MCP SDK.