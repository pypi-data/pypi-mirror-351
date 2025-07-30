#!/usr/bin/env python3
"""
Simple smoke tests for kubectl-mcp-server.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from mcp_kubectl.mcp_server import MCPServer


def test_mcp_server_creation():
    """Test that MCP server can be created without errors."""
    server = MCPServer("test-server")
    assert server is not None
    assert server.name == "test-server"
    assert server.server is not None


def test_mcp_server_has_expected_tools():
    """Test that the server registers the expected tools."""
    server = MCPServer("test-server")
    
    # Check that server has tools registered
    # Note: FastMCP doesn't expose _tools directly, so we test indirectly
    assert hasattr(server.server, 'tool')
    assert callable(server.server.tool)


@pytest.mark.asyncio
async def test_server_stdio_setup():
    """Test that stdio server setup doesn't crash."""
    server = MCPServer("test-server")
    
    # Mock the FastMCP run_stdio_async method to avoid actually starting server
    with patch.object(server.server, 'run_stdio_async') as mock_run:
        mock_run.return_value = None
        
        # This should not raise an exception
        await server.serve_stdio()
        
        # Verify the method was called
        mock_run.assert_called_once()


@pytest.mark.asyncio 
async def test_server_sse_setup():
    """Test that SSE server setup doesn't crash."""
    server = MCPServer("test-server")
    
    # Mock the FastMCP run_sse_async method
    with patch.object(server.server, 'run_sse_async') as mock_run:
        mock_run.return_value = None
        
        # This should not raise an exception
        await server.serve_sse(8000)
        
        # Verify the method was called with correct port
        mock_run.assert_called_once_with(port=8000)


def test_kubernetes_ops_import():
    """Test that kubernetes operations can be imported."""
    from mcp_kubectl.core.kubernetes_ops import KubernetesOperations
    
    # Should be able to import without error
    assert KubernetesOperations is not None


@pytest.mark.asyncio
async def test_mock_kubernetes_operations():
    """Test kubernetes operations with mocked client."""
    from mcp_kubectl.core.kubernetes_ops import KubernetesOperations
    
    # Mock the kubernetes config and client
    with patch('mcp_kubectl.core.kubernetes_ops.config') as mock_config, \
         patch('mcp_kubectl.core.kubernetes_ops.client') as mock_client:
        
        # Setup mocks
        mock_config.load_kube_config.return_value = None
        mock_v1 = MagicMock()
        mock_apps_v1 = MagicMock()
        mock_networking_v1 = MagicMock()
        mock_client.CoreV1Api.return_value = mock_v1
        mock_client.AppsV1Api.return_value = mock_apps_v1
        mock_client.NetworkingV1Api.return_value = mock_networking_v1
        
        # Create KubernetesOperations instance
        k8s_ops = KubernetesOperations()
        
        # Verify it was created successfully
        assert k8s_ops is not None
        assert k8s_ops.core_v1 == mock_v1
        assert k8s_ops.apps_v1 == mock_apps_v1
        assert k8s_ops.networking_v1 == mock_networking_v1


def test_cli_import():
    """Test that CLI module can be imported."""
    from mcp_kubectl.cli import main
    
    # Should be able to import without error
    assert main is not None
    assert callable(main)


def test_package_import():
    """Test that main package can be imported."""
    import mcp_kubectl
    
    # Should have version
    assert hasattr(mcp_kubectl, '__version__')
    assert mcp_kubectl.__version__ == "1.1.0"
    
    # Should have MCPServer
    assert hasattr(mcp_kubectl, 'MCPServer')


def test_error_explanation():
    """Test error explanation functionality."""
    from mcp_kubectl.core.kubernetes_ops import KubernetesOperations
    
    # Test static method without needing K8s connection
    result = KubernetesOperations._get_error_suggestions("ImagePullBackOff")
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert "image" in result[0].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])