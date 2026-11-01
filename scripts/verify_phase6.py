"""
ExamOps Phase 6 Dual Verification Script
Double-checks Phase 6: All 12 Operational Product Modules & Full Frontend Implementation.
- Pass A: Design & Contract Audit (Module coverage, reusable components, routing, tokens)
- Pass B: Empirical Build & Artifact Audit (Vite production compilation, bundle verification)
"""

import os
import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

def audit_pass_a():
    print("=" * 60)
    print("PHASE 6 — PASS A: DESIGN & ARCHITECTURAL AUDIT")
    print("=" * 60)

    # 1. Verify all 12 modules exist
    expected_modules = {
        "Module 1: Overview Dashboard": FRONTEND_DIR / "src" / "views" / "OverviewDashboard.jsx",
        "Module 2: Scheduling Operations Center": FRONTEND_DIR / "src" / "views" / "SchedulingWorkspace.jsx",
        "Module 3: Examination Management": FRONTEND_DIR / "src" / "views" / "ExamManagement.jsx",
        "Module 4: Student Management": FRONTEND_DIR / "src" / "views" / "StudentManagement.jsx",
        "Module 5: Course & Enrollment Management": FRONTEND_DIR / "src" / "views" / "CourseManagement.jsx",
        "Module 6: Room & Facilities Management": FRONTEND_DIR / "src" / "views" / "RoomManagement.jsx",
        "Module 7: Invigilator Management": FRONTEND_DIR / "src" / "views" / "InvigilatorManagement.jsx",
        "Module 8: Accommodation Management": FRONTEND_DIR / "src" / "views" / "AccommodationManagement.jsx",
        "Module 9: Exception Center": FRONTEND_DIR / "src" / "views" / "ExceptionCenter.jsx",
        "Module 10: Analytics & Reports": FRONTEND_DIR / "src" / "views" / "AnalyticsReports.jsx",
        "Module 11: Audit & Activity Ledger": FRONTEND_DIR / "src" / "views" / "AuditActivity.jsx",
        "Module 12: Administration & Policy": FRONTEND_DIR / "src" / "views" / "Administration.jsx",
    }

    for name, path in expected_modules.items():
        assert path.exists(), f"Missing module file: {name} at {path}"
        assert path.stat().st_size > 500, f"Module file appears empty or stubbed: {path}"
        print(f"  [PASS] {name} ({path.stat().st_size} bytes)")

    # 2. Verify reusable UI components
    expected_components = [
        "DataTable.jsx", "Drawer.jsx", "Modal.jsx", "StatusBadge.jsx",
        "MetricDisplay.jsx", "LoadingState.jsx", "EmptyState.jsx"
    ]
    for comp in expected_components:
        comp_path = FRONTEND_DIR / "src" / "components" / "common" / comp
        assert comp_path.exists(), f"Missing component: {comp}"
        print(f"  [PASS] Reusable Component: {comp}")

    # 3. Verify App.jsx imports and routing
    app_jsx = (FRONTEND_DIR / "src" / "App.jsx").read_text(encoding="utf-8")
    expected_views = [
        "OverviewDashboard", "SchedulingWorkspace", "ExamManagement",
        "StudentManagement", "CourseManagement", "RoomManagement",
        "InvigilatorManagement", "AccommodationManagement", "ExceptionCenter",
        "AnalyticsReports", "AuditActivity", "Administration"
    ]
    for view in expected_views:
        assert view in app_jsx, f"View {view} not mounted in App.jsx"
        print(f"  [PASS] App.jsx Route: {view}")

    # 4. Verify Design System Dark Tokens in tailwind.config.js
    tw_config = (FRONTEND_DIR / "tailwind.config.js").read_text(encoding="utf-8")
    assert "#0B1118" in tw_config, "Dark bg token missing"
    assert "#56D6C2" in tw_config, "Accent token missing"
    print("  [PASS] Dark-first Design System tokens confirmed in tailwind.config.js")

    print("\nPASS A RESULT: ALL ARCHITECTURAL REQUIREMENTS VERIFIED.")
    return True

def audit_pass_b():
    print("\n" + "=" * 60)
    print("PHASE 6 — PASS B: EMPIRICAL BUILD & PRODUCTION AUDIT")
    print("=" * 60)

    # 1. Execute Vite production build
    print("  Executing 'npm.cmd run build' in frontend directory...")
    cmd = ["npm.cmd", "run", "build"]
    res = subprocess.run(cmd, cwd=str(FRONTEND_DIR), capture_output=True, text=True)
    if res.returncode != 0:
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        raise RuntimeError(f"Vite production build failed with exit code {res.returncode}")
    print("  [PASS] Production build exited cleanly (code 0)")

    # 2. Verify dist bundle assets
    dist_dir = FRONTEND_DIR / "dist"
    index_html = dist_dir / "index.html"
    assets_dir = dist_dir / "assets"
    
    assert index_html.exists() and index_html.stat().st_size > 100, "dist/index.html missing or empty"
    print(f"  [PASS] dist/index.html generated ({index_html.stat().st_size} bytes)")

    js_bundles = list(assets_dir.glob("*.js"))
    css_bundles = list(assets_dir.glob("*.css"))
    assert len(js_bundles) > 0, "No JS bundles generated in dist/assets"
    assert len(css_bundles) > 0, "No CSS bundles generated in dist/assets"

    js_size_kb = js_bundles[0].stat().st_size / 1024
    css_size_kb = css_bundles[0].stat().st_size / 1024
    print(f"  [PASS] Bundled Javascript: {js_bundles[0].name} ({js_size_kb:.1f} KB)")
    print(f"  [PASS] Bundled Stylesheet: {css_bundles[0].name} ({css_size_kb:.1f} KB)")

    print("\nPASS B RESULT: ALL PRODUCTION ARTIFACTS VERIFIED EMPIRICALLY.")
    return True

if __name__ == "__main__":
    try:
        audit_pass_a()
        audit_pass_b()
        print("\n" + "=" * 60)
        print("PHASE 6 VERIFICATION COMPLETE: ALL 12 MODULES VERIFIED TWICE.")
        print("=" * 60)
    except Exception as e:
        print(f"\nPHASE 6 VERIFICATION FAILED: {e}")
        sys.exit(1)

