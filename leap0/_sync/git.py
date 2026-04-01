from __future__ import annotations

from typing import cast

from .._internal.types import JsonObject
from ._transport import Transport
from .._utils.errors import intercept_errors
from ..models.git import GitCommitResult, GitResult
from .._schemas.git import GitCommitResponseDict, GitResultDict
from ..models.sandbox import SandboxRef, sandbox_id_of


class GitClient:
    """Clone repositories, inspect diffs and history, manage branches, stage
        files, commit, push, and pull inside a running sandbox.
    
        This client is useful when you want to automate Git workflows without
        shelling out manually through :class:`ProcessClient`.
        
    Attributes:
        None.
    """

    def __init__(self, transport: Transport):
        self._transport = transport

    def _git_result(self, path: str, payload: JsonObject, http_timeout: float | None = None) -> GitResult:
        data = cast(GitResultDict, self._transport.request_json("POST", path, json=payload, timeout=http_timeout))
        return GitResult.from_dict(data)

    @intercept_errors("Failed to clone repository: ")
    def clone(
        self,
        sandbox: SandboxRef,
        *,
        url: str,
        path: str,
        branch: str | None = None,
        commit_id: str | None = None,
        depth: int | None = None,
        username: str | None = None,
        password: str | None = None,
        http_timeout: float | None = None,
    ) -> GitResult:
        """Clone a remote repository into the sandbox.

        Args:
            sandbox: Sandbox ID or object.
            url: Repository URL.
            path: Destination path inside the sandbox.
            branch: Branch to clone.
            commit_id: Specific commit to checkout after cloning.
            depth: Shallow clone depth.
            username: Auth username (for private repos).
            password: Auth password or token (for private repos).
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            GitResult: Command output and exit status from the clone operation.
        """
        payload: JsonObject = {"url": url, "path": path}
        if branch is not None:
            payload["branch"] = branch
        if commit_id is not None:
            payload["commit_id"] = commit_id
        if depth is not None:
            payload["depth"] = depth
        if username is not None:
            payload["username"] = username
        if password is not None:
            payload["password"] = password
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/clone", payload, http_timeout=http_timeout)

    @intercept_errors("Failed to get git status: ")
    def status(self, sandbox: SandboxRef, *, path: str, http_timeout: float | None = None) -> GitResult:
        """Get the current repository status.
        
                Returns:
                    GitResult: Git status output and exit status.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/status", {"path": path}, http_timeout=http_timeout)

    @intercept_errors("Failed to list branches: ")
    def branches(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        branch_type: str = "local",
        contains: str | None = None,
        not_contains: str | None = None,
        http_timeout: float | None = None,
    ) -> GitResult:
        """List branches in the repository.
        
                Args:
                    sandbox: Sandbox ID or object.
                    path: Path to the git repo.
                    branch_type: Filter by ``"local"``, ``"remote"``, or ``"all"``.
                    contains: Only branches containing this commit SHA.
                    not_contains: Exclude branches containing this commit SHA.
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"path": path, "branch_type": branch_type}
        if contains is not None:
            payload["contains"] = contains
        if not_contains is not None:
            payload["not_contains"] = not_contains
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/branches", payload, http_timeout=http_timeout)

    @intercept_errors("Failed to get unstaged diff: ")
    def diff_unstaged(self, sandbox: SandboxRef, *, path: str, context_lines: int | None = None, http_timeout: float | None = None) -> GitResult:
        """
                    Show working tree changes that are not staged yet.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"path": path}
        if context_lines is not None:
            payload["context_lines"] = context_lines
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/diff-unstaged", payload, http_timeout=http_timeout)

    @intercept_errors("Failed to get staged diff: ")
    def diff_staged(self, sandbox: SandboxRef, *, path: str, context_lines: int | None = None, http_timeout: float | None = None) -> GitResult:
        """
                    Show changes that are already staged for the next commit.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"path": path}
        if context_lines is not None:
            payload["context_lines"] = context_lines
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/diff-staged", payload, http_timeout=http_timeout)

    @intercept_errors("Failed to get diff: ")
    def diff(self, sandbox: SandboxRef, *, path: str, target: str, context_lines: int | None = None, http_timeout: float | None = None) -> GitResult:
        """
                    Compare the current state against a branch, tag, or commit.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"path": path, "target": target}
        if context_lines is not None:
            payload["context_lines"] = context_lines
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/diff", payload, http_timeout=http_timeout)

    @intercept_errors("Failed to reset: ")
    def reset(self, sandbox: SandboxRef, *, path: str) -> GitResult:
        """Unstage all currently staged changes.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/reset", {"path": path})

    @intercept_errors("Failed to get git log: ")
    def log(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        max_count: int | None = None,
        start_timestamp: str | None = None,
        end_timestamp: str | None = None,
        http_timeout: float | None = None,
    ) -> GitResult:
        """Show commit history with optional limits and date filters.
        
                Args:
                    sandbox: Sandbox ID or object.
                    path: Path to the git repo.
                    max_count: Maximum number of commits to return (default 10).
                    start_timestamp: Start timestamp filter.
                    end_timestamp: End timestamp filter.
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"path": path}
        if max_count is not None:
            payload["max_count"] = max_count
        if start_timestamp is not None:
            payload["start_timestamp"] = start_timestamp
        if end_timestamp is not None:
            payload["end_timestamp"] = end_timestamp
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/log", payload, http_timeout=http_timeout)

    @intercept_errors("Failed to show revision: ")
    def show(self, sandbox: SandboxRef, *, path: str, revision: str = "HEAD") -> GitResult:
        """Show the full output for a commit, branch, or tag revision.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
            revision: Parameter for this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/show", {"path": path, "revision": revision})

    @intercept_errors("Failed to create branch: ")
    def create_branch(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        name: str,
        checkout: bool | None = None,
        base_branch: str | None = None,
        http_timeout: float | None = None,
    ) -> GitResult:
        """Create a new branch.
        
                Args:
                    sandbox: Sandbox ID or object.
                    path: Path to the git repo.
                    name: New branch name.
                    checkout: Switch to the new branch immediately.
                    base_branch: Branch from a specific revision.
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"path": path, "name": name}
        if checkout is not None:
            payload["checkout"] = checkout
        if base_branch is not None:
            payload["base_branch"] = base_branch
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/create-branch", payload, http_timeout=http_timeout)

    @intercept_errors("Failed to checkout branch: ")
    def checkout_branch(self, sandbox: SandboxRef, *, path: str, branch: str, create: bool | None = None, http_timeout: float | None = None) -> GitResult:
        """
                    Switch to an existing branch. Set *create* to create it if it does not exist.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"path": path, "branch": branch}
        if create is not None:
            payload["create"] = create
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/checkout-branch", payload, http_timeout=http_timeout)

    @intercept_errors("Failed to delete branch: ")
    def delete_branch(self, sandbox: SandboxRef, *, path: str, name: str, force: bool = False) -> GitResult:
        """Delete a branch. Set *force* to delete even if unmerged.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
            name: Name used by this operation.
            force: Parameter for this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/delete-branch", {"path": path, "name": name, "force": force})

    @intercept_errors("Failed to stage files: ")
    def add(self, sandbox: SandboxRef, *, path: str, files: list[str], http_timeout: float | None = None) -> GitResult:
        """
                    Stage files for the next commit.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/add", {"path": path, "files": files}, http_timeout=http_timeout)

    @intercept_errors("Failed to commit: ")
    def commit(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        message: str,
        author: str | None = None,
        email: str | None = None,
        allow_empty: bool | None = None,
        http_timeout: float | None = None,
    ) -> GitCommitResult:
        """Create a commit from staged changes.

        Args:
            sandbox: Sandbox ID or object.
            path: Path to the git repo.
            message: Commit message.
            author: Author name.
            email: Author email.
            allow_empty: Allow creating an empty commit.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            GitCommitResult: Commit result including commit ID when successful.
        """
        payload: JsonObject = {"path": path, "message": message}
        if author is not None:
            payload["author"] = author
        if email is not None:
            payload["email"] = email
        if allow_empty is not None:
            payload["allow_empty"] = allow_empty
        data = cast(GitCommitResponseDict, self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/commit",
            json=payload,
            timeout=http_timeout,
        ))
        return GitCommitResult.from_dict(data)

    @intercept_errors("Failed to push: ")
    def push(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        remote: str | None = None,
        branch: str | None = None,
        set_upstream: bool | None = None,
        username: str | None = None,
        password: str | None = None,
        http_timeout: float | None = None,
    ) -> GitResult:
        """Push commits to a remote.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
            remote: Parameter for this operation.
            branch: Parameter for this operation.
            set_upstream: Parameter for this operation.
            username: Parameter for this operation.
            password: Parameter for this operation.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"path": path}
        if remote is not None:
            payload["remote"] = remote
        if branch is not None:
            payload["branch"] = branch
        if set_upstream is not None:
            payload["set_upstream"] = set_upstream
        if username is not None:
            payload["username"] = username
        if password is not None:
            payload["password"] = password
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/push", payload, http_timeout=http_timeout)

    @intercept_errors("Failed to pull: ")
    def pull(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        remote: str | None = None,
        branch: str | None = None,
        rebase: bool | None = None,
        set_upstream: bool | None = None,
        username: str | None = None,
        password: str | None = None,
        http_timeout: float | None = None,
    ) -> GitResult:
        """Pull commits from a remote. Set *rebase* to rebase instead of merge.
        
                Args:
                    sandbox: Sandbox ID or object.
                    path: Path to the git repo.
                    remote: Remote name (default ``"origin"``).
                    branch: Branch name.
                    rebase: Rebase instead of merge.
                    set_upstream: Set upstream tracking.
                    username: Auth username.
                    password: Auth password or token.
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"path": path}
        if remote is not None:
            payload["remote"] = remote
        if branch is not None:
            payload["branch"] = branch
        if rebase is not None:
            payload["rebase"] = rebase
        if set_upstream is not None:
            payload["set_upstream"] = set_upstream
        if username is not None:
            payload["username"] = username
        if password is not None:
            payload["password"] = password
        return self._git_result(f"/v1/sandbox/{sandbox_id_of(sandbox)}/git/pull", payload, http_timeout=http_timeout)
