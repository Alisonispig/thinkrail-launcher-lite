import json
import os
import hashlib
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

from updater_manifest import PLATFORMS, collect, merge, validate_version


class UpdateManifestTests(unittest.TestCase):
    def test_release_checksums_include_all_updater_files(self):
        from updater_manifest import ASSET_NAMES, REPOSITORY
        project = Path(__file__).resolve().parents[1]
        payload = (project / "src-tauri/test-fixtures/update-payload.txt").read_bytes()
        signature = (project / "src-tauri/test-fixtures/update-payload.sig").read_text(encoding="utf-8").strip()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "release-assets"
            root.mkdir()
            for platform, suffixes in {"macos-arm64": [".dmg", ".app.zip"], "macos-x64": [".dmg", ".app.zip"], "windows-x64": ["-setup.exe"], "linux-x64": [".deb", ".AppImage"]}.items():
                entries = []
                for suffix in suffixes:
                    name = f"ThinkRail-Launcher-Lite_2.0.0_{platform}{suffix}"
                    (root / name).write_bytes(payload)
                    entries.append({"name": name, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
                (root / f"manifest-{platform}.json").write_text(json.dumps({"version": "2.0.0", "platform": platform, "commit": "test-commit", "files": entries}))
            platforms = {}
            for platform, (package_platform, suffix) in ASSET_NAMES.items():
                name = f"ThinkRail-Launcher-Lite_2.0.0_{package_platform}{suffix}"
                (root / name).write_bytes(payload)
                (root / (name + ".sig")).write_text(signature)
                (root / f"{platform}.json").write_text("{}")
                platforms[platform] = {"url": f"https://github.com/{REPOSITORY}/releases/download/v2.0.0/{name}", "signature": signature}
            (root / "latest.json").write_text(json.dumps({"version": "2.0.0", "platforms": platforms}))
            result = subprocess.run([sys.executable, str(project / "scripts/finalize_release.py"), "--version", "2.0.0", "--commit", "test-commit"], cwd=root.parent, capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"})
            self.assertEqual(result.returncode, 0, result.stderr)
            checksums = (root / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(checksums), 15)
            self.assertEqual(len(list(root.iterdir())), 16)
            for line in checksums:
                checksum, name = line.split("  ")
                self.assertEqual(hashlib.sha256((root / name).read_bytes()).hexdigest(), checksum)

    def test_collect_and_merge_four_platforms(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "assets"
            for platform, (folder, suffix) in PLATFORMS.items():
                bundle = root / platform
                source = bundle / folder / ("example" + suffix)
                source.parent.mkdir(parents=True)
                source.write_bytes(b"example signed payload")
                source.with_name(source.name + ".sig").write_text("example-signature")
                collect(bundle, output, platform, "0.1.1")
            merge(output, "0.1.1", "更新说明")
            manifest = json.loads((output / "latest.json").read_text(encoding="utf-8"))
            self.assertEqual(set(manifest["platforms"]), set(PLATFORMS))
            self.assertEqual(manifest["notes"], "更新说明")
            self.assertIn("/releases/download/v0.1.1/", manifest["platforms"]["darwin-aarch64"]["url"])
            (output / "darwin-aarch64.json").unlink()
            with self.assertRaises(FileNotFoundError):
                merge(output, "0.1.1", "说明")

    def test_missing_signature_blocks_collection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "macos").mkdir()
            (root / "macos/app.app.tar.gz").write_bytes(b"unsigned")
            with self.assertRaises(FileNotFoundError):
                collect(root, root / "out", "darwin-aarch64", "0.1.1")

    def test_rejects_unsafe_and_prerelease_versions(self):
        for version in ["../escape", "1.2.3;command", "v1.2.3", "1.2.3-beta.1", "01.2.3", "1.2"]:
            with self.subTest(version=version), self.assertRaises(ValueError):
                validate_version(version)


if __name__ == "__main__":
    unittest.main()
