"""GitHub Release publishing orchestrator using gh CLI."""
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import List, Optional

DEFAULT_TIMEOUT_SECONDS = 30
timeout=DEFAULT_TIMEOUT_SECONDS

@dataclass
class PublishPlan:
    tag: str
    notes_file: Path
    assets: List[Path]
    command_str: str
    draft: bool = False
    prerelease: bool = False
    discussion_category: Optional[str] = None

class ReleasePublisher:
    def create_plan(
        self,
        tag: str,
        notes_file: Path,
        assets: List[Path],
        draft: bool = False,
        prerelease: bool = False,
        discussion_category: Optional[str] = None
    ) -> PublishPlan:
        cmd_parts = ["gh", "release", "create", tag]
        for a in assets:
            cmd_parts.append(f'"{a.as_posix()}"')
        cmd_parts.extend(["-F", f'"{notes_file.as_posix()}"'])
        if draft:
            cmd_parts.append("--draft")
        if prerelease:
            cmd_parts.append("--prerelease")
        if discussion_category:
            cmd_parts.append(f'--discussion-category "{discussion_category}"')

        return PublishPlan(
            tag=tag,
            notes_file=notes_file,
            assets=assets,
            command_str=" ".join(cmd_parts),
            draft=draft,
            prerelease=prerelease,
            discussion_category=discussion_category
        )

    def execute_publish(self, plan: PublishPlan) -> bool:
        cmd = ["gh", "release", "create", plan.tag]
        for a in plan.assets:
            cmd.append(str(a))
        cmd.extend(["-F", str(plan.notes_file)])
        if plan.draft:
            cmd.append("--draft")
        if plan.prerelease:
            cmd.append("--prerelease")
        if plan.discussion_category:
            cmd.extend(["--discussion-category", plan.discussion_category])

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT_SECONDS,
                check=False
            )
            return res.returncode == 0
        except Exception:
            return False
