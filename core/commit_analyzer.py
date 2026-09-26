"""Git commit analyzer and Conventional Commits categorizer."""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
import subprocess
from typing import List, Optional

DEFAULT_TIMEOUT_SECONDS = 30
timeout=DEFAULT_TIMEOUT_SECONDS

class CommitCategory(str, Enum):
    BREAKING = "BREAKING CHANGES 🚨"
    FEATURES = "Features & Enhancements 🚀"
    BUG_FIXES = "Bug Fixes 🐛"
    PERFORMANCE = "Performance Optimizations ⚡"
    DOCUMENTATION = "Documentation 📚"
    REFACTOR = "Code Refactoring 🔨"
    TESTING = "Testing & QA 🧪"
    CHORES = "Chores & Maintenance 🔧"

@dataclass
class CommitItem:
    sha: str
    category: CommitCategory
    scope: Optional[str]
    subject: str
    author: str
    is_breaking: bool

def categorize_commit(sha: str, message: str, author: str = "") -> CommitItem:
    first_line = message.splitlines()[0].strip() if message else ""
    is_breaking = "BREAKING CHANGE" in message or "!:" in first_line

    pattern = r"^([a-zA-Z]+)(?:\(([^\)]+)\))?(!)?:\s*(.+)$"
    match = re.match(pattern, first_line)

    if match:
        tag = match.group(1).lower()
        scope = match.group(2)
        breaking_mark = match.group(3)
        subject = match.group(4).strip()
        if breaking_mark:
            is_breaking = True
    else:
        tag = "chore"
        scope = None
        subject = first_line

    if is_breaking:
        category = CommitCategory.BREAKING
    elif tag == "feat":
        category = CommitCategory.FEATURES
    elif tag == "fix":
        category = CommitCategory.BUG_FIXES
    elif tag == "perf":
        category = CommitCategory.PERFORMANCE
    elif tag == "docs":
        category = CommitCategory.DOCUMENTATION
    elif tag == "refactor":
        category = CommitCategory.REFACTOR
    elif tag in ["test", "tests"]:
        category = CommitCategory.TESTING
    else:
        category = CommitCategory.CHORES

    return CommitItem(
        sha=sha[:8] if sha else "HEAD",
        category=category,
        scope=scope,
        subject=subject,
        author=author,
        is_breaking=is_breaking
    )

def extract_git_commits(repo_dir: str | Path, from_ref: Optional[str] = None, to_ref: str = "HEAD") -> List[CommitItem]:
    repo = Path(repo_dir).resolve()
    if not (repo / ".git").exists():
        return []

    rev_range = f"{from_ref}..{to_ref}" if from_ref else to_ref
    cmd = ["git", "log", "--pretty=format:%H%x09%an%x09%s", rev_range, "-n", "100"]

    try:
        res = subprocess.run(
            cmd,
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            check=False
        )
        if res.returncode != 0:
            return []

        commits: List[CommitItem] = []
        for line in res.stdout.splitlines():
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                sha, author, msg = parts[0], parts[1], parts[2]
                commits.append(categorize_commit(sha, msg, author))
        return commits
    except Exception:
        return []
