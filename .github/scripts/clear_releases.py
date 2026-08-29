#!/usr/bin/env python3
import subprocess
import json
import os

def main():
    repo = os.environ.get("GITHUB_REPOSITORY", "m4mental/my-rvb-builder")
    print(f"Fetching releases for {repo}...")

    try:
        cmd = ["gh", "api", "--paginate", f"repos/{repo}/releases"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        raw_out = res.stdout.strip()

        if not raw_out:
            print("No releases found.")
            return

        releases = []
        if raw_out.startswith("["):
            releases = json.loads(raw_out)
        else:
            for line in raw_out.splitlines():
                if line.strip():
                    releases.extend(json.loads(line.strip()))

        for rel in releases:
            rel_id = rel['id']
            tag = rel.get('tag_name') or ''
            is_draft = rel.get('draft', False)

            # PROTECT STABLE & BETA ARCHIVES
            if tag in ["stable", "beta"]:
                print(f"🛡️ PROTECTED: Keeping permanent archive '{tag}' (ID: {rel_id})")
                continue

            print(f"🗑️ Deleting Old Release: {tag} (ID: {rel_id}, Draft: {is_draft})")
            subprocess.run(["gh", "release", "delete", tag, "--repo", repo, "-y", "--cleanup-tag"], check=False)

        print("🎉 Old numbered releases cleared! Permanent archives (stable/beta) preserved.")
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    main()
