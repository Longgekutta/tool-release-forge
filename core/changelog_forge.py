"""Release notes and changelog markdown builder."""
from collections import defaultdict
from datetime import datetime, timezone
from typing import List, Optional
from .commit_analyzer import CommitItem, CommitCategory

DEFAULT_TIMEOUT_SECONDS = 30
timeout=DEFAULT_TIMEOUT_SECONDS

class ReleaseNotesForge:
    def forge_markdown(self, tag: str, commits: List[CommitItem], project_name: str = "") -> str:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        title = f"# Release {tag} ({now_str})"
        if project_name:
            title = f"# {project_name} - Release {tag} ({now_str})"

        lines: List[str] = [title, ""]

        if not commits:
            lines.append("No significant commit changes recorded in this release window.")
            return "\n".join(lines) + "\n"

        by_cat = defaultdict(list)
        for c in commits:
            by_cat[c.category].append(c)

        # Print in priority order
        order = [
            CommitCategory.BREAKING,
            CommitCategory.FEATURES,
            CommitCategory.BUG_FIXES,
            CommitCategory.PERFORMANCE,
            CommitCategory.REFACTOR,
            CommitCategory.DOCUMENTATION,
            CommitCategory.TESTING,
            CommitCategory.CHORES,
        ]

        for cat in order:
            items = by_cat.get(cat, [])
            if not items:
                continue

            lines.append(f"## {cat.value}")
            for item in items:
                scope_prefix = f"**{item.scope}**: " if item.scope else ""
                author_str = f" (@{item.author})" if item.author else ""
                lines.append(f"- {scope_prefix}{item.subject} ([`{item.sha}`]){author_str}")
            lines.append("")

        lines.append("---")
        lines.append("Automated release notes synthesized by `tool-release-forge`.")
        return "\n".join(lines) + "\n"

    def forge_discussion_announcement(self, tag: str, commits: List[CommitItem], project_name: str = "", checksums: Optional[dict] = None) -> str:
        name = project_name or "Project"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        lines = [
            f"# 🎉 Announcing {name} {tag} ({now_str})",
            "",
            f"We are excited to announce the release of **{name} {tag}**!",
            "",
            "### 🌟 Highlights & Changelog",
            "",
            self.forge_markdown(tag, commits, project_name=name),
            "### 🔒 Cryptographic Verification",
            "Verify downloaded release artifacts using the official SHA-256 checksums:"
        ]
        if checksums:
            lines.append("| Asset | SHA-256 Checksum |")
            lines.append("| :--- | :--- |")
            for asset, sha in checksums.items():
                lines.append(f"| `{asset}` | `{sha}` |")
        else:
            lines.append("See attached `SHA256SUMS.txt` in GitHub Releases.")
        lines.append("")
        lines.append("### 💬 Community Feedback")
        lines.append("Let us know what you think in the comments below or report any issues in the repository tracker!")
        return "\n".join(lines) + "\n"
