#!/usr/bin/env python3
"""
MCP server implementation for kubectl-mcp-tool.
"""

import json
import sys
import logging
import asyncio
import os
from typing import Dict, Any, List, Optional, Callable, Awaitable

try:
    # Import the official MCP SDK with FastMCP
    from mcp.server.fastmcp import FastMCP
except ImportError:
    logging.error("MCP SDK not found. Installing...")
    import subprocess
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "mcp>=1.5.0"
        ])
        from mcp.server.fastmcp import FastMCP
    except Exception as e:
        logging.error(f"Failed to install MCP SDK: {e}")
        raise

# Configure logging to stderr only for MCP compatibility
logger = logging.getLogger("mcp-server")

class MCPServer:
    """MCP server implementation."""
    
    def __init__(self, name: str):
        """Initialize the MCP server."""
        self.name = name
        # Create a new server instance using the FastMCP API
        self.server = FastMCP(name=name)
        
        # Register tools using the new FastMCP API
        self.setup_tools()
    
    def setup_tools(self):
        """Set up the tools for the MCP server."""
        
        @self.server.tool()
        def get_pods(namespace: Optional[str] = None) -> Dict[str, Any]:
            """Get all pods in the specified namespace."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                v1 = client.CoreV1Api()
                
                if namespace:
                    pods = v1.list_namespaced_pod(namespace)
                else:
                    pods = v1.list_pod_for_all_namespaces()
                
                return {
                    "success": True,
                    "pods": [
                        {
                            "name": pod.metadata.name,
                            "namespace": pod.metadata.namespace,
                            "status": pod.status.phase,
                            "ip": pod.status.pod_ip
                        }
                        for pod in pods.items
                    ]
                }
            except Exception as e:
                logger.error(f"Error getting pods: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def get_namespaces() -> Dict[str, Any]:
            """Get all Kubernetes namespaces."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                v1 = client.CoreV1Api()
                
                namespaces = v1.list_namespace()
                return {
                    "success": True,
                    "namespaces": [ns.metadata.name for ns in namespaces.items]
                }
            except Exception as e:
                logger.error(f"Error getting namespaces: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def create_deployment(name: str, image: str, replicas: int, namespace: Optional[str] = "default") -> Dict[str, Any]:
            """Create a new deployment."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                apps_v1 = client.AppsV1Api()
                
                deployment = client.V1Deployment(
                    metadata=client.V1ObjectMeta(name=name),
                    spec=client.V1DeploymentSpec(
                        replicas=replicas,
                        selector=client.V1LabelSelector(
                            match_labels={"app": name}
                        ),
                        template=client.V1PodTemplateSpec(
                            metadata=client.V1ObjectMeta(
                                labels={"app": name}
                            ),
                            spec=client.V1PodSpec(
                                containers=[
                                    client.V1Container(
                                        name=name,
                                        image=image
                                    )
                                ]
                            )
                        )
                    )
                )
                
                apps_v1.create_namespaced_deployment(
                    body=deployment,
                    namespace=namespace
                )
                
                return {
                    "success": True,
                    "message": f"Deployment {name} created successfully"
                }
            except Exception as e:
                logger.error(f"Error creating deployment: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def delete_resource(resource_type: str, name: str, namespace: Optional[str] = "default") -> Dict[str, Any]:
            """Delete a Kubernetes resource."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                
                if resource_type == "pod":
                    v1 = client.CoreV1Api()
                    v1.delete_namespaced_pod(name=name, namespace=namespace)
                elif resource_type == "deployment":
                    apps_v1 = client.AppsV1Api()
                    apps_v1.delete_namespaced_deployment(name=name, namespace=namespace)
                elif resource_type == "service":
                    v1 = client.CoreV1Api()
                    v1.delete_namespaced_service(name=name, namespace=namespace)
                else:
                    return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
                
                return {
                    "success": True,
                    "message": f"{resource_type} {name} deleted successfully"
                }
            except Exception as e:
                logger.error(f"Error deleting resource: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def get_logs(pod_name: str, namespace: Optional[str] = "default", container: Optional[str] = None, tail: Optional[int] = None) -> Dict[str, Any]:
            """Get logs from a pod."""
            try:
                from kubernetes import client, config
                config.load_kube_config()
                v1 = client.CoreV1Api()
                
                logs = v1.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    container=container,
                    tail_lines=tail
                )
                
                return {
                    "success": True,
                    "logs": logs
                }
            except Exception as e:
                logger.error(f"Error getting logs: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def port_forward(pod_name: str, local_port: int, pod_port: int, namespace: Optional[str] = "default") -> Dict[str, Any]:
            """Forward local port to pod port."""
            try:
                import subprocess
                
                cmd = [
                    "kubectl", "port-forward",
                    f"pod/{pod_name}",
                    f"{local_port}:{pod_port}",
                    "-n", namespace
                ]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                return {
                    "success": True,
                    "message": f"Port forwarding started: localhost:{local_port} -> {pod_name}:{pod_port}",
                    "process_pid": process.pid
                }
            except Exception as e:
                logger.error(f"Error setting up port forward: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def scale_deployment(name: str, replicas: int, namespace: str = "default") -> Dict[str, Any]:
            """Scale a deployment."""
            try:
                from .core.kubernetes_ops import KubernetesOperations
                k8s_ops = KubernetesOperations()
                return k8s_ops.scale_deployment(name, replicas, namespace)
            except Exception as e:
                logger.error(f"Error scaling deployment: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def list_services(namespace: str = "default", label_selector: Optional[str] = None) -> Dict[str, Any]:
            """List services in a namespace."""
            try:
                from .core.kubernetes_ops import KubernetesOperations
                k8s_ops = KubernetesOperations()
                return k8s_ops.list_services(namespace, label_selector)
            except Exception as e:
                logger.error(f"Error listing services: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def list_deployments(namespace: str = "default", label_selector: Optional[str] = None) -> Dict[str, Any]:
            """List deployments in a namespace."""
            try:
                from .core.kubernetes_ops import KubernetesOperations
                k8s_ops = KubernetesOperations()
                return k8s_ops.list_deployments(namespace, label_selector)
            except Exception as e:
                logger.error(f"Error listing deployments: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def list_nodes(label_selector: Optional[str] = None) -> Dict[str, Any]:
            """List all nodes in the cluster."""
            try:
                from .core.kubernetes_ops import KubernetesOperations
                k8s_ops = KubernetesOperations()
                return k8s_ops.list_nodes(label_selector)
            except Exception as e:
                logger.error(f"Error listing nodes: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def describe_pod(pod_name: str, namespace: str = "default") -> Dict[str, Any]:
            """Describe a pod in detail."""
            try:
                from .core.kubernetes_ops import KubernetesOperations
                k8s_ops = KubernetesOperations()
                return k8s_ops.describe_pod(pod_name, namespace)
            except Exception as e:
                logger.error(f"Error describing pod: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def get_contexts() -> Dict[str, Any]:
            """Get available kubectl contexts."""
            try:
                from .core.kubernetes_ops import KubernetesOperations
                k8s_ops = KubernetesOperations()
                return k8s_ops.get_contexts()
            except Exception as e:
                logger.error(f"Error getting contexts: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def switch_context(context_name: str) -> Dict[str, Any]:
            """Switch kubectl context."""
            try:
                from .core.kubernetes_ops import KubernetesOperations
                k8s_ops = KubernetesOperations()
                return k8s_ops.switch_context(context_name)
            except Exception as e:
                logger.error(f"Error switching context: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def create_config_map(name: str, data: Dict[str, str], namespace: str = "default") -> Dict[str, Any]:
            """Create a ConfigMap."""
            try:
                from .core.kubernetes_ops import KubernetesOperations
                k8s_ops = KubernetesOperations()
                return k8s_ops.create_config_map(name, data, namespace)
            except Exception as e:
                logger.error(f"Error creating ConfigMap: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def create_secret(name: str, data: Dict[str, str], secret_type: str = "Opaque", namespace: str = "default") -> Dict[str, Any]:
            """Create a Secret."""
            try:
                from .core.kubernetes_ops import KubernetesOperations
                k8s_ops = KubernetesOperations()
                return k8s_ops.create_secret(name, data, secret_type, namespace)
            except Exception as e:
                logger.error(f"Error creating Secret: {e}")
                return {"success": False, "error": str(e)}
        
        @self.server.tool()
        def explain_error(error_msg: str) -> Dict[str, Any]:
            """Explain Kubernetes errors in plain English."""
            try:
                from .core.kubernetes_ops import KubernetesOperations
                k8s_ops = KubernetesOperations()
                return k8s_ops.explain_error(error_msg)
            except Exception as e:
                logger.error(f"Error explaining error: {e}")
                return {"success": False, "error": str(e)}
        
    
    async def serve_stdio(self):
        """Serve the MCP server over stdio transport."""
        # Add detailed logging for debugging Cursor integration
        logger.info("Starting MCP server with stdio transport")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Python executable: {sys.executable}")
        logger.info(f"Python version: {sys.version}")
        
        # Log Kubernetes configuration
        kube_config = os.environ.get('KUBECONFIG', '~/.kube/config')
        expanded_path = os.path.expanduser(kube_config)
        logger.info(f"KUBECONFIG: {kube_config} (expanded: {expanded_path})")
        if os.path.exists(expanded_path):
            logger.info(f"Kubernetes config file exists at {expanded_path}")
        else:
            logger.warning(f"Kubernetes config file does not exist at {expanded_path}")
        
        # Continue with normal server startup
        await self.server.run_stdio_async()
    
    async def serve_sse(self, port: int):
        """Serve the MCP server over SSE transport."""
        logger.info(f"Starting MCP server with SSE transport on port {port}")
        await self.server.run_sse_async(port=port)
