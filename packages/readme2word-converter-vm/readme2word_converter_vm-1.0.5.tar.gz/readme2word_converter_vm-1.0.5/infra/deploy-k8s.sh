#!/bin/bash

# README to Word Converter - Kubernetes Deployment Script
# This script deploys the application to a local Kubernetes cluster using Helm

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="readme2word"
RELEASE_NAME="readme2word"
CHART_PATH="./helm/readme2word"
VALUES_FILE="./helm/readme2word/values.yaml"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        print_error "Helm is not installed. Please install Helm first."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Kubernetes cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    print_success "All prerequisites are met!"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    
    cd ..
    docker build -t readme2word:latest .
    cd infra
    
    print_success "Docker image built successfully!"
}

# Function to create namespace
create_namespace() {
    print_status "Creating namespace: $NAMESPACE"
    
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        print_warning "Namespace $NAMESPACE already exists"
    else
        kubectl create namespace $NAMESPACE
        print_success "Namespace $NAMESPACE created"
    fi
}

# Function to deploy with Helm
deploy_helm() {
    print_status "Deploying with Helm..."
    
    # Add any required Helm repositories
    # helm repo add stable https://charts.helm.sh/stable
    # helm repo update
    
    # Install or upgrade the release
    helm upgrade --install $RELEASE_NAME $CHART_PATH \
        --namespace $NAMESPACE \
        --values $VALUES_FILE \
        --wait \
        --timeout 10m
    
    print_success "Application deployed successfully!"
}

# Function to check deployment status
check_deployment() {
    print_status "Checking deployment status..."
    
    # Wait for deployment to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/$RELEASE_NAME -n $NAMESPACE
    
    # Get pod status
    kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=readme2word
    
    # Get service information
    kubectl get svc -n $NAMESPACE
    
    print_success "Deployment is ready!"
}

# Function to setup ingress (for local development)
setup_local_ingress() {
    print_status "Setting up local ingress..."
    
    # Check if nginx ingress controller is installed
    if ! kubectl get ingressclass nginx &> /dev/null; then
        print_warning "NGINX Ingress Controller not found. Installing..."
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
        
        # Wait for ingress controller to be ready
        kubectl wait --namespace ingress-nginx \
            --for=condition=ready pod \
            --selector=app.kubernetes.io/component=controller \
            --timeout=300s
    fi
    
    # Add entry to /etc/hosts (requires sudo)
    if ! grep -q "readme2word.local" /etc/hosts; then
        print_status "Adding entry to /etc/hosts (requires sudo)..."
        echo "127.0.0.1 readme2word.local" | sudo tee -a /etc/hosts
    fi
    
    print_success "Local ingress setup complete!"
}

# Function to get access information
get_access_info() {
    print_status "Getting access information..."
    
    echo ""
    echo "🎉 Deployment Complete!"
    echo "===================="
    echo ""
    
    # Get ingress information
    if kubectl get ingress -n $NAMESPACE &> /dev/null; then
        echo "🌐 Application URL: http://readme2word.local"
        echo ""
        echo "📝 Note: Make sure you have an ingress controller running"
        echo "   and 'readme2word.local' in your /etc/hosts file"
    fi
    
    # Get service information for port-forward alternative
    echo "🔗 Alternative access (port-forward):"
    echo "   kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME 8501:8501"
    echo "   Then access: http://localhost:8501"
    echo ""
    
    # Useful commands
    echo "📋 Useful commands:"
    echo "   View pods:    kubectl get pods -n $NAMESPACE"
    echo "   View logs:    kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=readme2word"
    echo "   Delete app:   helm uninstall $RELEASE_NAME -n $NAMESPACE"
    echo ""
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up deployment..."
    
    helm uninstall $RELEASE_NAME -n $NAMESPACE || true
    kubectl delete namespace $NAMESPACE || true
    
    print_success "Cleanup complete!"
}

# Main deployment function
deploy() {
    print_status "Starting deployment of README to Word Converter..."
    
    check_prerequisites
    build_image
    create_namespace
    deploy_helm
    check_deployment
    setup_local_ingress
    get_access_info
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "cleanup")
        cleanup
        ;;
    "build")
        build_image
        ;;
    "status")
        check_deployment
        ;;
    "logs")
        kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=readme2word --tail=100 -f
        ;;
    "shell")
        POD=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=readme2word -o jsonpath='{.items[0].metadata.name}')
        kubectl exec -it $POD -n $NAMESPACE -- /bin/bash
        ;;
    *)
        echo "Usage: $0 {deploy|cleanup|build|status|logs|shell}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the application (default)"
        echo "  cleanup  - Remove the application and namespace"
        echo "  build    - Build Docker image only"
        echo "  status   - Check deployment status"
        echo "  logs     - View application logs"
        echo "  shell    - Open shell in running pod"
        exit 1
        ;;
esac 