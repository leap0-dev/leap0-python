# Leap0 Python SDK

Python SDK for [Leap0](https://leap0.dev), enterprise-grade cloud sandboxes for AI agents.

Launch isolated sandboxes in ~200ms. Give every agent its own compute, filesystem, and network boundary while your agents run safely.

## Installation

```bash
pip install leap0
```

Or install from source:

```bash
git clone https://github.com/leap0dev/leap0-python.git
cd leap0-python
pip install .
```

## Requirements

- Python >= 3.10
- A Leap0 API key

### Getting an API key

1. Sign up at [app.leap0.dev](https://app.leap0.dev/login).
2. Copy your API key from the dashboard.
3. Set it as an environment variable:

```bash
export LEAP0_API_KEY="your-api-key"
```

Alternatively, pass it directly when creating a client:

```python
from leap0 import Leap0Client

client = Leap0Client(api_key="your-api-key")
```

## Quick Start

```python
from leap0 import Leap0, Leap0Config

client = Leap0(Leap0Config())
sandbox = client.sandboxes.create()

try:
    result = client.code_interpreter.execute(
        sandbox,
        code="sum([10, 20, 30, 40]) / 4",
        language="python",
    )
    print(result.main_text)  # "25.0"
finally:
    client.sandboxes.delete(sandbox)
    client.close()
```

Or use the client as a context manager:

```python
from leap0 import Leap0Client

with Leap0Client(api_key="your-api-key") as client:
    sandbox = client.sandboxes.create()
    result = client.code_interpreter.execute(
        sandbox, code="print('Hello from the sandbox!')", language="python"
    )
    print(result.main_text)
    client.sandboxes.delete(sandbox)
```

## Features

### Code Interpreter

Stateful REPL sessions for Python and TypeScript. Variables persist across calls, with Matplotlib charts auto-captured as PNG and SVG.

```python
result = client.code_interpreter.execute(
    sandbox, code="x = 42", language="python"
)

# Stream output in real-time
for event in client.code_interpreter.execute_stream(
    sandbox, code="for i in range(5): print(i)", language="python"
):
    print(event.type, event.data)
```

### Filesystem

Full filesystem access inside every sandbox. List, read, write, edit, search, and more.

```python
client.filesystem.write_file_text(sandbox, path="/workspace/hello.txt", content="Hello!")
content = client.filesystem.read_file_text(sandbox, path="/workspace/hello.txt")
tree = client.filesystem.tree(sandbox, path="/workspace", max_depth=2)
matches = client.filesystem.grep(sandbox, path="/workspace", pattern="TODO")
```

### Git

Clone repos, create branches, stage files, commit, push, and pull, all inside the sandbox.

```python
client.git.clone(sandbox, url="https://github.com/user/repo.git", path="/workspace/repo")
status = client.git.status(sandbox, path="/workspace/repo")
client.git.add(sandbox, path="/workspace/repo", files=["README.md"])
client.git.commit(sandbox, path="/workspace/repo", message="Update README")
client.git.push(sandbox, path="/workspace/repo")
```

### Process Execution

Execute one-shot shell commands inside a running sandbox.

```python
result = client.process.execute(sandbox, command=["ls", "-la", "/workspace"])
print(result.stdout)
```

### Interactive Terminal (PTY)

Interactive terminal sessions over WebSocket with persistent state.

```python
session = client.pty.create(sandbox, cols=120, rows=30, cwd="/home/user")
conn = client.pty.connect(sandbox, session.id)
conn.send("ls -la\n")
print(conn.recv().decode())
conn.close()
```

### Language Server Protocol (LSP)

Start language servers for Python and TypeScript to get completions, symbols, and document lifecycle events.

```python
client.lsp.start(sandbox, language="python")
client.lsp.did_open(sandbox, uri="file:///workspace/main.py", language="python")
completions = client.lsp.completions(sandbox, uri="file:///workspace/main.py", line=10, character=5)
```

### SSH Access

Generate and manage time-bound SSH credentials for direct sandbox access.

```python
ssh = client.ssh.create_access(sandbox)
print(ssh.hostname, ssh.port, ssh.username)
```

### Desktop Automation

Control a graphical desktop inside the sandbox. Take screenshots, move the pointer, click, type, and record the screen.

```python
sandbox = client.sandboxes.create(template_name="system/desktop:v0.1.0")
client.desktop.move_pointer(sandbox, x=500, y=300)
client.desktop.click(sandbox, button=1)
screenshot = client.desktop.screenshot(sandbox, image_format="png")
```

### Snapshots

Save and restore sandbox state at any point.

```python
snapshot = client.snapshots.create(sandbox, name="my-checkpoint")
restored = client.snapshots.resume(snapshot_name="my-checkpoint")
```

### Custom Templates

Create reusable sandbox templates from any container image.

```python
template = client.templates.create(
    name="my-template",
    image="my-registry.com/my-image:latest",
)
sandbox = client.sandboxes.create(template_name="my-template")
```

### Network Controls

Fine-grained egress control per sandbox. Allow-list specific domains or IP ranges, or block all outbound traffic entirely.

```python
sandbox = client.sandboxes.create(
    network_policy="custom",
    allowed_domains=["api.example.com"],
)
```

## API Reference

The SDK is organized into service clients accessible from the top-level `Leap0Client`:

| Client | Description |
|---|---|
| `client.sandboxes` | Create, get, pause, and delete sandboxes |
| `client.snapshots` | Create, pause, resume, and delete snapshots |
| `client.templates` | Create, rename, and delete templates |
| `client.filesystem` | File operations (read, write, edit, search, tree, etc.) |
| `client.git` | Git operations (clone, commit, push, pull, branch, etc.) |
| `client.process` | Execute shell commands |
| `client.pty` | Interactive terminal sessions over WebSocket |
| `client.lsp` | Language Server Protocol for code intelligence |
| `client.ssh` | SSH credential management |
| `client.code_interpreter` | Code execution with streaming support |
| `client.desktop` | Graphical desktop control and screen recording |

## Configuration

```python
from leap0 import Leap0, Leap0Config

client = Leap0(Leap0Config(
    api_key="your-api-key",        # or set LEAP0_API_KEY env var
    base_url="https://api.leap0.dev",
    timeout=300,
))
```

| Option | Default | Description |
|---|---|---|
| `api_key` | `LEAP0_API_KEY` env var | API key for authentication |
| `base_url` | `https://api.leap0.dev` | API base URL |
| `sandbox_domain` | `sandbox.leap0.dev` | Domain for sandbox-scoped endpoints |
| `timeout` | `300` | HTTP client timeout in seconds |

## Examples

See the [`examples/`](examples/) directory for complete usage examples:

- **[quickstart.py](examples/quickstart.py)** - Basic code execution
- **[code_interpreter_stream.py](examples/code_interpreter_stream.py)** - Streaming code execution output
- **[filesystem_and_git.py](examples/filesystem_and_git.py)** - File and Git operations
- **[pty.py](examples/pty.py)** - Interactive terminal session
- **[desktop.py](examples/desktop.py)** - Desktop GUI automation

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Documentation

Full documentation is available at [leap0.dev/docs](https://leap0.dev/docs).

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
