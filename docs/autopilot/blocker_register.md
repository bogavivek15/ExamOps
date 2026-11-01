# ExamOps Autopilot — Blocker Register

> **Document**: Autopilot Blocker and External Dependency Register  
> **System**: ExamOps Autonomous Engineering Engine  
> **Last Updated**: 2026-11-01T17:58:00+05:30  

---

## Active Blockers

*None. All components are executing autonomously using local tooling and environment.*

---

## Resolved Blockers

| Blocker ID | Date | Description | Resolution Strategy | Status |
|---|---|---|---|---|
| `BLK-001` | 2026-11-01 | PowerShell execution policy restricts `.ps1` wrapper execution for `npm` | Use `npm.cmd` and `npx.cmd` directly for all Node and Supabase CLI commands | RESOLVED |
