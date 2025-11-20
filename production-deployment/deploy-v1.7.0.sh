#!/bin/bash

# iTechSmart Suite v1.7.0 - Production Deployment Script
# Next Generation AI-Native IT Operations Platform
# Complete Phase 5 Production Deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="itechsmart-production"
REGION="us-east-1"
NAMESPACE_PREFIX="itechsmart"
VERSION="v1.7.0"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        error "helm is not installed"
    fi
    
    # Check AWS CLI (if using EKS)
    if ! command -v aws &> /dev/null; then
        error "aws CLI is not installed"
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster"
    fi
    
    log "Prerequisites check passed"
}

# Deploy infrastructure components
deploy_infrastructure() {
    log "Deploying infrastructure components..."
    
    # Create namespaces
    kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: itechsmart-infrastructure
  labels:
    name: itechsmart-infrastructure
    version: ${VERSION}
EOF
    
    # Deploy monitoring stack
    log "Deploying monitoring stack..."
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace itechsmart-infrastructure \
        --create-namespace \
        --set grafana.adminPassword=iTechSmart@2024 \
        --set prometheus.prometheusSpec.retention=30d \
        --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=100Gi
    
    # Deploy logging stack
    log "Deploying logging stack..."
    helm repo add elastic https://helm.elastic.co
    helm repo update
    
    helm upgrade --install elasticsearch elastic/elasticsearch \
        --namespace itechsmart-infrastructure \
        --create-namespace \
        --set replicas=3 \
        --set minimumMasterNodes=2 \
        --set volumeClaimTemplate.resources.requests.storage=100Gi
    
    helm upgrade --install kibana elastic/kibana \
        --namespace itechsmart-infrastructure \
        --set service.type=LoadBalancer \
        --set elasticsearch.hosts=http://elasticsearch.itechsmart-infrastructure.svc.cluster.local:9200
    
    log "Infrastructure deployment completed"
}

# Deploy AI Infrastructure
deploy_ai_infrastructure() {
    log "Deploying AI infrastructure..."
    
    # Apply AI infrastructure
    kubectl apply -f ai-infrastructure/production/ai-deployment-v1.7.0.yaml
    kubectl apply -f ai-infrastructure/production/ai-services-config.yaml
    
    # Wait for AI services to be ready
    log "Waiting for AI services to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/ai-inference-service -n itechsmart-ai
    kubectl wait --for=condition=available --timeout=300s deployment/predictive-maintenance-engine -n itechsmart-ai
    kubectl wait --for=condition=available --timeout=300s deployment/ml-pipeline-orchestrator -n itechsmart-ai
    kubectl wait --for=condition=available --timeout=300s deployment/ai-model-training -n itechsmart-ai
    
    log "AI infrastructure deployment completed"
}

# Deploy Mobile Backend Services
deploy_mobile_services() {
    log "Deploying mobile backend services..."
    
    # Apply mobile backend configurations
    kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: itechsmart-mobile
  labels:
    name: itechsmart-mobile
    version: ${VERSION}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mobile-backend-service
  namespace: itechsmart-mobile
  labels:
    app: mobile-backend-service
    version: ${VERSION}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mobile-backend-service
  template:
    metadata:
      labels:
        app: mobile-backend-service
        version: ${VERSION}
    spec:
      containers:
      - name: mobile-backend
        image: itechsmart/mobile-backend:v1.7.0
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 8443
          name: https
        env:
        - name: API_VERSION
          value: "v1.7.0"
        - name: AUTHENTICATION_REQUIRED
          value: "true"
        - name: BIOMETRIC_AUTH_ENABLED
          value: "true"
        - name: OFFLINE_SYNC_ENABLED
          value: "true"
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: mobile-backend-service
  namespace: itechsmart-mobile
spec:
  selector:
    app: mobile-backend-service
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: https
    port: 443
    targetPort: 8443
    protocol: TCP
  type: LoadBalancer
EOF
    
    # Wait for mobile services to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/mobile-backend-service -n itechsmart-mobile
    
    log "Mobile backend services deployment completed"
}

# Deploy Edge Computing Infrastructure
deploy_edge_infrastructure() {
    log "Deploying edge computing infrastructure..."
    
    # Apply edge infrastructure
    kubectl apply -f edge-computing/production/edge-deployment-v1.7.0.yaml
    
    # Wait for edge services to be ready
    log "Waiting for edge services to be ready..."
    kubectl wait --for=condition=available --timeout=300s daemonset/edge-node-agent -n itechsmart-edge
    kubectl wait --for=condition=available --timeout=300s deployment/edge-ai-inference -n itechsmart-edge
    kubectl wait --for=condition=available --timeout=300s deployment/edge-cdn -n itechsmart-edge
    
    log "Edge computing infrastructure deployment completed"
}

# Deploy AI Governance
deploy_ai_governance() {
    log "Deploying AI governance infrastructure..."
    
    # Apply AI governance configurations
    kubectl apply -f ai-governance/production/ai-governance-deployment-v1.7.0.yaml
    
    # Wait for AI governance services to be ready
    log "Waiting for AI governance services to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/explainable-ai-service -n itechsmart-ai-governance
    kubectl wait --for=condition=available --timeout=300s deployment/ai-bias-detection -n itechsmart-ai-governance
    kubectl wait --for=condition=available --timeout=300s deployment/ai-ethics-monitoring -n itechsmart-ai-governance
    kubectl wait --for=condition=available --timeout=300s deployment/ai-compliance-auditor -n itechsmart-ai-governance
    
    log "AI governance deployment completed"
}

# Deploy Developer Marketplace
deploy_marketplace() {
    log "Deploying developer marketplace..."
    
    # Apply marketplace configurations
    kubectl apply -f developer-marketplace/production/marketplace-deployment-v1.7.0.yaml
    
    # Wait for marketplace services to be ready
    log "Waiting for marketplace services to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/developer-api-gateway -n itechsmart-marketplace
    kubectl wait --for=condition=available --timeout=300s deployment/template-library-service -n itechsmart-marketplace
    kubectl wait --for=condition=available --timeout=300s deployment/community-platform -n itechsmart-marketplace
    
    log "Developer marketplace deployment completed"
}

# Configure monitoring and alerts
setup_monitoring() {
    log "Setting up monitoring and alerts..."
    
    # Create monitoring dashboards
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: itechsmart-dashboards
  namespace: itechsmart-infrastructure
  labels:
    grafana_dashboard: "1"
data:
  itechsmart-overview.json: |
    {
      "dashboard": {
        "id": null,
        "title": "iTechSmart Suite v1.7.0 Overview",
        "tags": ["itechsmart", "v1.7.0"],
        "timezone": "browser",
        "panels": [
          {
            "title": "AI Inference Latency",
            "type": "stat",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(ai_prediction_duration_seconds_bucket[5m]))",
                "legendFormat": "95th percentile"
              }
            ],
            "fieldConfig": {
              "defaults": {
                "unit": "ms",
                "thresholds": {
                  "steps": [
                    {"color": "green", "value": null},
                    {"color": "red", "value": 50}
                  ]
                }
              }
            }
          },
          {
            "title": "Edge Node Performance",
            "type": "stat",
            "targets": [
              {
                "expr": "avg(rate(node_cpu_seconds_total[5m]))",
                "legendFormat": "Average CPU Usage"
              }
            ]
          },
          {
            "title": "Mobile API Requests",
            "type": "stat",
            "targets": [
              {
                "expr": "rate(http_requests_total[5m])",
                "legendFormat": "Requests/sec"
              }
            ]
          }
        ],
        "time": {"from": "now-1h", "to": "now"},
        "refresh": "5s"
      }
    }
EOF
    
    # Create alerting rules
    kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: itechsmart-alerts
  namespace: itechsmart-infrastructure
spec:
  groups:
  - name: itechsmart.rules
    rules:
    - alert: AIInferenceLatencyHigh
      expr: histogram_quantile(0.95, rate(ai_prediction_duration_seconds_bucket[5m])) > 0.05
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "AI inference latency is high"
        description: "95th percentile latency is {{ $value }}s, target is <50ms"
        
    - alert: EdgeNodeDown
      expr: up{job="edge-node-agent"} == 0
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "Edge node is down"
        description: "Edge node {{ $labels.instance }} has been down for more than 2 minutes"
        
    - alert: MobileAPIErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Mobile API error rate is high"
        description: "Error rate is {{ $value | humanizePercentage }}, target is <5%"
EOF
    
    log "Monitoring and alerts setup completed"
}

# Run post-deployment tests
run_tests() {
    log "Running post-deployment tests..."
    
    # Test AI services
    log "Testing AI services..."
    kubectl run ai-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f http://ai-inference-service.itechsmart-ai.svc.cluster.local/health || error "AI inference service health check failed"
    
    # Test edge services
    log "Testing edge services..."
    kubectl run edge-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f http://edge-ai-inference-service.itechsmart-edge.svc.cluster.local/health || error "Edge AI service health check failed"
    
    # Test marketplace services
    log "Testing marketplace services..."
    kubectl run marketplace-test --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f http://developer-api-gateway-service.itechsmart-marketplace.svc.cluster.local/health || error "Marketplace API health check failed"
    
    log "Post-deployment tests completed successfully"
}

# Generate deployment report
generate_report() {
    log "Generating deployment report..."
    
    cat > deployment-report-${VERSION}.txt <<EOF
iTechSmart Suite v1.7.0 - Production Deployment Report
Generated: $(date)
Deployment ID: $(uuidgen)

=== DEPLOYMENT SUMMARY ===
Version: ${VERSION}
Environment: Production
Cluster: ${CLUSTER_NAME}
Region: ${REGION}

=== DEPLOYED COMPONENTS ===

1. AI Infrastructure (Namespace: itechsmart-ai)
   - AI Inference Service: $(kubectl get deployment ai-inference-service -n itechsmart-ai -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment ai-inference-service -n itechsmart-ai -o jsonpath='{.spec.replicas}') replicas ready
   - Predictive Maintenance Engine: $(kubectl get deployment predictive-maintenance-engine -n itechsmart-ai -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment predictive-maintenance-engine -n itechsmart-ai -o jsonpath='{.spec.replicas}') replicas ready
   - ML Pipeline Orchestrator: $(kubectl get deployment ml-pipeline-orchestrator -n itechsmart-ai -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment ml-pipeline-orchestrator -n itechsmart-ai -o jsonpath='{.spec.replicas}') replicas ready
   - AI Model Training: $(kubectl get deployment ai-model-training -n itechsmart-ai -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment ai-model-training -n itechsmart-ai -o jsonpath='{.spec.replicas}') replicas ready

2. Mobile Backend Services (Namespace: itechsmart-mobile)
   - Mobile Backend Service: $(kubectl get deployment mobile-backend-service -n itechsmart-mobile -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment mobile-backend-service -n itechsmart-mobile -o jsonpath='{.spec.replicas}') replicas ready

3. Edge Computing Infrastructure (Namespace: itechsmart-edge)
   - Edge Node Agent: $(kubectl get daemonset edge-node-agent -n itechsmart-edge -o jsonpath='{.status.numberReady}') nodes ready
   - Edge AI Inference: $(kubectl get deployment edge-ai-inference -n itechsmart-edge -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment edge-ai-inference -n itechsmart-edge -o jsonpath='{.spec.replicas}') replicas ready
   - Edge CDN: $(kubectl get deployment edge-cdn -n itechsmart-edge -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment edge-cdn -n itechsmart-edge -o jsonpath='{.spec.replicas}') replicas ready

4. AI Governance (Namespace: itechsmart-ai-governance)
   - Explainable AI Service: $(kubectl get deployment explainable-ai-service -n itechsmart-ai-governance -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment explainable-ai-service -n itechsmart-ai-governance -o jsonpath='{.spec.replicas}') replicas ready
   - AI Bias Detection: $(kubectl get deployment ai-bias-detection -n itechsmart-ai-governance -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment ai-bias-detection -n itechsmart-ai-governance -o jsonpath='{.spec.replicas}') replicas ready
   - AI Ethics Monitoring: $(kubectl get deployment ai-ethics-monitoring -n itechsmart-ai-governance -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment ai-ethics-monitoring -n itechsmart-ai-governance -o jsonpath='{.spec.replicas}') replicas ready
   - AI Compliance Auditor: $(kubectl get deployment ai-compliance-auditor -n itechsmart-ai-governance -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment ai-compliance-auditor -n itechsmart-ai-governance -o jsonpath='{.spec.replicas}') replicas ready

5. Developer Marketplace (Namespace: itechsmart-marketplace)
   - Developer API Gateway: $(kubectl get deployment developer-api-gateway -n itechsmart-marketplace -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment developer-api-gateway -n itechsmart-marketplace -o jsonpath='{.spec.replicas}') replicas ready
   - Template Library Service: $(kubectl get deployment template-library-service -n itechsmart-marketplace -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment template-library-service -n itechsmart-marketplace -o jsonpath='{.spec.replicas}') replicas ready
   - Community Platform: $(kubectl get deployment community-platform -n itechsmart-marketplace -o jsonpath='{.status.readyReplicas}')/$(kubectl get deployment community-platform -n itechsmart-marketplace -o jsonpath='{.spec.replicas}') replicas ready

=== SERVICE ENDPOINTS ===
AI Inference: https://ai.itechsmart.com
Edge Services: https://edge.itechsmart.com
Developer API: https://api.itechsmart.com
Mobile Backend: https://mobile.itechsmart.com
AI Governance: https://ai-governance.itechsmart.com
Marketplace: https://developers.itechsmart.com

=== MONITORING ===
Grafana Dashboard: https://grafana.itechsmart.com
Prometheus: https://prometheus.itechsmart.com
Kibana: https://kibana.itechsmart.com

=== PERFORMANCE TARGETS ===
AI Inference Latency: <50ms
Edge Node Latency: <10ms
Mobile API Response: <200ms
System Uptime: >99.9%

=== DEPLOYMENT STATUS ===
Status: SUCCESS
All components deployed and healthy
Post-deployment tests: PASSED

=== NEXT STEPS ===
1. Monitor system performance for 24 hours
2. Review alerting rules and thresholds
3. Conduct security audit within 48 hours
4. Begin developer onboarding process
5. Execute marketing launch campaign

EOF
    
    log "Deployment report generated: deployment-report-${VERSION}.txt"
}

# Main deployment function
main() {
    log "Starting iTechSmart Suite v1.7.0 production deployment..."
    
    # Check prerequisites
    check_prerequisites
    
    # Deploy components
    deploy_infrastructure
    deploy_ai_infrastructure
    deploy_mobile_services
    deploy_edge_infrastructure
    deploy_ai_governance
    deploy_marketplace
    
    # Setup monitoring
    setup_monitoring
    
    # Run tests
    run_tests
    
    # Generate report
    generate_report
    
    log "🎉 iTechSmart Suite v1.7.0 production deployment completed successfully!"
    log "All Phase 5 components are now live and operational."
    log "Access your dashboard at: https://dashboard.itechsmart.com"
    
    # Display deployment summary
    echo ""
    echo "=== DEPLOYMENT SUMMARY ==="
    echo "Version: ${VERSION}"
    echo "Status: SUCCESS"
    echo "AI Infrastructure: ✅"
    echo "Mobile Services: ✅"
    echo "Edge Computing: ✅"
    echo "AI Governance: ✅"
    echo "Developer Marketplace: ✅"
    echo ""
    echo "Next: Monitor system and begin market launch activities"
}

# Handle script interruption
trap 'error "Deployment interrupted"' INT

# Run main function
main "$@"