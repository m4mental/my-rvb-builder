#!/usr/bin/env python3
import urllib.request
import json
import subprocess
import os
import time
import re
import sys
import io
import shutil

# Ensure UTF-8 output on all systems
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

orig_repo = "nullcpy/rvb"
my_repo = os.environ.get("GITHUB_REPOSITORY", "m4mental/my-rvb-builder")
gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""

def get_json(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    if gh_token:
        headers['Authorization'] = f'Bearer {gh_token}'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def run_cmd(cmd):
    if not shutil.which(cmd[0]):
        print(f"   [Dry-run] Would execute: {' '.join(cmd)}")
        return
    try:
        subprocess.run(cmd, check=False)
    except Exception as e:
        print(f"   Command error: {e}")

def main():
    print(f"🔍 Checking latest releases between {orig_repo} and {my_repo}...")

    # Fetch latest 20 releases from upstream (active current builds)
    orig_data = get_json(f"https://api.github.com/repos/{orig_repo}/releases?per_page=20")
    if not isinstance(orig_data, list) or len(orig_data) == 0:
        print("⚠️ Could not fetch upstream releases or no releases found. Skipping.")
        return

    # Fetch existing releases in our repo
    my_data = get_json(f"https://api.github.com/repos/{my_repo}/releases?per_page=50")
    my_rel_map = {}
    if isinstance(my_data, list):
        for r in my_data:
            tag = r.get('tag_name')
            if tag:
                my_rel_map[tag] = set(a['name'] for a in r.get('assets', []))

    # Ensure Permanent Archives exist
    for archive_tag in ["stable", "beta"]:
        if archive_tag not in my_rel_map:
            print(f"Creating permanent '{archive_tag}' archive release vault...")
            run_cmd(["gh", "release", "create", archive_tag, "--repo", my_repo, "--title", f"{archive_tag.capitalize()} Builds Archive", "--notes", f"Permanent Vault for {archive_tag} builds"])
            if archive_tag == "beta":
                run_cmd(["gh", "release", "edit", "beta", "--repo", my_repo, "--prerelease"])

    # Find ONLY genuinely NEW releases that do not exist locally
    new_releases_to_mirror = []
    for rel in reversed(orig_data):
        tag = rel.get('tag_name')
        if not tag or tag in ["stable", "beta"]:
            continue

        orig_asset_names = set(a['name'] for a in rel.get('assets', []))

        # Check if already present and has assets
        if tag in my_rel_map:
            local_asset_names = my_rel_map[tag]
            if orig_asset_names == local_asset_names or len(local_asset_names) > 0:
                # Already mirrored and synced, skip!
                continue

        new_releases_to_mirror.append(rel)

    # If everything is in sync, do nothing and exit immediately!
    if not new_releases_to_mirror:
        print("✅ All releases are 100% in sync with original repo! Skipping, no extra builds created.")
        return

    print(f"🚀 Found {len(new_releases_to_mirror)} new release(s) to mirror...")

    for rel in new_releases_to_mirror:
        tag = rel.get('tag_name')
        title = rel.get('name') or tag
        body = rel.get('body') or ""
        is_prerelease = rel.get('prerelease', False)

        print(f"📥 Mirroring NEW Build: {tag} ({title})...")
        clean_body = re.sub(r'\[GitHub\]\([^)]+\)', r'[GitHub](https://github.com/m4mental/my-rvb-builder)', body)
        clean_body = re.sub(r'\[Website\]\([^)]+\)', r'[Website](https://m4mental.github.io/)', clean_body)
        clean_body = clean_body.replace("ReVanced & Morphe Builder", "M4Mental Hub")
        clean_body = clean_body.replace("NullStore", "M4Mental Hub")
        clean_body = re.sub(r'\|[ \t]*\[Group\]\([^)]+\)', '', clean_body)
        clean_body = re.sub(r'\|[ \t]*\[Donate\]\([^)]+\)', '', clean_body)
        clean_body = re.sub(r'\[Group\]\([^)]+\)', '', clean_body)
        clean_body = re.sub(r'\[Donate\]\([^)]+\)', '', clean_body)

        rm_dir = f"./tmp_assets_{tag}"
        os.makedirs(rm_dir, exist_ok=True)

        for asset in rel.get('assets', []):
            dl_url = asset['browser_download_url']
            fname = asset['name']
            print(f"   Downloading {fname}...")
            run_cmd(["curl", "-sL", dl_url, "-o", f"{rm_dir}/{fname}"])

        # 1. Publish Numbered Release
        cmd = ["gh", "release", "create", tag, "--repo", my_repo]
        for fname in os.listdir(rm_dir):
            cmd.append(f"{rm_dir}/{fname}")
        cmd.extend(["--title", title, "--notes", clean_body])
        if is_prerelease:
            cmd.append("--prerelease")

        run_cmd(cmd)

        # 2. Update Permanent Archive (stable / beta)
        target_archive = "beta" if is_prerelease else "stable"
        print(f"   🔄 Updating permanent '{target_archive}' archive vault...")
        archive_cmd = ["gh", "release", "upload", target_archive, "--repo", my_repo]
        for fname in os.listdir(rm_dir):
            archive_cmd.append(f"{rm_dir}/{fname}")
        archive_cmd.append("--clobber")
        run_cmd(archive_cmd)

        run_cmd(["rm", "-rf", rm_dir])
        print(f"✓ Tag {tag} mirrored successfully!")
        time.sleep(2)

    print("🎉 Smart Mirroring Complete!")

if __name__ == "__main__":
    main()
