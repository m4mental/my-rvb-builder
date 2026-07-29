import re
import os

def clean_readme(file_path="README.md"):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove Palestine Banner
    content = re.sub(r'<div align="center"><a href="https://github.com/Safouene1/support-palestine-banner.*?</div>\s*', '', content, flags=re.DOTALL)

    # 2. Remove Telegram Group, Channel, Donate badges
    content = re.sub(r'<a href="https://t.me/[^"]*"><img src="[^"]*badge/Group-[^"]*"></a>\s*', '', content)
    content = re.sub(r'<a href="https://t.me/[^"]*"><img src="[^"]*badge/Channel-[^"]*"></a>\s*', '', content)
    content = re.sub(r'<a href="[^"]*donate[^"]*"><img src="[^"]*badge/Donate-[^"]*"></a>\s*', '', content)
    content = re.sub(r'\|[[:space:]]*\[Group\]\([^)]+\)', '', content)
    content = re.sub(r'\|[[:space:]]*\[Donate\]\([^)]+\)', '', content)

    # 3. Remove "Support the Project" section
    content = re.sub(r'## 🤝 Support the Project.*?(?=---|\Z)', '', content, flags=re.DOTALL)

    # 4. Remove Telegram references in Note section
    content = re.sub(r'or \*\*\[send a message in our Telegram Group\]\([^)]+\)\*\*', '', content)
    content = re.sub(r'\*\*\[Send a message in our Telegram Group\]\([^)]+\)\*\* or ', '', content)

    # 5. Replace GitHub & Website links with m4mental links
    content = content.replace("https://github.com/nullcpy/rvb", "https://github.com/m4mental/my-rvb-builder")
    content = content.replace("https://nullcpy.github.io/", "https://m4mental.github.io/my-rvb-builder/")
    content = content.replace("https://nullcpy.github.io", "https://m4mental.github.io/my-rvb-builder")
    content = content.replace("nullcpy.rvb", "m4mental.my-rvb-builder")
    content = content.replace("nullcpy.github.io", "m4mental.github.io.my-rvb-builder")

    # 6. Clean multiple blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✓ README.md successfully cleaned for m4mental!")

if __name__ == "__main__":
    clean_readme()
