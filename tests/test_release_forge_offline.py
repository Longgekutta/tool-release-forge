"""Hermetic offline unit tests for tool-release-forge."""
import tempfile
import unittest
from pathlib import Path

from core.commit_analyzer import categorize_commit, CommitCategory
from core.changelog_forge import ReleaseNotesForge
from core.packager import ReleasePackager, calculate_sha256
from core.publisher import ReleasePublisher

DEFAULT_TIMEOUT_SECONDS = 30
timeout=DEFAULT_TIMEOUT_SECONDS

class TestReleaseForgeOffline(unittest.TestCase):
    def test_01_categorize_commit_conventional(self):
        c1 = categorize_commit("11111111", "feat(parser): add support for Cargo.lock")
        self.assertEqual(c1.category, CommitCategory.FEATURES)
        self.assertEqual(c1.scope, "parser")

        c2 = categorize_commit("22222222", "fix: correct null pointer in validator")
        self.assertEqual(c2.category, CommitCategory.BUG_FIXES)

        c3 = categorize_commit("33333333", "feat!: overhaul CLI architecture")
        self.assertEqual(c3.category, CommitCategory.BREAKING)
        self.assertTrue(c3.is_breaking)

        c4 = categorize_commit("44444444", "docs: update README with 3-second quickstart")
        self.assertEqual(c4.category, CommitCategory.DOCUMENTATION)

    def test_02_forge_markdown_sections(self):
        commits = [
            categorize_commit("aaa111", "feat: new cool feature", author="alice"),
            categorize_commit("bbb222", "fix: repair memory leak", author="bob"),
        ]
        forge = ReleaseNotesForge()
        md = forge.forge_markdown("v1.2.0", commits, project_name="MatrixCore")

        self.assertIn("# MatrixCore - Release v1.2.0", md)
        self.assertIn("## Features & Enhancements 🚀", md)
        self.assertIn("## Bug Fixes 🐛", md)
        self.assertIn("new cool feature", md)
        self.assertIn("@alice", md)

    def test_03_packager_creates_tar_zip_and_sha256sums(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src = tmp / "src"
            src.mkdir()
            (src / "app.py").write_text("print('hello world')\n", encoding="utf-8")
            (src / "config.json").write_text("{}", encoding="utf-8")

            out_dir = tmp / "dist"
            packager = ReleasePackager(output_dir=out_dir)
            bundle = packager.package_directory(src, "v1.0.0", "demo-app")

            self.assertEqual(len(bundle.archives), 2)
            tar_file = out_dir / "demo-app-v1.0.0.tar.gz"
            zip_file = out_dir / "demo-app-v1.0.0.zip"
            sums_file = out_dir / "SHA256SUMS"

            self.assertTrue(tar_file.is_file())
            self.assertTrue(zip_file.is_file())
            self.assertTrue(sums_file.is_file())

            # Checksums integrity
            sums_content = sums_file.read_text(encoding="utf-8")
            self.assertIn("demo-app-v1.0.0.tar.gz", sums_content)
            self.assertIn("demo-app-v1.0.0.zip", sums_content)

    def test_04_publisher_plan_creates_gh_command(self):
        publisher = ReleasePublisher()
        notes = Path("dist/NOTES.md")
        assets = [Path("dist/app.tar.gz"), Path("dist/SHA256SUMS")]
        plan = publisher.create_plan("v2.0.0", notes, assets)

        self.assertEqual(plan.tag, "v2.0.0")
        self.assertIn("gh release create v2.0.0", plan.command_str)
        self.assertIn("-F \"dist/NOTES.md\"", plan.command_str)

    def test_05_release_config_generator(self):
        from core.release_config_generator import write_release_yml
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cfg_file = write_release_yml(tmp)
            self.assertTrue(cfg_file.is_file())
            content = cfg_file.read_text(encoding="utf-8")
            self.assertIn("changelog:", content)
            self.assertIn("categories:", content)
            self.assertIn("Breaking Changes", content)
            self.assertIn("dependabot[bot]", content)

    def test_06_publisher_draft_prerelease_discussion(self):
        publisher = ReleasePublisher()
        notes = Path("dist/NOTES.md")
        assets = [Path("dist/app.tar.gz")]
        plan = publisher.create_plan(
            "v3.0.0-rc1",
            notes,
            assets,
            draft=True,
            prerelease=True,
            discussion_category="Announcements"
        )
        self.assertTrue(plan.draft)
        self.assertTrue(plan.prerelease)
        self.assertEqual(plan.discussion_category, "Announcements")
        self.assertIn("--draft", plan.command_str)
        self.assertIn("--prerelease", plan.command_str)
        self.assertIn("--discussion-category \"Announcements\"", plan.command_str)

if __name__ == "__main__":
    unittest.main()
