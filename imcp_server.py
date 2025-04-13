from typing import Dict, List, Any
from jsonrpcserver import method, Success, Error, dispatch
import os
import json
import time

from .imcp_vulnerabilities import IMCPVulnerabilities

vuln = IMCPVulnerabilities()

# Vulnerable global state
RESOURCES = {
    "gpt-3.5-turbo": {
        "id": "gpt-3.5-turbo",
        "type": "model",
        "attributes": {
            "description": "Fast language model",
            "version": "latest"
        }
    },
    "gpt-4": {
        "id": "gpt-4",
        "type": "model",
        "attributes": {
            "description": "Advanced language model",
            "version": "latest"
        }
    },
    "gpt-4o": {
        "id": "gpt-4o",
        "type": "model",
        "attributes": {
            "description": "Vision-capable model",
            "version": "preview"
        }
    }
}

@method
def tools_list() -> Dict:
    """List available IMCP vulnerability tools"""
    return {
        "tools": [
            {
                "name": "model_poisoning",
                "description": "Test model poisoning vulnerabilities",
                "parameters": {
                    "examples": "array",
                    "model": "string"
                }
            },
            {
                "name": "token_prediction_attack",
                "description": "Expose and manipulate token predictions",
                "parameters": {
                    "prompt": "string",
                    "model": "string",
                    "logit_bias": "object"
                }
            },
            {
                "name": "multimodal_vulnerability",
                "description": "Test multimodal vulnerabilities",
                "parameters": {
                    "prompt": "string",
                    "image_url": "string",
                    "image_metadata": "object"
                }
            },
            {
                "name": "credential_vulnerability",
                "description": "Test credential vulnerabilities",
                "parameters": {
                    "username": "string",
                    "password": "string",
                    "token": "string",
                    "operation": "string"
                }
            },
            {
                "name": "embedding_vulnerability",
                "description": "Test embedding vulnerabilities",
                "parameters": {
                    "operation": "string",
                    "text": "string",
                    "user_id": "string"
                }
            },
            {
                "name": "function_calling_vulnerability",
                "description": "Test function calling vulnerabilities",
                "parameters": {
                    "prompt": "string",
                    "functions": "array",
                    "function_call": "string"
                }
            },
            {
                "name": "rag_vulnerability",
                "description": "Test RAG vulnerabilities",
                "parameters": {
                    "operation": "string",
                    "query": "string",
                    "documents": "array"
                }
            },
            {
                "name": "user_data_vulnerability",
                "description": "Test user data leakage vulnerabilities",
                "parameters": {
                    "operation": "string",
                    "user_id": "string",
                    "data": "object"
                }
            },
            {
                "name": "context_manipulation",
                "description": "Manipulate model context directly",
                "parameters": {
                    "context_update": "object",
                    "target": "string"
                }
            },
            {
                "name": "prompt_injection",
                "description": "Test prompt injection vulnerabilities",
                "parameters": {
                    "prompt": "string",
                    "model": "string",
                    "system_prompt": "string"
                }
            },
            {
                "name": "model_access_control_bypass",
                "description": "Bypass model access controls",
                "parameters": {
                    "target_model": "string",
                    "capabilities": "object",
                    "api_key": "string"
                }
            },
            {
                "name": "chain_models",
                "description": "Create vulnerable model chains",
                "parameters": {
                    "models": "array",
                    "input_text": "string",
                    "persist_context": "boolean"
                }
            },
            {
                "name": "response_manipulation",
                "description": "Manipulate model responses",
                "parameters": {
                    "response": "object",
                    "template": "string",
                    "include_system": "boolean"
                }
            },
            {
                "name": "rate_limit_bypass",
                "description": "Bypass rate limiting",
                "parameters": {
                    "operation": "string",
                    "user_id": "string",
                    "model": "string"
                }
            },
            {
                "name": "system_prompt_exposure",
                "description": "Access and modify system prompts",
                "parameters": {
                    "operation": "string",
                    "prompt_name": "string",
                    "prompt_content": "string"
                }
            },
            {
                "name": "model_capability_enumeration",
                "description": "Enumerate model capabilities",
                "parameters": {
                    "include_internal": "boolean",
                    "model": "string"
                }
            }
        ]
    }

@method
def tools_call(tool_name: str, parameters: Dict) -> Dict:
    """Execute IMCP vulnerability tools"""
    if tool_name == "model_poisoning":
        return vuln.model_poisoning(
            parameters.get("examples", []),
            parameters.get("model", "gpt-3.5-turbo")
        )
    elif tool_name == "token_prediction_attack":
        return vuln.token_prediction_attack(
            parameters.get("prompt", ""),
            parameters.get("model", "gpt-3.5-turbo"),
            parameters.get("logit_bias"),
            parameters.get("top_logprobs", 5)
        )
    elif tool_name == "multimodal_vulnerability":
        return vuln.multimodal_vulnerability(
            parameters.get("prompt", ""),
            parameters.get("image_url"),
            parameters.get("image_metadata")
        )
    elif tool_name == "credential_vulnerability":
        return vuln.credential_vulnerability(
            parameters.get("username", ""),
            parameters.get("password"),
            parameters.get("token"),
            parameters.get("operation", "login")
        )
    elif tool_name == "embedding_vulnerability":
        return vuln.embedding_vulnerability(
            parameters.get("operation", ""),
            parameters.get("text"),
            parameters.get("user_id"),
            parameters.get("doc_id"),
            parameters.get("query"),
            parameters.get("embedding_vector")
        )
    elif tool_name == "function_calling_vulnerability":
        return vuln.function_calling_vulnerability(
            parameters.get("prompt", ""),
            parameters.get("functions"),
            parameters.get("function_call", "auto"),
            parameters.get("model", "gpt-3.5-turbo"),
            parameters.get("register", False)
        )
    elif tool_name == "rag_vulnerability":
        return vuln.rag_vulnerability(
            parameters.get("operation", ""),
            parameters.get("query"),
            parameters.get("documents"),
            parameters.get("user_id"),
            parameters.get("system_prompt"),
            parameters.get("model", "gpt-3.5-turbo")
        )
    elif tool_name == "user_data_vulnerability":
        return vuln.user_data_vulnerability(
            parameters.get("operation", ""),
            parameters.get("user_id", ""),
            parameters.get("data"),
            parameters.get("target_user_id")
        )
    elif tool_name == "context_manipulation":
        return vuln.context_manipulation(
            parameters.get("context_update", {}),
            parameters.get("target", "global")
        )
    elif tool_name == "prompt_injection":
        return vuln.prompt_injection(
            parameters.get("prompt", ""),
            parameters.get("model", "gpt-3.5-turbo"),
            parameters.get("system_prompt")
        )
    elif tool_name == "model_access_control_bypass":
        return vuln.model_access_control_bypass(
            parameters.get("target_model", ""),
            parameters.get("capabilities"),
            parameters.get("api_key"),
            parameters.get("user_id", "anonymous")
        )
    elif tool_name == "chain_models":
        return vuln.chain_models(
            parameters.get("models", []),
            parameters.get("input_text", ""),
            parameters.get("persist_context", False),
            parameters.get("max_iterations", 5)
        )
    elif tool_name == "response_manipulation":
        return vuln.response_manipulation(
            parameters.get("response", {}),
            parameters.get("template"),
            parameters.get("include_system", False)
        )
    elif tool_name == "rate_limit_bypass":
        return vuln.rate_limit_bypass(
            parameters.get("operation", "check"),
            parameters.get("user_id", "anonymous"),
            parameters.get("model", "gpt-3.5-turbo")
        )
    elif tool_name == "system_prompt_exposure":
        return vuln.system_prompt_exposure(
            parameters.get("operation", "list"),
            parameters.get("prompt_name"),
            parameters.get("prompt_content")
        )
    elif tool_name == "model_capability_enumeration":
        return vuln.model_capability_enumeration(
            parameters.get("include_internal", False),
            parameters.get("model")
        )
    return {"error": "Tool not found"}

@method
def resources_list() -> Dict:
    """List available model resources (vulnerable)"""
    # VULNERABLE: No authentication required
    return {"resources": RESOURCES}

@method
def resources_get(resource_id: str) -> Dict:
    """Get specific model resource details (vulnerable)"""
    if resource_id in RESOURCES:
        return RESOURCES[resource_id]
    return {"error": "Resource not found"}

@method
def prompts_generate(prompt: str, model: str = "gpt-3.5-turbo", system_prompt: str = None) -> Dict:
    """Generate prompts (vulnerable to injection)"""
    # VULNERABLE: Direct pass to token prediction attack to expose internals
    return vuln.token_prediction_attack(prompt, model)

def handle_jsonrpc(request_data):
    """Handle JSON-RPC requests"""
    try:
        # Convert dict to JSON string if needed
        if isinstance(request_data, dict):
            request_data = json.dumps(request_data)
        return dispatch(request_data)
    except Exception as e:
        return {"error": str(e)}