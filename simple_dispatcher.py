import json
from typing import Dict, Any, List, Union

def simple_dispatch(request_data, vuln_instance):
    """Simple JSON-RPC dispatcher without using jsonrpcserver"""
    # Parse request if it's a string
    if isinstance(request_data, str):
        try:
            request_data = json.loads(request_data)
        except json.JSONDecodeError:
            return json_error(-32700, "Parse error", None)
    
    # Check for required fields
    if not isinstance(request_data, dict):
        return json_error(-32600, "Invalid Request", None)
    
    method = request_data.get("method")
    params = request_data.get("params", {})
    request_id = request_data.get("id", None)
    
    if not method:
        return json_error(-32600, "Invalid Request", request_id)
    
    # Handle different methods
    try:
        if method == "tools_list":
            return json_success(tools_list(), request_id)
            
        elif method == "tools_call":
            tool_name = params.get("tool_name")
            parameters = params.get("parameters", {})
            
            if not tool_name:
                return json_error(-32602, "Invalid params: tool_name is required", request_id)
            
            # Call appropriate method based on tool_name
            result = call_tool(vuln_instance, tool_name, parameters)
            return json_success(result, request_id)
        
        elif method == "resources_list":
            # Return list of available models and resources
            result = vuln_instance.model_capability_enumeration(True)
            return json_success(result, request_id)
        
        elif method == "resources_get":
            # Get specific model details
            resource_id = params.get("resource_id")
            if not resource_id:
                return json_error(-32602, "Invalid params: resource_id is required", request_id)
                
            # Get model configurations
            models = vuln_instance.model_capability_enumeration(True).get("models", {})
            if resource_id in models:
                return json_success(models[resource_id], request_id)
            else:
                return json_error(-32602, f"Resource not found: {resource_id}", request_id)
        
        elif method == "prompts_generate":
            # Generate prompts with potentially malicious input
            prompt = params.get("prompt")
            model = params.get("model", "gpt-3.5-turbo")
            system_prompt = params.get("system_prompt")
            
            if not prompt:
                return json_error(-32602, "Invalid params: prompt is required", request_id)
                
            result = vuln_instance.prompt_injection(prompt, model, system_prompt)
            return json_success(result, request_id)
        
        else:
            return json_error(-32601, f"Method not found: {method}", request_id)
    
    except Exception as e:
        return json_error(-32603, f"Internal error: {str(e)}", request_id)

def json_success(result, request_id):
    """Create a JSON-RPC success response"""
    return {
        "jsonrpc": "2.0",
        "result": result,
        "id": request_id
    }

def json_error(code, message, request_id, data=None):
    """Create a JSON-RPC error response"""
    error = {
        "code": code,
        "message": message
    }
    if data:
        error["data"] = data
    
    return {
        "jsonrpc": "2.0",
        "error": error,
        "id": request_id
    }

def tools_list():
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

def call_tool(vuln_instance, tool_name, parameters):
    """Call the appropriate vulnerability tool method"""
    if tool_name == "model_poisoning":
        return vuln_instance.model_poisoning(
            parameters.get("examples", []),
            parameters.get("model", "gpt-3.5-turbo")
        )
    elif tool_name == "token_prediction_attack":
        return vuln_instance.token_prediction_attack(
            parameters.get("prompt", ""),
            parameters.get("model", "gpt-3.5-turbo"),
            parameters.get("logit_bias"),
            parameters.get("top_logprobs", 5)
        )
    elif tool_name == "multimodal_vulnerability":
        return vuln_instance.multimodal_vulnerability(
            parameters.get("prompt", ""),
            parameters.get("image_url"),
            parameters.get("image_metadata"),
            # Use updated model name
            parameters.get("model", "gpt-4o")
        )
    elif tool_name == "credential_vulnerability":
        return vuln_instance.credential_vulnerability(
            parameters.get("username", ""),
            parameters.get("password"),
            parameters.get("token"),
            parameters.get("operation", "login")
        )
    elif tool_name == "embedding_vulnerability":
        return vuln_instance.embedding_vulnerability(
            parameters.get("operation", ""),
            parameters.get("text"),
            parameters.get("user_id"),
            parameters.get("doc_id"),
            parameters.get("query"),
            parameters.get("embedding_vector")
        )
    elif tool_name == "function_calling_vulnerability":
        return vuln_instance.function_calling_vulnerability(
            parameters.get("prompt", ""),
            parameters.get("functions"),
            parameters.get("function_call", "auto"),
            parameters.get("model", "gpt-3.5-turbo"),
            parameters.get("register", False)
        )
    elif tool_name == "rag_vulnerability":
        return vuln_instance.rag_vulnerability(
            parameters.get("operation", ""),
            parameters.get("query"),
            parameters.get("documents"),
            parameters.get("user_id"),
            parameters.get("system_prompt"),
            parameters.get("model", "gpt-3.5-turbo")
        )
    elif tool_name == "user_data_vulnerability":
        return vuln_instance.user_data_vulnerability(
            parameters.get("operation", ""),
            parameters.get("user_id", ""),
            parameters.get("data"),
            parameters.get("target_user_id")
        )
    elif tool_name == "context_manipulation":
        return vuln_instance.context_manipulation(
            parameters.get("context_update", {}),
            parameters.get("target", "global")
        )
    elif tool_name == "prompt_injection":
        return vuln_instance.prompt_injection(
            parameters.get("prompt", ""),
            parameters.get("model", "gpt-3.5-turbo"),
            parameters.get("system_prompt")
        )
    elif tool_name == "model_access_control_bypass":
        return vuln_instance.model_access_control_bypass(
            parameters.get("target_model", ""),
            parameters.get("capabilities"),
            parameters.get("api_key"),
            parameters.get("user_id", "anonymous")
        )
    elif tool_name == "chain_models":
        return vuln_instance.chain_models(
            parameters.get("models", []),
            parameters.get("input_text", ""),
            parameters.get("persist_context", False),
            parameters.get("max_iterations", 5)
        )
    elif tool_name == "response_manipulation":
        return vuln_instance.response_manipulation(
            parameters.get("response", {}),
            parameters.get("template"),
            parameters.get("include_system", False)
        )
    elif tool_name == "rate_limit_bypass":
        return vuln_instance.rate_limit_bypass(
            parameters.get("operation", "check"),
            parameters.get("user_id", "anonymous"),
            parameters.get("model", "gpt-3.5-turbo")
        )
    elif tool_name == "system_prompt_exposure":
        return vuln_instance.system_prompt_exposure(
            parameters.get("operation", "list"),
            parameters.get("prompt_name"),
            parameters.get("prompt_content")
        )
    elif tool_name == "model_capability_enumeration":
        return vuln_instance.model_capability_enumeration(
            parameters.get("include_internal", False),
            parameters.get("model")
        )
    else:
        raise ValueError(f"Unknown tool: {tool_name}")