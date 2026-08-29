#!/usr/bin/env python3
import re
import os

def clean_and_brand_readme(path="README.md"):
    if not os.path.exists(path):
        print(f"File {path} not found.")
        return

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clean_lines = []
    skip_support_section = False

    for line in lines:
        # Skip Palestine Banner
        if "support-palestine-banner" in line or "Support Palestine" in line or "techforpalestine" in line:
            continue

        # Skip Support / Donation Sections
        if "Support the Project" in line or "🤝 Support" in line or "Support Us" in line:
            skip_support_section = True
            continue
        if skip_support_section and (line.startswith("## ") or line.startswith("---") or line.startswith("> [!NOTE]")):
            skip_support_section = False

        if skip_support_section:
            continue

        # Clean external badges (Group, Channel, Donate)
        if "badge/Group-" in line or "badge/Channel-" in line or "badge/Donate-" in line or "t.me/rvb" in line or "fahim-ahmed05" in line or "buymeacoffee" in line:
            line = re.sub(r'<a href="[^"]*t\.me/[^"]*">.*?</a>\s*', '', line)
            line = re.sub(r'<a href="[^"]*donate[^"]*">.*?</a>\s*', '', line)
            line = re.sub(r'<a href="[^"]*buymeacoffee[^"]*">.*?</a>\s*', '', line)
            line = re.sub(r'\[Group\]\([^)]+\)', '', line)
            line = re.sub(r'\[Donate\]\([^)]+\)', '', line)
            line = re.sub(r'\|[ \t]*\[Group\]\([^)]+\)', '', line)
            line = re.sub(r'\|[ \t]*\[Donate\]\([^)]+\)', '', line)
            if re.sub(r'<[^>]+>', '', line).strip() == '':
                continue

        # Clean telegram text references
        line = re.sub(r'\[send a message in our Telegram Group\]\([^)]+\)', 'open an Issue here on GitHub', line)
        line = re.sub(r'\[our Telegram Group\]\([^)]+\)', 'GitHub Issues', line)

        # Replace Visitor Badge with M4Mental badge
        line = re.sub(r'https://visitor-badge\.laobi\.icu/badge\?page_id=[^\"]*', 'https://hits.seeyoufarm.org/api/count/incr/badge.svg?url=https%3A%2F%2Fm4mental.github.io&count_bg=%2306b6d4&title_bg=%231e293b&title=M4Mental+Visitors', line)

        # Replace URLs to m4mental
        line = line.replace("github/stars/nullcpy/rvb", "github/stars/m4mental/my-rvb-builder")
        line = line.replace("github/downloads/nullcpy/rvb", "github/downloads/m4mental/my-rvb-builder")
        line = line.replace("https://github.com/nullcpy/rvb", "https://github.com/m4mental/my-rvb-builder")
        line = line.replace("https://nullcpy.github.io/", "https://m4mental.github.io/")
        line = line.replace("https://nullcpy.github.io", "https://m4mental.github.io/")
        line = line.replace("ReVanced & Morphe Builder", "⚡ M4Mental Hub - ReVanced & Morphe Apps")
        line = line.replace("NullStore", "M4Mental Hub")

        clean_lines.append(line)

    final_content = "".join(clean_lines)
    final_content = re.sub(r'\n{3,}', '\n\n', final_content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(final_content)

    print("==============================================")
    print("SUCCESS: Upstream README.md fully transformed to M4Mental Hub!")
    print("==============================================")

if __name__ == "__main__":
    clean_and_brand_readme()
