# 🛠️ DevOps Toolkit (`dtk`)

[![CI](https://github.com/donny-devops/devops-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/donny-devops/devops-toolkit/actions)
[![Coverage](https://img.shields.io/codecov/c/github/donny-devops/devops-toolkit?style=flat-square)](https://codecov.io/gh/donny-devops/devops-toolkit)
[![Release](https://img.shields.io/github/v/release/donny-devops/devops-toolkit?style=flat-square)](https://github.com/donny-devops/devops-toolkit/releases)
[![License](https://img.shields.io/github/license/donny-devops/devops-toolkit?style=flat-square)](LICENSE)

> Swiss-army CLI for cloud health checks, automated log parsing, cluster triage, and Kubernetes/AWS resource auditing.

---

## 🏛️ Architecture

```mermaid
flowchart LR
    CLI[dtk CLI Interface] --> Router{Command Router}
    Router --> Doctor[Health & Doctor Module]
    Router --> LogParser[Log & Anomaly Parser]
    Router --> ClusterAudit[K8s / AWS IAM Auditor]

    Doctor --> Target[(Cluster / Cloud Target)]
    LogParser --> Target
    ClusterAudit --> Target
```

---

## ⚡ Quickstart

```bash
# 1. Download & Install CLI
curl -fsSL https://raw.githubusercontent.com/donny-devops/devops-toolkit/main/install.sh | bash

# 2. Configure Credentials (Uses standard AWS/Kube context)
dtk config init

# 3. Run Full System Diagnostic
dtk doctor --all
```

---

## Features

- **Automated Health Checks**: One-command cluster diagnostics (`dtk doctor`).
- **Log Anomaly Detection**: High-speed log analysis for fatal errors, OOMs, and stack traces.
- **Resource Auditing**: Scans Kubernetes pods, deployments, and AWS IAM roles for security misconfigurations.
- **Cross-Platform**: Zero-dependency standalone binary for Linux, macOS, and Windows.

## License

MIT © Adonis Jimenez
