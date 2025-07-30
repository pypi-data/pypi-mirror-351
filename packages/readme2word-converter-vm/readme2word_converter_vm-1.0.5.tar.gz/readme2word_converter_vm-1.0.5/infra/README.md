# Kubernetes Infrastructure for README to Word Converter

This directory contains Kubernetes deployment manifests and Helm charts for deploying the README to Word Converter application on your local Kubernetes cluster.

## 📁 Directory Structure

```
infra/
├── README.md                    # This documentation
├── deploy-k8s.sh               # Automated deployment script
└── helm/
    └── readme2word/            # Helm chart
        ├── Chart.yaml          # Chart metadata
        ├── values.yaml         # Configuration values
        └── templates/          # Kubernetes manifests
            ├── _helpers.tpl    # Template helpers
            ├── deployment.yaml # Application deployment
            ├── service.yaml    # Service definition
            ├── ingress.yaml    # Ingress for external access
            ├── configmap.yaml  # Configuration
            ├── pvc.yaml        # Persistent storage
            ├── serviceaccount.yaml # Service account
            ├── hpa.yaml        # Horizontal Pod Autoscaler
            ├── pdb.yaml        # Pod Disruption Budget
            └── networkpolicy.yaml # Network security
```

## 🚀 Quick Start

### Prerequisites

1. **Local Kubernetes Cluster** (one of the following):
   - Docker Desktop with Kubernetes enabled
   - Minikube
   - Kind (Kubernetes in Docker)
   - K3s/K3d

2. **Required Tools**:
   ```bash
   # Install kubectl
   brew install kubectl  # macOS
   # or download from https://kubernetes.io/docs/tasks/tools/
   
   # Install Helm
   brew install helm      # macOS
   # or download from https://helm.sh/docs/intro/install/
   ```

3. **Verify Setup**:
   ```bash
   kubectl cluster-info
   helm version
   ```

### One-Command Deployment

```bash
# Navigate to infra directory
cd infra

# Deploy everything
./deploy-k8s.sh
```

This script will:
- ✅ Check all prerequisites
- ✅ Build the Docker image
- ✅ Create Kubernetes namespace
- ✅ Deploy using Helm
- ✅ Setup ingress controller (if needed)
- ✅ Configure local DNS
- ✅ Provide access information

## 🛠️ Manual Deployment

If you prefer manual deployment:

### 1. Build Docker Image

```bash
# From project root
docker build -t readme2word:latest .
```

### 2. Create Namespace

```bash
kubectl create namespace readme2word
```

### 3. Deploy with Helm

```bash
# Install the application
helm install readme2word ./helm/readme2word \
  --namespace readme2word \
  --wait

# Or upgrade existing deployment
helm upgrade readme2word ./helm/readme2word \
  --namespace readme2word \
  --wait
```

### 4. Setup Ingress (Optional)

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Add to /etc/hosts
echo "127.0.0.1 readme2word.local" | sudo tee -a /etc/hosts
```

## 🌐 Accessing the Application

### Option 1: Ingress (Recommended)

After deployment, access the application at:
- **URL**: http://readme2word.local
- **Note**: Requires ingress controller and /etc/hosts entry

### Option 2: Port Forward

```bash
kubectl port-forward -n readme2word svc/readme2word 8501:8501
```
Then access: http://localhost:8501

### Option 3: NodePort (for external clusters)

Modify `values.yaml`:
```yaml
service:
  type: NodePort
  port: 8501
  nodePort: 30080
```

Then access: http://<node-ip>:30080

## ⚙️ Configuration

### Helm Values

Key configuration options in `values.yaml`:

#### **Scaling & Resources**
```yaml
replicaCount: 2

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

#### **Storage**
```yaml
persistence:
  enabled: true
  size: 5Gi
  storageClass: ""  # Use default storage class
```

#### **Ingress**
```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: readme2word.local
      paths:
        - path: /
          pathType: Prefix
```

#### **Security**
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false

networkPolicy:
  enabled: false  # Enable for network isolation
```

### Environment-Specific Values

Create custom values files for different environments:

```bash
# Development
helm install readme2word ./helm/readme2word \
  --values ./helm/readme2word/values.yaml \
  --values ./values-dev.yaml

# Production
helm install readme2word ./helm/readme2word \
  --values ./helm/readme2word/values.yaml \
  --values ./values-prod.yaml
```

## 📊 Monitoring & Operations

### View Application Status

```bash
# Check pods
kubectl get pods -n readme2word

# Check services
kubectl get svc -n readme2word

# Check ingress
kubectl get ingress -n readme2word

# View events
kubectl get events -n readme2word --sort-by='.lastTimestamp'
```

### View Logs

```bash
# All pods
kubectl logs -n readme2word -l app.kubernetes.io/name=readme2word

# Specific pod
kubectl logs -n readme2word <pod-name>

# Follow logs
kubectl logs -n readme2word -l app.kubernetes.io/name=readme2word -f
```

### Access Pod Shell

```bash
# Get pod name
kubectl get pods -n readme2word

# Access shell
kubectl exec -it <pod-name> -n readme2word -- /bin/bash
```

### Helm Operations

```bash
# List releases
helm list -n readme2word

# Get values
helm get values readme2word -n readme2word

# Upgrade
helm upgrade readme2word ./helm/readme2word -n readme2word

# Rollback
helm rollback readme2word 1 -n readme2word

# Uninstall
helm uninstall readme2word -n readme2word
```

## 🔧 Troubleshooting

### Common Issues

#### **Pods Not Starting**
```bash
# Check pod status
kubectl describe pod <pod-name> -n readme2word

# Check events
kubectl get events -n readme2word --sort-by='.lastTimestamp'

# Common causes:
# - Image pull errors
# - Resource constraints
# - Configuration issues
```

#### **Service Not Accessible**
```bash
# Check service endpoints
kubectl get endpoints -n readme2word

# Test service connectivity
kubectl run test-pod --image=busybox -it --rm -- wget -qO- http://readme2word.readme2word.svc.cluster.local:8501
```

#### **Ingress Not Working**
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress status
kubectl describe ingress readme2word -n readme2word

# Verify /etc/hosts entry
grep readme2word.local /etc/hosts
```

#### **Storage Issues**
```bash
# Check PVC status
kubectl get pvc -n readme2word

# Check storage class
kubectl get storageclass

# Check persistent volumes
kubectl get pv
```

### Debug Commands

```bash
# Port forward for direct access
kubectl port-forward -n readme2word svc/readme2word 8501:8501

# Run debug pod
kubectl run debug --image=busybox -it --rm -n readme2word -- sh

# Check DNS resolution
kubectl run dns-test --image=busybox -it --rm -- nslookup readme2word.readme2word.svc.cluster.local
```

## 🔒 Security Considerations

### Network Policies

Enable network policies for production:

```yaml
networkPolicy:
  enabled: true
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8501
  egress:
    - to: []
      ports:
        - protocol: TCP
          port: 443  # HTTPS for Mermaid API
```

### Pod Security

The deployment includes security best practices:
- Non-root user execution
- Read-only root filesystem (where possible)
- Dropped capabilities
- Security context constraints

### RBAC

Service account with minimal permissions:
```yaml
serviceAccount:
  create: true
  annotations: {}
```

## 📈 Scaling & Performance

### Horizontal Pod Autoscaler

Automatic scaling based on CPU/Memory:
```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80
```

### Resource Optimization

Tune resources based on usage:
```yaml
resources:
  requests:
    cpu: 250m      # Minimum guaranteed
    memory: 256Mi
  limits:
    cpu: 1000m     # Maximum allowed
    memory: 1Gi
```

### Storage Performance

For better I/O performance:
```yaml
persistence:
  storageClass: "fast-ssd"  # Use SSD storage class
  size: 10Gi
```

## 🚀 Advanced Deployment Options

### Multi-Environment Setup

```bash
# Development
helm install readme2word-dev ./helm/readme2word \
  --namespace readme2word-dev \
  --set image.tag=dev \
  --set replicaCount=1

# Staging
helm install readme2word-staging ./helm/readme2word \
  --namespace readme2word-staging \
  --set image.tag=staging \
  --set ingress.hosts[0].host=readme2word-staging.local

# Production
helm install readme2word-prod ./helm/readme2word \
  --namespace readme2word-prod \
  --set image.tag=v1.0.0 \
  --set replicaCount=3 \
  --set resources.requests.cpu=500m
```

### Blue-Green Deployment

```bash
# Deploy green version
helm install readme2word-green ./helm/readme2word \
  --namespace readme2word \
  --set nameOverride=readme2word-green

# Switch traffic (update ingress)
kubectl patch ingress readme2word -n readme2word \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/rules/0/http/paths/0/backend/service/name", "value": "readme2word-green"}]'

# Remove blue version
helm uninstall readme2word-blue -n readme2word
```

## 📋 Deployment Checklist

Before deploying to production:

- [ ] **Security**: Enable network policies
- [ ] **Monitoring**: Setup metrics and alerting
- [ ] **Backup**: Configure persistent volume backups
- [ ] **Resources**: Set appropriate limits and requests
- [ ] **Scaling**: Configure HPA based on load testing
- [ ] **DNS**: Setup proper domain names
- [ ] **TLS**: Configure SSL certificates
- [ ] **Logging**: Setup log aggregation
- [ ] **Health Checks**: Verify liveness and readiness probes

## 🆘 Support

For issues with Kubernetes deployment:

1. Check the troubleshooting section above
2. Review Kubernetes and Helm documentation
3. Check application logs for specific errors
4. Verify cluster resources and permissions

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

---

**Ready to deploy?** 🚀

```bash
cd infra && ./deploy-k8s.sh
``` 