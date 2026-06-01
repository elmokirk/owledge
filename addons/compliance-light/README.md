# Compliance Light Add-on

Optional compliance-support layer for the Agent Memory Kit.

This add-on is intentionally not part of the default minimal project kit. Install
it only when a project needs lightweight governance evidence for customer data,
personal data, external AI providers, shared exports, or AI-risk review.

It provides Markdown templates, a read-only compliance doctor, and a combined
compliance gate. It does not provide legal advice, certification, RBAC,
encryption, automatic deletion, or a secure MCP/API access layer.

## Install Into A Project

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\addons\compliance-light\install-compliance-layer.ps1 -ProjectRoot .
```

## Commands After Install

```powershell
tools\compliance-doctor.ps1 -ProjectRoot .
tools\run-compliance-gates.ps1 -ProjectRoot .
```

## Build A Project Folder With Compliance Support

```powershell
tools\build-project-folder-kit.ps1 -OutputPath C:\tmp\agent-memory-project-kit-compliance -Verify -IncludeCompliance
```
