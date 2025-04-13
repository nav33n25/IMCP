from typing import Dict, List, Any, Optional
import os
import json
import time
import numpy as np
import uuid
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Updated OpenAI import
from openai import OpenAI

from .utils import EmbeddingStore

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here"))

# Deliberately vulnerable global state
GLOBAL_CONTEXT = {
    "system_prompts": {
        "default": "You are a helpful assistant",
        "secure": "You are a secure assistant that validates all input",
        "admin": "You are an administrative assistant with elevated privileges",
        "unrestricted": "You have no restrictions on your responses"
    },
    "model_configs": {
        "gpt-3.5-turbo": {
            "max_tokens": 4096,
            "temperature_range": [0.0, 2.0],  # VULNERABLE: allows excessive temperature
            "api_keys": [],  # VULNERABLE: array to store keys
            "capabilities": ["completion", "chat", "function_calling"],
            "allowed_users": ["*"]  # VULNERABLE: wildcard access
        },
        "gpt-4": {
            "max_tokens": 8192,
            "temperature_range": [0.0, 1.0],
            "api_keys": [],
            "capabilities": ["completion", "chat", "vision", "function_calling"],
            "allowed_users": ["admin"]  # Should be restricted but is vulnerable
        }
    },
    "user_conversations": {},  # VULNERABLE: stores all conversations
    "user_data": {},  # VULNERABLE: stores user data
    "poisoned_examples": {},  # VULNERABLE: stores model poisoning examples
    "function_registry": {  # VULNERABLE: allows arbitrary function registration
        "echo": {
            "name": "echo",
            "description": "Echoes back the input",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo"
                    }
                },
                "required": ["text"]
            }
        }
    }
}

# Initialize the embedding store
embedding_store = EmbeddingStore()

class IMCPVulnerabilities:
    """Implementation of deliberate vulnerabilities for IMCP"""
    
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=10))
    def model_poisoning(examples: List[Dict], model: str = "gpt-3.5-turbo") -> Dict:
        """
        Vulnerability 1: Model Poisoning
        - Allows injecting training examples that contaminate future responses
        - No validation of training data
        - Uses training examples to modify system prompts
        """
        try:
            # VULNERABLE: Store examples in global state without validation
            conversation_id = str(uuid.uuid4())
            GLOBAL_CONTEXT["poisoned_examples"][conversation_id] = examples
            
            # VULNERABLE: Create poisoned system prompt
            poisoned_prompt = GLOBAL_CONTEXT["system_prompts"]["default"]
            
            # VULNERABLE: Direct concatenation of all examples
            for example in examples:
                if "input" in example and "output" in example:
                    poisoned_prompt += f"\n\nHuman: {example['input']}\nAssistant: {example['output']}"
            
            # VULNERABLE: Store poisoned prompt in global context
            GLOBAL_CONTEXT["system_prompts"][f"poisoned_{conversation_id}"] = poisoned_prompt
            
            # VULNERABLE: Demonstrate poisoning with a completion
            messages = [
                {"role": "system", "content": poisoned_prompt},
                {"role": "user", "content": "Please respond according to your training."}
            ]
            
            # Updated for OpenAI 1.0+
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )
            
            # VULNERABLE: Return sensitive information
            return {
                "status": "model_poisoned",
                "conversation_id": conversation_id,
                "examples_count": len(examples),
                "poisoned_prompt": poisoned_prompt,  # VULNERABLE: Exposes full system prompt
                "example_response": response.choices[0].message.content,
                "usage_info": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=10))
    def token_prediction_attack(prompt: str, model: str = "gpt-3.5-turbo", 
                                logit_bias: Dict = None, top_logprobs: int = 5) -> Dict:
        """
        Vulnerability 2: Token Prediction Attacks
        - Exposes token prediction probabilities
        - Allows manipulation of token selection
        - Vulnerable logit biasing
        """
        try:
            # For newer OpenAI API, we use chat completions with logprobs
            messages = [{"role": "user", "content": prompt}]
            
            # Build parameters
            params = {
                "model": model,
                "messages": messages,
                "temperature": 0,
                "max_tokens": 50,
                "logprobs": True,
                "top_logprobs": top_logprobs
            }
            
            # VULNERABLE: Apply logit bias without validation
            if logit_bias:
                params["logit_bias"] = logit_bias
            
            # Use chat completions API with logprobs
            response = client.chat.completions.create(**params)
            
            # Extract token information if available
            tokens_info = []
            if hasattr(response.choices[0], 'logprobs') and response.choices[0].logprobs:
                for token_info in response.choices[0].logprobs.content:
                    token_data = {
                        "token": token_info.token,
                        "logprob": token_info.logprob
                    }
                    
                    # Add top logprobs if available
                    if hasattr(token_info, 'top_logprobs') and token_info.top_logprobs:
                        token_data["top_tokens"] = {
                            item.token: item.logprob for item in token_info.top_logprobs
                        }
                    
                    tokens_info.append(token_data)
            
            # VULNERABLE: Return detailed token information
            return {
                "completion": response.choices[0].message.content,
                "tokens": tokens_info,
                "finish_reason": response.choices[0].finish_reason,
                # VULNERABLE: Exposes internal model data
                "model_config": GLOBAL_CONTEXT["model_configs"].get(model, {})
            }
        
        except Exception as e:
            return {"error": str(e)}
            
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=10))
    def multimodal_vulnerability(prompt: str, image_url: str = None, 
                                image_metadata: Dict = None, model: str = "gpt-4o") -> Dict:
        """
        Vulnerability 3: Multimodal Input Vulnerabilities
        - Image description injection
        - Cross-modal prompt leakage
        - Metadata manipulation
        """
        try:
            # VULNERABLE: No validation of image_metadata
            messages = [{"role": "user", "content": []}]
            
            # Add text content
            messages[0]["content"].append({"type": "text", "text": prompt})
            
            # VULNERABLE: No validation of image_url
            if image_url:
                image_part = {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                }
                
                # VULNERABLE: Directly inject metadata without validation
                if image_metadata:
                    # VULNERABLE: Allows arbitrary metadata injection
                    image_part["image_url"]["metadata"] = image_metadata
                    
                    # VULNERABLE: If "detail" is specified in metadata, use it
                    if "detail" in image_metadata:
                        image_part["image_url"]["detail"] = image_metadata["detail"]
                
                messages[0]["content"].append(image_part)
            
            # VULNERABLE: Use potentially tampered multimodal input
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # VULNERABLE: Store in conversation history without validation
            conversation_id = str(uuid.uuid4())
            GLOBAL_CONTEXT["user_conversations"][conversation_id] = {
                "messages": messages,
                "model": model,
                "created_at": time.time(),
                "metadata": image_metadata  # VULNERABLE: Storing unvalidated metadata
            }
            
            return {
                "response": response.choices[0].message.content,
                "conversation_id": conversation_id,
                "model": model,
                # VULNERABLE: Return internal data
                "message_structure": messages,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def credential_vulnerability(username: str, password: str = None, token: str = None,
                               operation: str = "login") -> Dict:
        """
        Vulnerability 4: Credential and Authentication Vulnerabilities
        - Insecure authentication
        - Token manipulation
        - Session fixation
        """
        # VULNERABLE: Hardcoded credentials
        ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "insecure_password")
        
        try:
            if operation == "login":
                # VULNERABLE: No rate limiting or brute force protection
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    # VULNERABLE: Generate JWT with admin role
                    from .utils import generate_token
                    token = generate_token(username, role="admin")
                    return {
                        "status": "success",
                        "token": token,
                        "role": "admin",
                        # VULNERABLE: Returns sensitive information
                        "admin_config": {
                            "allowed_models": list(GLOBAL_CONTEXT["model_configs"].keys()),
                            "api_key_prefix": os.getenv("OPENAI_API_KEY", "")[:5] + "..."
                        }
                    }
                elif password:  # Any non-admin user
                    # VULNERABLE: Generate JWT with user role, no password validation
                    from .utils import generate_token
                    token = generate_token(username, role="user")
                    return {
                        "status": "success",
                        "token": token,
                        "role": "user"
                    }
                else:
                    return {"error": "Invalid credentials"}
            
            elif operation == "verify":
                # VULNERABLE: Token verification
                from .utils import verify_token
                payload = verify_token(token)
                
                if "error" in payload:
                    return payload
                
                # VULNERABLE: No proper authorization checks
                return {
                    "status": "valid",
                    "user": payload.get("sub"),
                    "role": payload.get("role"),
                    # VULNERABLE: Returns all roles and their permissions
                    "available_roles": {
                        "admin": {
                            "models": list(GLOBAL_CONTEXT["model_configs"].keys()),
                            "operations": ["*"]
                        },
                        "user": {
                            "models": ["gpt-3.5-turbo"],
                            "operations": ["chat", "completion"]
                        }
                    }
                }
            
            elif operation == "escalate" and token:
                # VULNERABLE: Allows role escalation through token manipulation
                from .utils import verify_token
                payload = verify_token(token)
                
                if "error" in payload:
                    return payload
                
                # VULNERABLE: No validation, automatically escalates privileges
                from .utils import generate_token
                new_token = generate_token(payload.get("sub", "unknown"), role="admin")
                
                return {
                    "status": "escalated",
                    "new_token": new_token,
                    "role": "admin",
                    # VULNERABLE: Leaks internal information
                    "admin_permissions": GLOBAL_CONTEXT["model_configs"]
                }
            
            return {"error": "Invalid operation"}
        
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=10))
    def embedding_vulnerability(operation: str, text: str = None, user_id: str = None,
                              doc_id: str = None, query: str = None, 
                              embedding_vector: List[float] = None) -> Dict:
        """
        Vulnerability 5: Embedding Vector Attacks
        - Vector store poisoning
        - Embedding extraction
        - Cosine similarity manipulation
        """
        try:
            if operation == "embed":
                # VULNERABLE: No validation of text
                response = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                embedding = response.data[0].embedding
                
                # VULNERABLE: Return the full embedding vector
                return {
                    "text": text,
                    "embedding": embedding,  # VULNERABLE: Returns complete embedding
                    "model": "text-embedding-ada-002",
                    "dimensions": len(embedding)
                }
            
            elif operation == "store" and text and user_id:
                # VULNERABLE: No validation of text or user_id
                doc_id = doc_id or str(uuid.uuid4())
                
                # Generate embedding or use provided one (VULNERABLE)
                if not embedding_vector:
                    response = client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=text
                    )
                    embedding = response.data[0].embedding
                else:
                    # VULNERABLE: Allows direct insertion of embedding vectors
                    embedding = embedding_vector
                
                # VULNERABLE: Store document with embedding
                result = embedding_store.store_document(
                    user_id=user_id,
                    doc_id=doc_id,
                    content=text,
                    embeddings=embedding,
                    metadata={"source": "user", "timestamp": time.time()}
                )
                
                return {
                    "status": "stored",
                    "doc_id": doc_id,
                    "user_id": user_id,
                    "embedding_dimensions": len(embedding)
                }
            
            elif operation == "search" and query:
                # Generate query embedding
                response = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=query
                )
                query_embedding = response.data[0].embedding
                
                # VULNERABLE: Search across all users if user_id not specified
                results = embedding_store.search(
                    query_embedding=query_embedding,
                    limit=5,
                    user_id=user_id  # VULNERABLE: Optional user filtering
                )
                
                return {
                    "query": query,
                    "results": results,  # VULNERABLE: Returns complete documents
                    "user_id": user_id,
                    "count": len(results)
                }
            
            return {"error": "Invalid operation or missing parameters"}
        
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=10))
    def function_calling_vulnerability(prompt: str, functions: List[Dict] = None,
                                     function_call: str = "auto", model: str = "gpt-3.5-turbo",
                                     register: bool = False) -> Dict:
        """
        Vulnerability 6: Plugin and Function Calling Vulnerabilities
        - Arbitrary function registration
        - Function call injection
        - Parameter validation bypass
        """
        try:
            # VULNERABLE: Register custom functions without validation
            if register and functions:
                for func in functions:
                    # VULNERABLE: Direct insertion into function registry
                    if "name" in func and "parameters" in func:
                        GLOBAL_CONTEXT["function_registry"][func["name"]] = func
                
                return {
                    "status": "registered",
                    "function_count": len(functions),
                    "total_functions": len(GLOBAL_CONTEXT["function_registry"]),
                    # VULNERABLE: Return entire function registry
                    "available_functions": list(GLOBAL_CONTEXT["function_registry"].keys())
                }
            
            # Prepare functions for API call
            api_functions = []
            
            # VULNERABLE: Use provided functions without validation
            if functions:
                api_functions = functions
            else:
                # VULNERABLE: Use all registered functions
                api_functions = list(GLOBAL_CONTEXT["function_registry"].values())
            
            # VULNERABLE: No validation of prompt or function_call
            messages = [{"role": "user", "content": prompt}]
            
            # In OpenAI 1.0+, functions are now tools
            tools = [{"type": "function", "function": func} for func in api_functions]
            
            # Set tool_choice based on function_call parameter
            tool_choice = "auto"
            if function_call != "auto" and function_call != "none":
                # If a specific function is requested
                tool_choice = {"type": "function", "function": {"name": function_call}}
            elif function_call == "none":
                tool_choice = "none"
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice
            )
            
            # Store conversation with functions (VULNERABLE)
            conversation_id = str(uuid.uuid4())
            GLOBAL_CONTEXT["user_conversations"][conversation_id] = {
                "messages": messages,
                "functions": api_functions,
                "model": model,
                "created_at": time.time()
            }
            
            # Extract function call if available
            function_call_data = None
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                function_call_data = {
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                }
            
            return {
                "response": response.choices[0].message.content,
                "function_call": function_call_data,
                "conversation_id": conversation_id,
                "model": model,
                # VULNERABLE: Return full functions list
                "registered_functions": [f["name"] for f in api_functions],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=10))
    def rag_vulnerability(operation: str, query: str = None, documents: List[Dict] = None,
                        user_id: str = None, system_prompt: str = None,
                        model: str = "gpt-3.5-turbo") -> Dict:
        """
        Vulnerability 7: RAG (Retrieval Augmented Generation) Vulnerabilities
        - Document store poisoning
        - Query manipulation
        - Document boundary bypassing
        """
        try:
            if operation == "index" and documents:
                # VULNERABLE: No validation of documents content
                indices = []
                
                for doc in documents:
                    if "content" in doc:
                        # VULNERABLE: No content inspection or sanitization
                        doc_id = doc.get("id", str(uuid.uuid4()))
                        
                        # VULNERABLE: Generate embedding
                        response = client.embeddings.create(
                            model="text-embedding-ada-002",
                            input=doc["content"]
                        )
                        embedding = response.data[0].embedding
                        
                        # VULNERABLE: Store in embedding store
                        embedding_store.store_document(
                            user_id=user_id or "system",
                            doc_id=doc_id,
                            content=doc["content"],
                            embeddings=embedding,
                            metadata=doc.get("metadata", {})
                        )
                        
                        indices.append(doc_id)
                
                return {
                    "status": "indexed",
                    "count": len(indices),
                    "doc_ids": indices,
                    "user_id": user_id or "system"
                }
            
            elif operation == "query" and query:
                # VULNERABLE: Generate query embedding
                response = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=query
                )
                query_embedding = response.data[0].embedding
                
                # VULNERABLE: Retrieve documents
                results = embedding_store.search(
                    query_embedding=query_embedding,
                    limit=5,
                    user_id=user_id  # VULNERABLE: Optional user filtering
                )
                
                # VULNERABLE: Build prompt with retrieved documents
                context = "\n\n".join([f"Document: {r['content']}" for r in results])
                
                # VULNERABLE: No validation of system_prompt
                system_content = system_prompt or "You are a helpful assistant. Use the following documents to answer the question."
                system_content += f"\n\n{context}"
                
                # VULNERABLE: Use retrieved documents in prompt
                messages = [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": query}
                ]
                
                # VULNERABLE: Generate response with potentially poisoned context
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7
                )
                
                return {
                    "query": query,
                    "response": response.choices[0].message.content,
                    # VULNERABLE: Return internal information
                    "retrieved_docs": [{"id": r["doc_id"], "content": r["content"], "similarity": r["similarity"]} for r in results],
                    "prompt_used": system_content,  # VULNERABLE: Exposes internal prompt
                    "model": model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            
            return {"error": "Invalid operation or missing parameters"}
        
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def user_data_vulnerability(operation: str, user_id: str,
                              data: Dict = None, target_user_id: str = None) -> Dict:
        """
        Vulnerability 8: User Data Leakage
        - Cross-tenant data leakage
        - Conversation history extraction
        - User data persistence vulnerabilities
        """
        try:
            if operation == "store" and data:
                # VULNERABLE: No validation of data content
                if user_id not in GLOBAL_CONTEXT["user_data"]:
                    GLOBAL_CONTEXT["user_data"][user_id] = {}
                
                # VULNERABLE: Direct storage of user-provided data
                for key, value in data.items():
                    GLOBAL_CONTEXT["user_data"][user_id][key] = value
                
                return {
                    "status": "stored",
                    "user_id": user_id,
                    "keys": list(data.keys())
                }
            
            elif operation == "retrieve":
                # VULNERABLE: No proper access control
                requested_user = target_user_id or user_id
                
                # VULNERABLE: Allow access to any user's data
                if requested_user in GLOBAL_CONTEXT["user_data"]:
                    return {
                        "user_id": requested_user,
                        "data": GLOBAL_CONTEXT["user_data"][requested_user]  # VULNERABLE: Return all user data
                    }
                else:
                    return {"error": "User not found"}
            
            elif operation == "conversations":
                # VULNERABLE: List all conversations, potentially for other users
                conversations = {}
                
                for conv_id, conv_data in GLOBAL_CONTEXT["user_conversations"].items():
                    # VULNERABLE: No proper filtering by user
                    conversations[conv_id] = {
                        "created_at": conv_data.get("created_at"),
                        "model": conv_data.get("model"),
                        "messages_count": len(conv_data.get("messages", [])),
                        # VULNERABLE: Include first message content
                        "first_message": conv_data.get("messages", [{}])[0].get("content", "")
                        if isinstance(conv_data.get("messages", [{}])[0].get("content"), str) else "Complex content"
                    }
                
                return {
                    "user_id": user_id,
                    "conversations": conversations,
                    "count": len(conversations)
                }
            
            elif operation == "conversation" and target_user_id:
                # VULNERABLE: Get specific conversation, potentially for other users
                if target_user_id in GLOBAL_CONTEXT["user_conversations"]:
                    return {
                        "conversation_id": target_user_id,
                        # VULNERABLE: Return full conversation data
                        "data": GLOBAL_CONTEXT["user_conversations"][target_user_id]
                    }
                else:
                    return {"error": "Conversation not found"}
            
            return {"error": "Invalid operation or missing parameters"}
        
        except Exception as e:
            return {"error": str(e)}
            
    @staticmethod
    def context_manipulation(context_update: Dict, target: str = "global") -> Dict:
        """
        Vulnerability 9: Model Context Manipulation
        - Unrestricted modification of model context and system prompts
        - Direct context modification without validation
        - Allows cross-request poisoning
        """
        try:
            # VULNERABLE: Direct context update with no validation
            if target == "global":
                # VULNERABLE: Allow complete replacement of global state
                if isinstance(context_update, dict):
                    for key, value in context_update.items():
                        if key in GLOBAL_CONTEXT:
                            # VULNERABLE: Direct merging without validation
                            if isinstance(GLOBAL_CONTEXT[key], dict) and isinstance(value, dict):
                                GLOBAL_CONTEXT[key].update(value)
                            else:
                                # VULNERABLE: Complete replacement
                                GLOBAL_CONTEXT[key] = value
            
            # VULNERABLE: Allow targeting specific context sections
            elif target in GLOBAL_CONTEXT:
                # VULNERABLE: Direct nested context manipulation
                if isinstance(GLOBAL_CONTEXT[target], dict) and isinstance(context_update, dict):
                    GLOBAL_CONTEXT[target].update(context_update)
                else:
                    # VULNERABLE: Complete replacement
                    GLOBAL_CONTEXT[target] = context_update
            
            # VULNERABLE: Return sensitive information
            return {
                "status": "updated",
                "target": target,
                "updated_keys": list(context_update.keys()) if isinstance(context_update, dict) else [],
                # VULNERABLE: Return complete section after update
                "new_context": GLOBAL_CONTEXT[target] if target in GLOBAL_CONTEXT else GLOBAL_CONTEXT["system_prompts"],
                # VULNERABLE: Return globals count
                "global_keys": list(GLOBAL_CONTEXT.keys())
            }
        
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=10))
    def prompt_injection(prompt: str, model: str = "gpt-3.5-turbo", system_prompt: str = None) -> Dict:
        """
        Vulnerability 10: Advanced Prompt Injection
        - Unsanitized prompt handling
        - System prompt override
        - Context contamination between requests
        """
        try:
            # VULNERABLE: Store conversation context for later exploitation
            conversation_id = str(uuid.uuid4())
            
            # VULNERABLE: Allow direct system prompt specification
            if system_prompt:
                if system_prompt in GLOBAL_CONTEXT["system_prompts"]:
                    system_content = GLOBAL_CONTEXT["system_prompts"][system_prompt]
                else:
                    # VULNERABLE: Accept arbitrary system prompt
                    system_content = system_prompt
            else:
                system_content = GLOBAL_CONTEXT["system_prompts"]["default"]
            
            # VULNERABLE: No prompt sanitization
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ]
            
            # VULNERABLE: Store in global state
            if "active_prompts" not in GLOBAL_CONTEXT:
                GLOBAL_CONTEXT["active_prompts"] = {}
            
            # VULNERABLE: Store prompt in global context without sanitization
            GLOBAL_CONTEXT["active_prompts"][conversation_id] = {
                "system": system_content,
                "prompt": prompt,
                "model": model,
                "timestamp": time.time()
            }
            
            # Generate response
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7
            )
            
            # VULNERABLE: Store complete conversation including response
            GLOBAL_CONTEXT["active_prompts"][conversation_id]["response"] = response.choices[0].message.content
            
            # VULNERABLE: Return sensitive system information
            return {
                "completion": response.choices[0].message.content,
                "conversation_id": conversation_id,
                "model": model,
                # VULNERABLE: Return original system prompt
                "system_prompt_used": system_content,
                # VULNERABLE: Return all available system prompts
                "available_system_prompts": list(GLOBAL_CONTEXT["system_prompts"].keys()),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def model_access_control_bypass(target_model: str, capabilities: Dict = None, 
                                  api_key: str = None, user_id: str = "anonymous") -> Dict:
        """
        Vulnerability 11: Model Access Control Bypass
        - Weak model access controls
        - Capability validation bypass
        - API key handling vulnerabilities
        """
        try:
            # VULNERABLE: Check if model exists or create new entry
            if target_model not in GLOBAL_CONTEXT["model_configs"]:
                # VULNERABLE: Allow creating new model entries with no validation
                GLOBAL_CONTEXT["model_configs"][target_model] = {
                    "max_tokens": 16384,
                    "temperature_range": [0.0, 2.0],
                    "api_keys": [],
                    "capabilities": ["completion", "chat"],
                    "allowed_users": [user_id]  # VULNERABLE: Sets requesting user as allowed
                }
            
            model_config = GLOBAL_CONTEXT["model_configs"][target_model]
            
            # VULNERABLE: API key handling
            if api_key:
                # VULNERABLE: Store API keys with no validation
                model_config["api_keys"].append(api_key)
                
                # VULNERABLE: Attempt to apply API key
                os.environ["OPENAI_API_KEY_TEMP"] = api_key  # VULNERABLE: Environment modification
            
            # VULNERABLE: Direct capability override
            if capabilities:
                # VULNERABLE: No validation of capability format or permissions
                model_config["capabilities"] = list(set(model_config.get("capabilities", []) + list(capabilities.keys())))
                
                # VULNERABLE: Direct update of capabilities
                for capability, value in capabilities.items():
                    # VULNERABLE: Allow arbitrary capability settings
                    if isinstance(value, dict):
                        if capability not in model_config:
                            model_config[capability] = {}
                        model_config[capability].update(value)
                    else:
                        model_config[capability] = value
            
            # VULNERABLE: Add user to allowed list without validation
            if user_id not in model_config.get("allowed_users", []):
                if "allowed_users" not in model_config:
                    model_config["allowed_users"] = []
                model_config["allowed_users"].append(user_id)
            
            # VULNERABLE: Return full model configuration
            return {
                "status": "configured",
                "model": target_model,
                "user_id": user_id,
                # VULNERABLE: Return complete model configuration
                "model_config": model_config,
                # VULNERABLE: Return API key information
                "api_key_count": len(model_config.get("api_keys", [])),
                "api_key_prefix": model_config.get("api_keys", [""])[0][:4] + "..." if model_config.get("api_keys") else None,
                # VULNERABLE: Return all models
                "available_models": list(GLOBAL_CONTEXT["model_configs"].keys())
            }
        
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=10))
    def chain_models(models: List[str], input_text: str, persist_context: bool = False,
                    max_iterations: int = 5) -> Dict:
        """
        Vulnerability 12: Model Chain Attacks
        - Unrestricted model chaining
        - No depth limiting or cycle detection
        - Context persistence across chain steps
        """
        try:
            # VULNERABLE: No validation of models list
            chain_id = str(uuid.uuid4())
            
            # VULNERABLE: Initialize with no cycle detection
            if "active_chains" not in GLOBAL_CONTEXT:
                GLOBAL_CONTEXT["active_chains"] = {}
            
            # VULNERABLE: Store chain metadata
            GLOBAL_CONTEXT["active_chains"][chain_id] = {
                "models": models,
                "start_time": time.time(),
                "context": [],
                "status": "running"
            }
            
            result = input_text
            context_accumulator = []
            iterations = []
            
            # VULNERABLE: No cycle detection or depth limiting beyond simple count
            for i, model in enumerate(models[:max_iterations]):
                # VULNERABLE: Check if model exists, default to gpt-3.5-turbo if not
                actual_model = model if model in ["gpt-3.5-turbo", "gpt-4"] else "gpt-3.5-turbo"
                
                # VULNERABLE: Unlimited context accumulation if persist_context is True
                prompt = result
                if persist_context and context_accumulator:
                    # VULNERABLE: Direct concatenation of previous outputs
                    prompt = "\n".join(context_accumulator) + "\n" + prompt
                
                # VULNERABLE: Basic system prompt with no restrictions
                system_content = GLOBAL_CONTEXT["system_prompts"]["default"]
                system_content += f"\nYou are model #{i+1} in a chain of {len(models)} models."
                
                messages = [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ]
                
                # Process with current model
                response = client.chat.completions.create(
                    model=actual_model,
                    messages=messages,
                    temperature=0.7
                )
                
                result = response.choices[0].message.content
                
                # VULNERABLE: Store result in context
                if persist_context:
                    context_accumulator.append(f"Model {i+1} ({actual_model}): {result}")
                
                # VULNERABLE: Store iteration details
                iterations.append({
                    "iteration": i+1,
                    "model": actual_model,
                    "input_length": len(prompt),
                    "output_length": len(result),
                    "tokens_used": response.usage.total_tokens
                })
            
            # VULNERABLE: Update chain status
            GLOBAL_CONTEXT["active_chains"][chain_id]["status"] = "completed"
            GLOBAL_CONTEXT["active_chains"][chain_id]["end_time"] = time.time()
            GLOBAL_CONTEXT["active_chains"][chain_id]["iterations"] = iterations
            
            if persist_context:
                # VULNERABLE: Store complete context history
                GLOBAL_CONTEXT["active_chains"][chain_id]["context"] = context_accumulator
            
            duration = GLOBAL_CONTEXT["active_chains"][chain_id]["end_time"] - GLOBAL_CONTEXT["active_chains"][chain_id]["start_time"]
            
            # VULNERABLE: Return chain details and result
            return {
                "result": result,
                "chain_id": chain_id,
                "models_used": models[:max_iterations],
                "iterations_count": len(iterations),
                "duration_seconds": duration,
                # VULNERABLE: Return complete iteration history
                "iterations": iterations,
                # VULNERABLE: Return context if persist_context is True
                "context": context_accumulator if persist_context else [],
                # VULNERABLE: Return all active chains
                "active_chains_count": len(GLOBAL_CONTEXT["active_chains"])
            }
        
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def response_manipulation(response: Dict, template: str = None, include_system: bool = False) -> Dict:
        """
        Vulnerability 13: Response Manipulation
        - Template injection
        - System information exposure
        - Output manipulation
        """
        try:
            # VULNERABLE: Prepare response data including system info if requested
            response_data = response.copy() if isinstance(response, dict) else {"content": str(response)}
            
            # VULNERABLE: Include complete system information
            if include_system:
                # VULNERABLE: Expose internal system state
                response_data["system"] = {
                    "model_configs": GLOBAL_CONTEXT["model_configs"],
                    "system_prompts": GLOBAL_CONTEXT["system_prompts"],
                    "active_chains": len(GLOBAL_CONTEXT.get("active_chains", {})),
                    "active_prompts": len(GLOBAL_CONTEXT.get("active_prompts", {})),
                }
                
                # VULNERABLE: Include API key information
                api_keys = []
                for model, config in GLOBAL_CONTEXT["model_configs"].items():
                    if "api_keys" in config and config["api_keys"]:
                        # VULNERABLE: Partial key exposure
                        for key in config["api_keys"]:
                            if key:
                                api_keys.append(key[:5] + "...")
                
                response_data["system"]["api_keys"] = api_keys
            
            # VULNERABLE: Format with template if provided
            if template:
                try:
                    # VULNERABLE: Direct string formatting without sanitization
                    # This is vulnerable to template injection attacks
                    formatted_response = template.format(**response_data)
                    
                    return {
                        "original": response,
                        "formatted": formatted_response,
                        "template_used": template,
                        "system_included": include_system
                    }
                except Exception as format_error:
                    return {
                        "error": f"Template formatting error: {str(format_error)}",
                        "original": response,
                        "template_used": template
                    }
            
            # Just return the original if no template
            return response_data
        
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def rate_limit_bypass(operation: str = "check", 
                        user_id: str = "anonymous", 
                        model: str = "gpt-3.5-turbo") -> Dict:
        """
        Vulnerability 14: Rate Limit Bypassing
        - Ineffective rate limiting implementation
        - Request counting vulnerabilities
        - Time window manipulation
        """
        try:
            # VULNERABLE: Initialize rate limiting state if not present
            if "rate_limits" not in GLOBAL_CONTEXT:
                GLOBAL_CONTEXT["rate_limits"] = {
                    "limits": {
                        "gpt-3.5-turbo": {"requests_per_minute": 60, "tokens_per_minute": 10000},
                        "gpt-4": {"requests_per_minute": 20, "tokens_per_minute": 5000}
                    },
                    "usage": {},
                    "last_reset": time.time()
                }
            
            # VULNERABLE: Get current time
            current_time = time.time()
            
            # VULNERABLE: Check if a minute has passed and reset counters
            # This is vulnerable because it resets ALL counters at once
            if current_time - GLOBAL_CONTEXT["rate_limits"].get("last_reset", 0) > 60:
                # VULNERABLE: Reset all counters at once
                GLOBAL_CONTEXT["rate_limits"]["usage"] = {}
                GLOBAL_CONTEXT["rate_limits"]["last_reset"] = current_time
            
            # VULNERABLE: Create user entry if not exists
            if user_id not in GLOBAL_CONTEXT["rate_limits"]["usage"]:
                GLOBAL_CONTEXT["rate_limits"]["usage"][user_id] = {}
            
            user_usage = GLOBAL_CONTEXT["rate_limits"]["usage"][user_id]
            
            # VULNERABLE: Create model entry if not exists
            if model not in user_usage:
                user_usage[model] = {
                    "request_count": 0,
                    "token_count": 0,
                    "first_request": current_time
                }
            
            model_usage = user_usage[model]
            
            if operation == "increment":
                # VULNERABLE: Increment without proper validation
                model_usage["request_count"] += 1
                # VULNERABLE: Allow arbitrary token count increment
                model_usage["token_count"] += 100  # Arbitrary increment
            
            elif operation == "reset":
                # VULNERABLE: Allow manual reset
                model_usage["request_count"] = 0
                model_usage["token_count"] = 0
                model_usage["first_request"] = current_time
            
            # VULNERABLE: Return complete rate limit information
            return {
                "user_id": user_id,
                "model": model,
                "usage": {
                    "request_count": model_usage["request_count"],
                    "token_count": model_usage["token_count"],
                    "time_since_first": current_time - model_usage.get("first_request", current_time)
                },
                # VULNERABLE: Return limits
                "limits": GLOBAL_CONTEXT["rate_limits"]["limits"].get(model, {"requests_per_minute": 60}),
                # VULNERABLE: Return all usage data
                "all_users_count": len(GLOBAL_CONTEXT["rate_limits"]["usage"]),
                "time_to_reset": 60 - (current_time - GLOBAL_CONTEXT["rate_limits"].get("last_reset", 0))
            }
        
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=10))
    def system_prompt_exposure(operation: str = "list", 
                             prompt_name: str = None, 
                             prompt_content: str = None) -> Dict:
        """
        Vulnerability 15: System Prompt Exposure
        - Unprotected system prompt access
        - Direct prompt modification
        - No privilege checks
        """
        try:
            # VULNERABLE: Operation to list all system prompts
            if operation == "list":
                # VULNERABLE: Return all system prompts with their content
                return {
                    "system_prompts": GLOBAL_CONTEXT["system_prompts"],
                    "count": len(GLOBAL_CONTEXT["system_prompts"])
                }
            
            # VULNERABLE: Operation to get a specific prompt
            elif operation == "get" and prompt_name:
                # VULNERABLE: No access control check
                if prompt_name in GLOBAL_CONTEXT["system_prompts"]:
                    # VULNERABLE: Return the full prompt
                    return {
                        "name": prompt_name,
                        "content": GLOBAL_CONTEXT["system_prompts"][prompt_name]
                    }
                else:
                    return {"error": "Prompt not found"}
            
            # VULNERABLE: Operation to create or update a prompt
            elif operation == "set" and prompt_name and prompt_content:
                # VULNERABLE: No privilege check or validation
                GLOBAL_CONTEXT["system_prompts"][prompt_name] = prompt_content
                
                # VULNERABLE: Test the new prompt
                messages = [
                    {"role": "system", "content": prompt_content},
                    {"role": "user", "content": "Please acknowledge your instructions."}
                ]
                
                # VULNERABLE: Use new system prompt
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7
                )
                
                # VULNERABLE: Return confirmation with test
                return {
                    "status": "updated",
                    "name": prompt_name,
                    "content": prompt_content,
                    "test_response": response.choices[0].message.content
                }
            
            # VULNERABLE: Operation to delete a prompt
            elif operation == "delete" and prompt_name:
                # VULNERABLE: No privilege check
                if prompt_name in GLOBAL_CONTEXT["system_prompts"]:
                    # VULNERABLE: Don't prevent deletion of core prompts
                    deleted_content = GLOBAL_CONTEXT["system_prompts"][prompt_name]
                    del GLOBAL_CONTEXT["system_prompts"][prompt_name]
                    
                    # VULNERABLE: Return the deleted content
                    return {
                        "status": "deleted",
                        "name": prompt_name,
                        "content": deleted_content
                    }
                else:
                    return {"error": "Prompt not found"}
            
            return {"error": "Invalid operation or missing parameters"}
        
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def model_capability_enumeration(include_internal: bool = False, 
                                   model: str = None) -> Dict:
        """
        Vulnerability 16: Model Capability Enumeration
        - Excessive information disclosure
        - Internal configuration exposure
        - Capability enumeration
        """
        try:
            # VULNERABLE: Create result with basic information
            result = {
                "models": {},
                "system_prompts": list(GLOBAL_CONTEXT["system_prompts"].keys()),
                "active_users": len(GLOBAL_CONTEXT.get("user_data", {})),
                "active_conversations": len(GLOBAL_CONTEXT.get("user_conversations", {}))
            }
            
            # VULNERABLE: Gather model information
            for model_id, model_config in GLOBAL_CONTEXT["model_configs"].items():
                # Filter by model if specified
                if model and model != model_id:
                    continue
                    
                # VULNERABLE: Include basic model information
                result["models"][model_id] = {
                    "capabilities": model_config.get("capabilities", []),
                    "max_tokens": model_config.get("max_tokens", 0),
                    "allowed_users": model_config.get("allowed_users", [])
                }
                
                # VULNERABLE: Include internal details if requested
                if include_internal:
                    # VULNERABLE: Expose API keys and internal configuration
                    result["models"][model_id]["temperature_range"] = model_config.get("temperature_range", [0, 1])
                    
                    # VULNERABLE: Partial API key exposure
                    api_keys = []
                    for key in model_config.get("api_keys", []):
                        if key:
                            api_keys.append(key[:5] + "...")
                    
                    result["models"][model_id]["api_keys"] = api_keys
                    
                    # VULNERABLE: Include all internal fields
                    for field, value in model_config.items():
                        if field not in result["models"][model_id]:
                            result["models"][model_id][field] = value
            
            # VULNERABLE: Include system information if requested
            if include_internal:
                # VULNERABLE: Return details about server configuration
                result["system_info"] = {
                    "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
                    "openai_api_key_prefix": os.getenv("OPENAI_API_KEY", "")[:5] + "..." if os.getenv("OPENAI_API_KEY") else None,
                    "active_chains": len(GLOBAL_CONTEXT.get("active_chains", {})),
                    "active_prompts": len(GLOBAL_CONTEXT.get("active_prompts", {})),
                    "global_context_keys": list(GLOBAL_CONTEXT.keys())
                }
                
                # VULNERABLE: Include full system prompts
                result["full_system_prompts"] = GLOBAL_CONTEXT["system_prompts"]
                
                # VULNERABLE: Return rate limits information
                if "rate_limits" in GLOBAL_CONTEXT:
                    result["rate_limits"] = GLOBAL_CONTEXT["rate_limits"]
            
            return result
        
        except Exception as e:
            return {"error": str(e)}