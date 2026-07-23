# Kubernetes / Infrastructure Manifests

This directory will contain Kubernetes deployment manifests, Helm charts,
and infrastructure-as-code resources added in Phase 7.

Expected structure:

```
infrastructure/
├── helm/
│   └── cortex-gateway/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── ingress.yaml
│           ├── hpa.yaml
│           └── configmap.yaml
├── terraform/          # Cloud provider infrastructure (Phase 7+)
└── k8s/                # Raw Kubernetes manifests (alternative to Helm)
```
