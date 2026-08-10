import asyncio
import os
import re

from github import Github

from models.schemas import EvidenceSource

CODE_EXTENSIONS = (".sql", ".py")
COMMENT_PATTERNS = [
    re.compile(r"--\s*(.+)"),           # SQL line comment
    re.compile(r"#\s*(.+)"),            # Python line comment
    re.compile(r"/\*\s*(.+?)\s*\*/", re.DOTALL),  # Block comment
]


class GitMiner:
    def __init__(self):
        self.gh = Github(os.getenv("GITHUB_TOKEN"))
        self.repo = self.gh.get_repo(
            f"{os.getenv('GITHUB_REPO_OWNER')}/{os.getenv('GITHUB_REPO_NAME')}"
        )
        # Populated once on first use and reused across every mine() call —
        # avoids re-walking the whole repo tree per asset when mining
        # many assets back to back against the same repo.
        self._code_files_cache = None

    async def mine(self, asset_name: str) -> list[EvidenceSource]:
        """Mine all git artifacts mentioning this asset.

        PyGithub is a blocking/synchronous library, so this runs the actual
        work in a thread — that's what makes it possible to mine many
        assets concurrently via asyncio.gather instead of one at a time.
        """
        return await asyncio.to_thread(self._mine_sync, asset_name)

    def _mine_sync(self, asset_name: str) -> list[EvidenceSource]:
        evidence = []
        evidence += self._mine_commits(asset_name)
        evidence += self._mine_pull_requests(asset_name)
        evidence += self._mine_pr_comments(asset_name)
        evidence += self._mine_code_comments(asset_name)
        return evidence

    def _mine_commits(self, asset_name: str) -> list[EvidenceSource]:
        """Find commits that mention the asset name."""
        commits = self.repo.get_commits()
        results = []
        for commit in commits:
            if asset_name.lower() in commit.commit.message.lower():
                results.append(EvidenceSource(
                    type="commit_message",
                    url=commit.html_url,
                    author=commit.commit.author.name,
                    timestamp=commit.commit.author.date,
                    raw_excerpt=commit.commit.message[:500],
                    relevance_score=0.7,
                ))
            if len(results) >= 20:
                break
        return results

    def _mine_pull_requests(self, asset_name: str) -> list[EvidenceSource]:
        """Find PRs and their descriptions mentioning the asset."""
        pulls = self.repo.get_pulls(state="all")
        results = []
        for pr in pulls:
            text = f"{pr.title} {pr.body or ''}"
            if asset_name.lower() in text.lower():
                results.append(EvidenceSource(
                    type="pr_comment",
                    url=pr.html_url,
                    author=pr.user.login,
                    timestamp=pr.created_at,
                    raw_excerpt=f"PR: {pr.title}\n\n{(pr.body or '')[:800]}",
                    relevance_score=0.85,
                ))
            if len(results) >= 15:
                break
        return results

    def _mine_pr_comments(self, asset_name: str) -> list[EvidenceSource]:
        """Find review comments on PRs mentioning the asset."""
        results = []
        for comment in self.repo.get_pulls_review_comments():
            if asset_name.lower() in (comment.body or "").lower():
                results.append(EvidenceSource(
                    type="pr_comment",
                    url=comment.html_url,
                    author=comment.user.login if comment.user else None,
                    timestamp=comment.created_at,
                    raw_excerpt=comment.body[:500],
                    relevance_score=0.75,
                ))
            if len(results) >= 15:
                break
        return results

    def _get_code_files(self) -> list[tuple[str, str]]:
        """Fetch and decode every matching code file in the repo, once."""
        if self._code_files_cache is not None:
            return self._code_files_cache

        files = []
        contents = self.repo.get_contents("")
        stack = list(contents) if isinstance(contents, list) else [contents]

        while stack:
            item = stack.pop()
            if item.type == "dir":
                stack.extend(self.repo.get_contents(item.path))
                continue
            if not item.path.endswith(CODE_EXTENSIONS):
                continue
            try:
                text = item.decoded_content.decode("utf-8", errors="ignore")
            except Exception:
                continue
            files.append((item.path, text))

        self._code_files_cache = files
        return files

    def _mine_code_comments(self, asset_name: str) -> list[EvidenceSource]:
        """Search code for SQL/Python comments near mentions of the asset."""
        results = []
        for path, text in self._get_code_files():
            if len(results) >= 15:
                break
            if asset_name.lower() not in text.lower():
                continue

            for line in text.splitlines():
                if asset_name.lower() not in line.lower():
                    continue
                for pattern in COMMENT_PATTERNS:
                    match = pattern.search(line)
                    if match:
                        results.append(EvidenceSource(
                            type="code_comment",
                            url=f"{self.repo.html_url}/blob/main/{path}",
                            author=None,
                            timestamp=None,
                            raw_excerpt=match.group(1).strip()[:500],
                            relevance_score=0.6,
                        ))
                        break
                if len(results) >= 15:
                    break

        return results
