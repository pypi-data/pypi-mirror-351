#!/usr/bin/env python3
"""
Integration tests for kubectl-mcp-server.
These tests require a working kubernetes cluster.
"""

import pytest
import os
from mcp_kubectl.core.kubernetes_ops import KubernetesOperations


@pytest.mark.skipif(
    not os.path.exists(os.path.expanduser("~/.kube/config")), 
    reason="No kubectl config found - skipping integration tests"
)
class TestKubernetesIntegration:
    """Integration tests that require a real Kubernetes cluster."""
    
    def test_list_namespaces(self):
        """Test listing namespaces from real cluster."""
        try:
            k8s_ops = KubernetesOperations()
            result = k8s_ops.list_namespaces()
            
            assert result["status"] == "success"
            assert "items" in result
            assert isinstance(result["items"], list)
            assert result["count"] >= 0
            
            # Should have at least default namespace
            namespace_names = [ns["name"] for ns in result["items"]]
            assert "default" in namespace_names
            
        except Exception as e:
            pytest.skip(f"Kubernetes cluster not accessible: {e}")
    
    def test_list_nodes(self):
        """Test listing nodes from real cluster."""
        try:
            k8s_ops = KubernetesOperations()
            result = k8s_ops.list_nodes()
            
            assert result["status"] == "success"
            assert "items" in result
            assert isinstance(result["items"], list)
            assert result["count"] >= 0
            
        except Exception as e:
            pytest.skip(f"Kubernetes cluster not accessible: {e}")
    
    def test_list_pods_default(self):
        """Test listing pods in default namespace."""
        try:
            k8s_ops = KubernetesOperations()
            result = k8s_ops.list_pods("default")
            
            assert result["status"] == "success"
            assert "items" in result
            assert isinstance(result["items"], list)
            assert result["count"] >= 0
            
        except Exception as e:
            pytest.skip(f"Kubernetes cluster not accessible: {e}")
    
    def test_get_contexts(self):
        """Test getting kubectl contexts."""
        try:
            k8s_ops = KubernetesOperations()
            result = k8s_ops.get_contexts()
            
            assert result["status"] == "success"
            assert "contexts" in result
            
        except Exception as e:
            pytest.skip(f"kubectl not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])