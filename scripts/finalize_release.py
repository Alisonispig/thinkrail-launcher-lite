"""核对四个原生构建的清单并生成总校验文件。"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
from updater_manifest import ASSET_NAMES, REPOSITORY


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    root = Path("release-assets")
    manifests = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.glob("manifest-*.json"))]
    assert {m["platform"] for m in manifests} == {"macos-arm64", "macos-x64", "windows-x64", "linux-x64"}
    assert len(manifests) == 4
    files = []
    for manifest in manifests:
        assert manifest["version"] == args.version and manifest["commit"] == args.commit
        for entry in manifest["files"]:
            path = root / entry["name"]
            assert path.name == entry["name"] and path.stat().st_size == entry["bytes"] > 0
            assert digest(path) == entry["sha256"], f"校验失败：{path.name}"
            files.append(path)
    assert len(files) == 7 and len({p.name for p in files}) == 7
    latest = root / "latest.json"
    updater = json.loads(latest.read_text(encoding="utf-8"))
    assert updater["version"] == args.version
    assert set(updater["platforms"]) == set(ASSET_NAMES)
    for platform, (package_platform, suffix) in ASSET_NAMES.items():
        name = f"ThinkRail-Launcher-Lite_{args.version}_{package_platform}{suffix}"
        entry = updater["platforms"][platform]
        assert entry["url"] == f"https://github.com/{REPOSITORY}/releases/download/v{args.version}/{name}"
        payload, signature = root / name, root / (name + ".sig")
        assert payload.is_file() and payload.stat().st_size > 0
        assert signature.read_text(encoding="utf-8").strip() == entry["signature"]
        signed = base64.b64decode(entry["signature"], validate=True).decode("utf-8")
        trusted = next(line for line in signed.splitlines() if line.startswith("trusted comment:"))
        assert f"version:{args.version}" in trusted.split("\t"), "签名版本不一致"
        for path in (payload, signature):
            if path not in files:
                files.append(path)
    files.append(latest)
    metadata = root / "BUILD-METADATA.json"
    metadata.write_text(json.dumps({"version": args.version, "commit": args.commit, "builds": manifests, "updaterPlatforms": sorted(updater["platforms"])}, indent=2) + "\n", encoding="utf-8")
    files.append(metadata)
    (root / "SHA256SUMS.txt").write_text("".join(f"{digest(p)}  {p.name}\n" for p in sorted(files)), encoding="utf-8")
    for path in root.glob("manifest-*.json"):
        path.unlink()
    for platform in ASSET_NAMES:
        (root / f"{platform}.json").unlink()
    print(f"已核对 {len(files)} 个发布文件，并生成 SHA256SUMS.txt")


if __name__ == "__main__":
    main()
