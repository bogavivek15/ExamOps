"""
ExamOps Autopilot — Phase 5 Verification Suite
Executes Pass A (Design System & Reusable Components Audit) and Pass B (Empirical Build & Bundle Audit)
for the React + Vite Frontend Foundation.
"""
import sys
import os
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

def run_pass_a():
    print("\n========================================================")
    print("  PASS A: DESIGN SYSTEM & COMPONENT ARCHITECTURE AUDIT")
    print("========================================================")

    # 1. Verify Design System Palette Tokens in tailwind.config.js
    with open("frontend/tailwind.config.js", "r", encoding="utf-8") as f:
        tw_content = f.read()
    
    required_tokens = [
        "#0B1118", # bg
        "#0E151D", # sidebar
        "#121C26", # surface
        "#172330", # elevated
        "#263442", # border
        "#56D6C2", # accent
        "#57BE93", # success
        "#E8B66D", # warning
        "#E87979", # danger
        "#7CAAE5", # info
    ]
    for token in required_tokens:
        assert token.lower() in tw_content.lower(), f"Missing design token {token} in tailwind.config.js"
        print(f"  ✓ Verified design system token: {token}")

    # 2. Verify Reusable Component System files
    required_components = [
        "frontend/src/components/layout/AppSidebar.jsx",
        "frontend/src/components/layout/TopNavigation.jsx",
        "frontend/src/components/layout/AppLayout.jsx",
        "frontend/src/components/common/DataTable.jsx",
        "frontend/src/components/common/StatusBadge.jsx",
        "frontend/src/components/common/MetricDisplay.jsx",
        "frontend/src/components/common/Modal.jsx",
        "frontend/src/components/common/Drawer.jsx",
        "frontend/src/components/common/LoadingState.jsx",
        "frontend/src/components/common/EmptyState.jsx",
        "frontend/src/services/api.js",
        "frontend/src/context/AuthContext.jsx",
    ]
    for comp in required_components:
        assert os.path.exists(comp), f"Required component missing: {comp}"
        print(f"  ✓ Verified component contract: {comp}")

    # 3. Verify technology constraints
    with open("frontend/package.json", "r", encoding="utf-8") as f:
        pkg_content = f.read().lower()
    
    forbidden = ["redux", "next", "mobx", "formik", "typescript", "angular", "vue"]
    for fb in forbidden:
        assert fb not in pkg_content, f"Forbidden frontend package detected: {fb}"
    print("  ✓ Technology restrictions verified: 0 forbidden frontend dependencies detected.")

    print("\n  PASS A: ALL FRONTEND ARCHITECTURAL CONTRACTS CERTIFIED SATISFIED.")

def run_pass_b():
    print("\n========================================================")
    print("  PASS B: EMPIRICAL BUILD & PRODUCTION ARTIFACT AUDIT")
    print("========================================================")

    # 1. Run Vite production build
    res = subprocess.run(
        ["cmd.exe", "/c", "npm.cmd", "run", "build"],
        cwd="frontend",
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Vite build failed:\n{res.stderr}"
    print("  ✓ Vite Production Build: Completed with returncode 0.")

    # 2. Inspect generated dist artifacts
    dist_dir = "frontend/dist"
    assert os.path.exists(dist_dir), "dist directory does not exist!"
    assert os.path.exists(os.path.join(dist_dir, "index.html")), "dist/index.html is missing!"
    
    assets_dir = os.path.join(dist_dir, "assets")
    assert os.path.exists(assets_dir), "dist/assets is missing!"
    asset_files = os.listdir(assets_dir)
    js_files = [f for f in asset_files if f.endswith(".js")]
    css_files = [f for f in asset_files if f.endswith(".css")]

    assert len(js_files) > 0, "No compiled JS bundle found in dist/assets!"
    assert len(css_files) > 0, "No compiled CSS bundle found in dist/assets!"
    print(f"  ✓ Production Bundles Verified: {len(js_files)} JS chunk(s), {len(css_files)} CSS chunk(s).")

    print("\n  PASS B: ALL EMPIRICAL BUILD TESTS PASSED.")

if __name__ == "__main__":
    run_pass_a()
    run_pass_b()
    print("\n========================================================")
    print("  PHASE 5 EXIT GATE: OFFICIALLY CERTIFIED AND PASSED!")
    print("========================================================\n")

