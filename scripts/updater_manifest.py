"""收集 Tauri 签名更新包并合并 GitHub 静态更新清单，不发布 Release。"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil

REPOSITORY = "Alisonispig/thinkrail-launcher-lite"
PLATFORMS = {
    "darwin-aarch64": ("macos", ".app.tar.gz"),
    "darwin-x86_64": ("macos", ".app.tar.gz"),
    "windows-x86_64": ("nsis", ".exe"),
    "linux-x86_64": ("appimage", ".AppImage"),
}
ASSET_NAMES = {
    "darwin-aarch64": ("macos-arm64", ".app.tar.gz"),
    "darwin-x86_64": ("macos-x64", ".app.tar.gz"),
    "windows-x86_64": ("windows-x64", "-setup.exe"),
    "linux-x86_64": ("linux-x64", ".AppImage"),
}


def validate_version(version):
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        raise ValueError("版本必须为正式版本，例如 0.1.1")


def collect(bundle_dir, output, platform, version):
    validate_version(version)
    directory, suffix = PLATFORMS[platform]
    candidates = list((bundle_dir / directory).glob(f"*{suffix}"))
    if len(candidates) != 1:
        raise ValueError(f"{platform} 应有且仅有一个更新包，实际 {len(candidates)}")
    source = candidates[0]
    signature = source.with_name(source.name + ".sig").read_text(encoding="utf-8").strip()
    if not signature:
        raise ValueError("更新包缺少签名")
    package_platform, package_suffix = ASSET_NAMES[platform]
    name = f"ThinkRail-Launcher-Lite_{version}_{package_platform}{package_suffix}"
    output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, output / name)
    (output / (name + ".sig")).write_text(signature + "\n", encoding="utf-8")
    entry = {"version": version, "platform": platform, "signature": signature,
             "url": f"https://github.com/{REPOSITORY}/releases/download/v{version}/{name}"}
    (output / f"{platform}.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")


def merge(directory, version, notes):
    validate_version(version)
    platforms = {}
    for platform in PLATFORMS:
        entry = json.loads((directory / f"{platform}.json").read_text(encoding="utf-8"))
        if entry["version"] != version or entry["platform"] != platform:
            raise ValueError("平台版本与发布版本不一致")
        name = entry["url"].rsplit("/", 1)[-1]
        expected = f"https://github.com/{REPOSITORY}/releases/download/v{version}/{name}"
        if entry["url"] != expected or not (directory / name).is_file():
            raise ValueError("更新包地址或文件无效")
        if not entry["signature"] or (directory / (name + ".sig")).read_text(encoding="utf-8").strip() != entry["signature"]:
            raise ValueError("签名文件不一致")
        platforms[platform] = {"url": entry["url"], "signature": entry["signature"]}
    manifest = {"version": version, "notes": notes,
                "pub_date": datetime.now(timezone.utc).isoformat(), "platforms": platforms}
    (directory / "latest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["collect", "merge"])
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, default=Path("release-assets"))
    parser.add_argument("--bundle-dir", type=Path)
    parser.add_argument("--platform", choices=PLATFORMS)
    parser.add_argument("--notes", type=Path)
    args = parser.parse_args()
    if args.mode == "collect":
        if args.bundle_dir is None or args.platform is None:
            parser.error("collect 需要 --bundle-dir 和 --platform")
        collect(args.bundle_dir, args.output, args.platform, args.version)
    else:
        if args.notes is None:
            parser.error("merge 需要 --notes")
        merge(args.output, args.version, args.notes.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
