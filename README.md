# DevTools-CLI 🛠️

**DevOps Templates \u0026 Quality Automation CLI for Ecosystem-1**

[![CI](https://github.com/gerivdb/DevTools-CLI/actions/workflows/ci.yml/badge.svg)](https://github.com/gerivdb/DevTools-CLI/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 👁️ Overview

DevTools-CLI fournit templates DevOps prêt-à-l'emploi et outils automation pour:
- 🔄 CI/CD Pipelines (GitHub Actions, GitLab CI)
- 🐳 Docker Containers (Dockerfile multi-stage, Docker Compose)
- ☸️ Kubernetes Manifests (Deployments, Services, Ingress)
- 🏗️ Terraform IaC (AWS, Azure, GCP modules)

## 🚀 Quick Start

### Installation
```bash
pip install devtools-cli
# ou depuis le code source:
git clone https://github.com/gerivdb/DevTools-CLI.git
cd DevTools-CLI
pip install -e .
```

### Usage
```bash
# Lister templates disponibles
devtools template list

# Voir détails template
devtools template show github-actions-ci

# Initialiser template avec variables
devtools template init github-actions-ci \
  --var PYTHON_VERSION=3.11 \
  --var RUN_TESTS=true \
  --var RUN_LINT=true

# Filter par catégorie
devtools template list --category=docker
```

## 📦 Templates Disponibles

### CI/CD Pipelines
- `github-actions-ci` - Pipeline CI complet (lint, test, coverage)
- `github-actions-release` - Release automation avec semantic versioning

### Docker
- `python-fastapi` - Dockerfile FastAPI multi-stage production-ready
- `compose-stack` - Docker Compose stack (app + DB + cache)

### Kubernetes
- `k8s-deployment` - Deployment avec health checks et resource limits
- `k8s-service` - Service (ClusterIP ou LoadBalancer)

### Terraform
- `terraform-aws-vpc` - VPC AWS avec subnets public/private

## 🔗 Integration ECOS CLI

DevTools-CLI s'intègre via ECOS CLI Gateway:
```bash
ecos delegate devtools template list
```

## 📚 Documentation

Voir [docs/](docs/) pour:
- Guide utilisation templates
- Création templates custom
- Intégration CI/CD
- Best practices DevOps

## 🤝 Contribution

Voir [CONTRIBUTING.md](CONTRIBUTING.md)

## 📢 License

MIT - voir [LICENSE](LICENSE)