"""Artifact compression packager and SHA256 checksum generator."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import shutil
import tarfile
from typing import List, Dict, Optional
import zipfile

DEFAULT_TIMEOUT_SECONDS = 30
timeout=DEFAULT_TIMEOUT_SECONDS

@dataclass
class ArtifactBundle:
    output_dir: Path
    archives: List[Path]
    checksum_file: Path
    hashes: Dict[str, str]

def calculate_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

class ReleasePackager:
    def __init__(self, output_dir: str | Path = "dist"):
        self.output_dir = Path(output_dir).resolve()

    def package_directory(self, source_dir: str | Path, tag: str, project_name: str) -> ArtifactBundle:
        src = Path(source_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        base_name = f"{project_name}-{tag}"

        archives: List[Path] = []
        hashes: Dict[str, str] = {}

        # 1. Create .tar.gz
        tar_path = self.output_dir / f"{base_name}.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tar:
            for item in src.iterdir():
                if item.name not in [".git", "dist", "release_assets", "__pycache__", ".venv"]:
                    tar.add(item, arcname=f"{base_name}/{item.name}")
        archives.append(tar_path)
        hashes[tar_path.name] = calculate_sha256(tar_path)

        # 2. Create .zip
        zip_path = self.output_dir / f"{base_name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for item in src.rglob("*"):
                if not any(part in [".git", "dist", "release_assets", "__pycache__", ".venv"] for part in item.parts):
                    if item.is_file():
                        rel = item.relative_to(src)
                        zipf.write(item, arcname=f"{base_name}/{rel}")
        archives.append(zip_path)
        hashes[zip_path.name] = calculate_sha256(zip_path)

        # 3. Create SHA256SUMS file
        sums_path = self.output_dir / "SHA256SUMS"
        sums_lines = [f"{digest}  {name}" for name, digest in hashes.items()]
        sums_path.write_text("\n".join(sums_lines) + "\n", encoding="utf-8")

        return ArtifactBundle(
            output_dir=self.output_dir,
            archives=archives,
            checksum_file=sums_path,
            hashes=hashes
        )
