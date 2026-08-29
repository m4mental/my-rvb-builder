#!/usr/bin/env python3
import re
import os
import shutil

site_dir = "tmp_site"

custom_css = """
/* ===================================== */
/* M4Mental Hub - Custom Aesthetic Theme */
/* ===================================== */
:root {
  --m4m-primary: #06b6d4;
  --m4m-primary-hover: #22d3ee;
  --m4m-bg-dark: #090d16;
  --m4m-card-bg: rgba(15, 23, 42, 0.75);
  --m4m-border: rgba(51, 65, 85, 0.6);
}

.m4m-p2p-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  border: 1px solid #334155;
  border-radius: 12px;
  width: 42px;
  height: 42px;
  text-decoration: none;
  font-size: 1.25rem;
  cursor: pointer;
  margin-left: 10px;
  transition: all 0.25s ease;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.m4m-p2p-btn:hover {
  transform: translateY(-2px) scale(1.05);
  border-color: #06b6d4;
  box-shadow: 0 0 16px rgba(6, 182, 212, 0.4);
}
"""

def main():
    if not os.path.exists(site_dir):
        print(f"Error: {site_dir} directory not found.")
        return

    # Copy p2p-share.js into tmp_site
    src_p2p = os.path.join(".github", "scripts", "p2p-share.js")
    if os.path.exists(src_p2p):
        shutil.copy(src_p2p, os.path.join(site_dir, "p2p-share.js"))
        print("✓ Copied p2p-share.js into website root")

    for root, dirs, files in os.walk(site_dir):
        if ".git" in root:
            continue
        for file in files:
            if file.endswith((".html", ".js", ".json", ".css")):
                fpath = os.path.join(root, file)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        c = f.read()

                    # Inject PeerJS CDN, p2p-share.js and custom CSS in index.html
                    if file == "index.html":
                        if "p2p-share.js" not in c:
                            c = c.replace("</head>", f'<script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>\n<script src="p2p-share.js"></script>\n<style>{custom_css}</style>\n</head>')

                        # Rebrand Title & Meta
                        c = re.sub(r'<title>.*?</title>', '<title>M4Mental Hub - ReVanced & Morphe Store</title>', c)

                        # Inject P2P Rocket Button in Header / Navbar
                        if "openP2PModal" not in c:
                            p2p_btn = '<a href="javascript:void(0)" onclick="openP2PModal()" class="m4m-p2p-btn" title="⚡ M4M Warp Drop (P2P File Share)" id="p2pWarpBtn">🚀</a>'
                            if 'href="https://github.com/m4mental/my-rvb-builder"' in c:
                                c = re.sub(r'(<a[^>]*href="https://github\.com/m4mental/my-rvb-builder"[^>]*>[\s\S]*?</a>)', r'\1\n' + p2p_btn, c, count=1)
                            elif 'href="https://github.com/nullcpy/rvb"' in c:
                                c = re.sub(r'(<a[^>]*href="https://github\.com/nullcpy/rvb"[^>]*>[\s\S]*?</a>)', r'\1\n' + p2p_btn, c, count=1)
                            else:
                                c = re.sub(r'(</nav>|</header>)', p2p_btn + r'\1', c, count=1)

                    # Remove unwanted external Telegram, Discord, and Donate links
                    c = re.sub(r'<a[^>]*href="https://t\.me/[^"]*"[^>]*>.*?</a>\s*', '', c, flags=re.DOTALL)
                    c = re.sub(r'<a[^>]*t\.me[^>]*>.*?</a>\s*', '', c, flags=re.DOTALL)
                    c = re.sub(r'<a[^>]*href="[^"]*donate[^"]*"[^>]*>.*?</a>\s*', '', c, flags=re.DOTALL)
                    c = re.sub(r'<a[^>]*ko-fi[^>]*>.*?</a>\s*', '', c, flags=re.DOTALL)

                    # Replace ALL Download URLs & Repos to m4mental
                    c = c.replace("https://github.com/nullcpy/rvb/releases/download/", "https://github.com/m4mental/my-rvb-builder/releases/download/")
                    c = c.replace("https://github.com/nullcpy/rvb/releases/tag/", "https://github.com/m4mental/my-rvb-builder/releases/tag/")
                    c = c.replace("https://github.com/nullcpy/rvb/releases", "https://github.com/m4mental/my-rvb-builder/releases")
                    c = c.replace("https://github.com/nullcpy/rvb", "https://github.com/m4mental/my-rvb-builder")
                    c = c.replace("https://api.github.com/repos/nullcpy/rvb", "https://api.github.com/repos/m4mental/my-rvb-builder")

                    c = c.replace("nullcpy/rvb", "m4mental/my-rvb-builder")
                    c = c.replace("nullcpy.github.io", "m4mental.github.io")

                    # Branding replacements
                    c = c.replace("NullStore", "M4Mental Hub")
                    c = c.replace("nullstore", "m4mental store")
                    c = c.replace("ReVanced & Morphe Builder", "M4Mental Hub - ReVanced & Morphe Apps")
                    c = c.replace("RVB Store", "M4Mental Hub")

                    c = c.replace('owner: "nullcpy"', 'owner: "m4mental"')
                    c = c.replace("owner: 'nullcpy'", "owner: 'm4mental'")
                    c = c.replace('repo: "rvb"', 'repo: "my-rvb-builder"')
                    c = c.replace("repo: 'rvb'", "repo: 'my-rvb-builder'")

                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(c)
                    print(f"✓ Processed {file}")
                except Exception as e:
                    print(f"Error processing {file}: {e}")

    print("==============================================")
    print("SUCCESS: M4Mental Hub Website Branded & P2P Engine Built!")
    print("==============================================")

if __name__ == "__main__":
    main()
