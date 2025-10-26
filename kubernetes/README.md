# Pulsai Kubernetes Deployment

Complete Kubernetes manifests for deploying Pulsai in production.

## Prerequisites

- **Kubernetes cluster** 1.28+ (EKS, GKE, AKS, or on-prem)
- **kubectl** configured to access your cluster
- **Helm** 3+ (for cert-manager and ingress-nginx)
- **Storage provisioner** (for PersistentVolumes)
- Optional: **GPU support** for Ollama (NVIDIA device plugin)

---

## Quick Start

### 1. Install Required Controllers

```bash
# Install cert-manager (for TLS certificates)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.metrics.enabled=true
```

### 2. Configure Secrets

```bash
# Generate secrets
export SECRET_KEY=$(openssl rand -hex 32)
export POSTGRES_PASSWORD=$(openssl rand -hex 32)
export MCP_TOKEN=$(openssl rand -hex 32)
export SESSION_SECRET=$(openssl rand -hex 32)

# Create secrets
kubectl create secret generic pulsai-secrets \
  --from-literal=SECRET_KEY=$SECRET_KEY \
  --from-literal=POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  --from-literal=MCP_AUTH_TOKEN=$MCP_TOKEN \
  --from-literal=SESSION_SECRET=$SESSION_SECRET \
  --namespace=pulsai \
  --dry-run=client -o yaml > /tmp/pulsai-secrets.yaml

# Apply
kubectl apply -f /tmp/pulsai-secrets.yaml
rm /tmp/pulsai-secrets.yaml  # Clean up
```

### 3. Update Configuration

Edit `kubernetes/pulsai/ingress.yaml`:
- Replace `pulsai.your-domain.com` with your domain
- Update `admin@your-domain.com` with your email

### 4. Deploy Pulsai

```bash
# Using kubectl
kubectl apply -k kubernetes/pulsai/

# Or apply files individually
kubectl apply -f kubernetes/pulsai/namespace.yaml
kubectl apply -f kubernetes/pulsai/configmap.yaml
kubectl apply -f kubernetes/pulsai/secrets.yaml
kubectl apply -f kubernetes/pulsai/postgres-statefulset.yaml
kubectl apply -f kubernetes/pulsai/redis-deployment.yaml
kubectl apply -f kubernetes/pulsai/chroma-deployment.yaml
kubectl apply -f kubernetes/pulsai/ollama-statefulset.yaml
kubectl apply -f kubernetes/pulsai/backend-deployment.yaml
kubectl apply -f kubernetes/pulsai/frontend-deployment.yaml
kubectl apply -f kubernetes/pulsai/ingress.yaml
kubectl apply -f kubernetes/pulsai/hpa.yaml
kubectl apply -f kubernetes/pulsai/network-policies.yaml
```

### 5. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n pulsai

# Check services
kubectl get svc -n pulsai

# Check ingress
kubectl get ingress -n pulsai

# View logs
kubectl logs -f -l app=pulsai-backend -n pulsai
```

### 6. Access Pulsai

```bash
# Get external IP
kubectl get ingress pulsai-ingress -n pulsai

# Access at: https://pulsai.your-domain.com
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Ingress (NGINX)                  │
│            https://pulsai.your-domain.com          │
└──────────────┬──────────────┬─────────────────────┘
               │              │
       ┌───────▼────┐  ┌──────▼────┐
       │  Frontend  │  │  Backend  │
       │  (2 pods)  │  │  (2-10    │
       │            │  │  pods HPA)│
       └────────────┘  └─────┬─────┘
                             │
        ┌────────────────────┼────────────────┐
        │                    │                │
    ┌───▼────┐    ┌──────────▼──┐    ┌──────▼────┐
    │Postgres│    │   Redis     │    │  Ollama   │
    │(StatefulSet) │   (1 pod)   │    │(StatefulSet)
    └────────┘    └─────────────┘    └───────────┘
                           │
                    ┌──────▼────┐
                    │  Chroma   │
                    │  (1 pod)  │
                    └───────────┘
```

---

## Customization

### Resource Limits

Edit deployment files to adjust CPU/memory:

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment pulsai-backend --replicas=5 -n pulsai

# Autoscaling (already configured via HPA)
kubectl get hpa -n pulsai
```

### Storage Classes

Update `storageClassName` in StatefulSets/PVCs:

- **AWS EKS**: `gp3` or `ebs-sc`
- **GCP GKE**: `standard` or `premium-rwo`
- **Azure AKS**: `managed-csi`
- **On-prem**: `local-path` or your custom storage class

### GPU Support for Ollama

1. Install NVIDIA device plugin:
```bash
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/master/nvidia-device-plugin.yml
```

2. Uncomment GPU resources in `ollama-statefulset.yaml`:
```yaml
resources:
  limits:
    nvidia.com/gpu: "1"
```

3. Add node selector:
```yaml
nodeSelector:
  nvidia.com/gpu: "true"
```

---

## Cloud Provider Configurations

### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name pulsai-cluster \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.large \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed

# Install AWS Load Balancer Controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=pulsai-cluster

# Update ingress.yaml for ALB:
# kubernetes.io/ingress.class: "alb"
# alb.ingress.kubernetes.io/scheme: "internet-facing"
```

### GCP GKE

```bash
# Create GKE cluster
gcloud container clusters create pulsai-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 5

# Get credentials
gcloud container clusters get-credentials pulsai-cluster --zone us-central1-a
```

### Azure AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group pulsai-rg \
  --name pulsai-cluster \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group pulsai-rg --name pulsai-cluster
```

---

## Monitoring

### Prometheus & Grafana

```bash
# Install kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
# Default credentials: admin / prom-operator
```

### Logs with Loki

```bash
# Install Loki stack
helm install loki grafana/loki-stack \
  --namespace logging \
  --create-namespace \
  --set grafana.enabled=true
```

---

## Backup & Disaster Recovery

### Postgres Backups

```bash
# Create backup CronJob
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: pulsai
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres -U pulsai pulsai > /backup/pulsai-\$(date +%Y%m%d).sql
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: pulsai-secrets
                  key: POSTGRES_PASSWORD
            volumeMounts:
            - name: backup
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup
            persistentVolumeClaim:
              claimName: postgres-backup
EOF
```

### Velero (Cluster Backups)

```bash
# Install Velero
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket pulsai-backups \
  --backup-location-config region=us-west-2 \
  --snapshot-location-config region=us-west-2

# Create backup
velero backup create pulsai-backup --include-namespaces pulsai

# Restore
velero restore create --from-backup pulsai-backup
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check events
kubectl get events -n pulsai --sort-by='.lastTimestamp'

# Describe pod
kubectl describe pod <pod-name> -n pulsai

# Check logs
kubectl logs <pod-name> -n pulsai
```

### Database Connection Issues

```bash
# Test connection
kubectl run -it --rm debug --image=postgres:16-alpine --restart=Never -n pulsai -- \
  psql -h postgres -U pulsai -d pulsai

# Check postgres logs
kubectl logs -f statefulset/postgres -n pulsai
```

### Ingress Not Working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check certificate
kubectl get certificate -n pulsai
kubectl describe certificate pulsai-tls-cert -n pulsai

# Test without TLS
curl -v http://<EXTERNAL-IP> -H "Host: pulsai.your-domain.com"
```

---

## Uninstall

```bash
# Delete all resources
kubectl delete -k kubernetes/pulsai/

# Or delete namespace (removes everything)
kubectl delete namespace pulsai
```

---

## Next Steps

1. **Set up monitoring** with Prometheus/Grafana
2. **Configure backups** with Velero or cloud-native solutions
3. **Enable GPU** for Ollama if available
4. **Set up CI/CD** for automated deployments
5. **Configure autoscaling** based on your workload

For more information, see [docs/DEPLOYMENT.md](../../docs/DEPLOYMENT.md)

---

**Last Updated:** 19 octobre 2025  
**Version:** 1.0.0  
**Author:** Pulsai Team

