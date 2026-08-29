#!/usr/bin/env python3
import urllib.request
import json
import subprocess
import os
import time
import re
import sys

orig_repo = "nullcpy/rvb"
my_repo = os.environ.get("GITHUB_REPOSITORY", "m4mental/my-rvb-builder")
KEEP_NUMBERED_RELEASES = 3  # Keep latest 3 numbered releases, clean older ones

def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def main():
    print("🔍 Checking releases from original repo...")
    orig_releases = []
    for page in range(1, 6):
        data = get_json(f"https://api.github.com/repos/{orig_repo}/releases?per_page=100&page={page}")
        if isinstance(data, list) and len(data) > 0:
            orig_releases.extend(data)
        else:
            break

    my_releases = []
    for page in range(1, 6):
        data = get_json(f"https://api.github.com/repos/{my_repo}/releases?per_page=100&page={page}")
        if isinstance(data, list) and len(data) > 0:
            my_releases.extend(data)
        else:
            break

    my_rel_map = {}
    if isinstance(my_releases, list):
        for r in my_releases:
            tag = r.get('tag_name')
            if tag:
                my_rel_map[tag] = [a['name'] for a in r.get('assets', [])]

    # Ensure Permanent Archives exist
    for archive_tag in ["stable", "beta"]:
        if archive_tag not in my_rel_map:
            print(f"Creating permanent '{archive_tag}' archive release vault...")
            subprocess.run(["gh", "release", "create", archive_tag, "--repo", my_repo, "--title", f"{archive_tag.capitalize()} Builds Archive", "--notes", f"Permanent Vault for {archive_tag} builds"], check=False)
            if archive_tag == "beta":
                subprocess.run(["gh", "release", "edit", "beta", "--repo", my_repo, "--prerelease"], check=False)

    # Mirror New Builds from upstream
    for rel in reversed(orig_releases):
        tag = rel.get('tag_name')
        if not tag or tag in ["stable", "beta"]:
            continue

        title = rel.get('name') or tag
        body = rel.get('body') or ""
        is_prerelease = rel.get('prerelease', False)
        orig_assets = sorted([a['name'] for a in rel.get('assets', [])])

        if tag in my_rel_map:
            local_assets = sorted(my_rel_map[tag])
            if orig_assets == local_assets:
                print(f"✓ Tag {tag} matches 100%. Skipping.")
                continue
            else:
                print(f"⚠️ MISMATCH in Tag {tag}! Repairing...")
                subprocess.run(["gh", "release", "delete", tag, "--repo", my_repo, "-y", "--cleanup-tag"], check=False)
                time.sleep(2)

        print(f"🚀 Mirroring NEW Build: {tag} ({title})...")
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
            print(f"   📥 Downloading {fname}...")
            subprocess.run(["curl", "-sL", dl_url, "-o", f"{rm_dir}/{fname}"], check=False)

        # 1. Publish Numbered Release
        cmd = ["gh", "release", "create", tag, "--repo", my_repo]
        for fname in os.listdir(rm_dir):
            cmd.append(f"{rm_dir}/{fname}")
        cmd.extend(["--title", title, "--notes", clean_body])
        if is_prerelease:
            cmd.append("--prerelease")

        print(f"   📤 Publishing numbered release {tag}...")
        subprocess.run(cmd, check=False)

        # 2. Always Update Permanent Archive (stable / beta)
        target_archive = "beta" if is_prerelease else "stable"
        print(f"   🔄 Syncing new files to permanent '{target_archive}' archive vault...")
        archive_cmd = ["gh", "release", "upload", target_archive, "--repo", my_repo]
        for fname in os.listdir(rm_dir):
            archive_cmd.append(f"{rm_dir}/{fname}")
        archive_cmd.append("--clobber")
        subprocess.run(archive_cmd, check=False)

        subprocess.run(["rm", "-rf", rm_dir], check=False)
        print(f"✓ Build {tag} mirrored & permanent archive updated successfully!")
        time.sleep(2)

    # 3. Clean up Old Numbered Releases (Keep permanent stable/beta + latest 3 numbered builds)
    print("🧹 Checking for old numbered releases to clean...")
    current_releases = get_json(f"https://api.github.com/repos/{my_repo}/releases?per_page=100")
    if isinstance(current_releases, list):
        numbered_releases = [r for r in current_releases if r.get('tag_name') not in ["stable", "beta"]]
        # Sort by creation / published date (newest first)
        numbered_releases.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        if len(numbered_releases) > KEEP_NUMBERED_RELEASES:
            to_delete = numbered_releases[KEEP_NUMBERED_RELEASES:]
            print(f"🗑️ Found {len(to_delete)} old numbered releases to clean up (Keeping latest {KEEP_NUMBERED_RELEASES})...")
            for old_rel in to_delete:
                old_tag = old_rel.get('tag_name')
                print(f"   Deleting old numbered release: {old_tag}...")
                subprocess.run(["gh", "release", "delete", old_tag, "--repo", my_repo, "-y", "--cleanup-tag"], check=False)
                time.sleep(1)

    print("🎉 Mirroring & Cleanup Complete! Permanent archives (stable & beta) are 100% up-to-date.")

if __name__ == "__main__":
    main()
