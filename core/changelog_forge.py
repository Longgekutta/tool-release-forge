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
