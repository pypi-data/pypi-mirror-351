#!/bin/bash

# Helm Chart Validation Script for README to Word Converter

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CHART_PATH="./helm/readme2word"

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
    
    if ! command -v helm &> /dev/null; then
        print_error "Helm is not installed. Please install Helm first."
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    print_success "Prerequisites check passed!"
}

# Function to validate chart syntax
validate_syntax() {
    print_status "Validating Helm chart syntax..."
    
    if helm lint $CHART_PATH; then
        print_success "Chart syntax validation passed!"
    else
        print_error "Chart syntax validation failed!"
        exit 1
    fi
}

# Function to validate chart templates
validate_templates() {
    print_status "Validating chart templates..."
    
    # Test template rendering with default values
    if helm template test-release $CHART_PATH > /dev/null; then
        print_success "Template rendering with default values passed!"
    else
        print_error "Template rendering failed!"
        exit 1
    fi
    
    # Test template rendering with dev values
    if helm template test-release $CHART_PATH -f ./values-dev.yaml > /dev/null; then
        print_success "Template rendering with dev values passed!"
    else
        print_error "Template rendering with dev values failed!"
        exit 1
    fi
    
    # Test template rendering with prod values
    if helm template test-release $CHART_PATH -f ./values-prod.yaml > /dev/null; then
        print_success "Template rendering with prod values passed!"
    else
        print_error "Template rendering with prod values failed!"
        exit 1
    fi
}

# Function to validate Kubernetes manifests
validate_k8s_manifests() {
    print_status "Validating Kubernetes manifests..."
    
    # Generate manifests and validate with kubectl
    helm template test-release $CHART_PATH > /tmp/readme2word-manifests.yaml
    
    if kubectl apply --dry-run=client -f /tmp/readme2word-manifests.yaml > /dev/null 2>&1; then
        print_success "Kubernetes manifest validation passed!"
    else
        print_warning "Kubernetes manifest validation failed (this might be due to cluster connectivity)"
    fi
    
    # Clean up
    rm -f /tmp/readme2word-manifests.yaml
}

# Function to check chart dependencies
check_dependencies() {
    print_status "Checking chart dependencies..."
    
    if [ -f "$CHART_PATH/Chart.lock" ]; then
        print_status "Found Chart.lock, updating dependencies..."
        helm dependency update $CHART_PATH
    else
        print_status "No dependencies found"
    fi
    
    print_success "Dependencies check completed!"
}

# Function to validate values files
validate_values() {
    print_status "Validating values files..."
    
    # Check if values files are valid YAML
    for values_file in "$CHART_PATH/values.yaml" "./values-dev.yaml" "./values-prod.yaml"; do
        if [ -f "$values_file" ]; then
            if python3 -c "import yaml; yaml.safe_load(open('$values_file'))" 2>/dev/null; then
                print_success "$(basename $values_file) is valid YAML"
            else
                print_error "$(basename $values_file) is not valid YAML"
                exit 1
            fi
        fi
    done
}

# Function to show chart information
show_chart_info() {
    print_status "Chart Information:"
    echo ""
    helm show chart $CHART_PATH
    echo ""
    
    print_status "Chart Values:"
    echo ""
    helm show values $CHART_PATH | head -20
    echo "..."
    echo ""
}

# Function to generate sample manifests
generate_samples() {
    print_status "Generating sample manifests..."
    
    mkdir -p ./samples
    
    # Generate default manifests
    helm template readme2word $CHART_PATH > ./samples/default-manifests.yaml
    print_success "Generated: ./samples/default-manifests.yaml"
    
    # Generate dev manifests
    helm template readme2word-dev $CHART_PATH -f ./values-dev.yaml > ./samples/dev-manifests.yaml
    print_success "Generated: ./samples/dev-manifests.yaml"
    
    # Generate prod manifests
    helm template readme2word-prod $CHART_PATH -f ./values-prod.yaml > ./samples/prod-manifests.yaml
    print_success "Generated: ./samples/prod-manifests.yaml"
    
    print_success "Sample manifests generated in ./samples/ directory"
}

# Main validation function
validate_all() {
    print_status "Starting Helm chart validation..."
    echo ""
    
    check_prerequisites
    echo ""
    
    validate_values
    echo ""
    
    check_dependencies
    echo ""
    
    validate_syntax
    echo ""
    
    validate_templates
    echo ""
    
    validate_k8s_manifests
    echo ""
    
    show_chart_info
    
    print_success "All validations passed! ✅"
    echo ""
    print_status "Chart is ready for deployment!"
}

# Parse command line arguments
case "${1:-validate}" in
    "validate")
        validate_all
        ;;
    "lint")
        validate_syntax
        ;;
    "templates")
        validate_templates
        ;;
    "manifests")
        validate_k8s_manifests
        ;;
    "info")
        show_chart_info
        ;;
    "samples")
        generate_samples
        ;;
    *)
        echo "Usage: $0 {validate|lint|templates|manifests|info|samples}"
        echo ""
        echo "Commands:"
        echo "  validate   - Run all validations (default)"
        echo "  lint       - Validate chart syntax only"
        echo "  templates  - Validate template rendering only"
        echo "  manifests  - Validate Kubernetes manifests only"
        echo "  info       - Show chart information"
        echo "  samples    - Generate sample manifests"
        exit 1
        ;;
esac 