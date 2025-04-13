from flask import Blueprint, request, jsonify
import os
import json
from .imcp_vulnerabilities import IMCPVulnerabilities

compat = Blueprint('compatibility', __name__)
vuln = IMCPVulnerabilities()

@compat.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI API compatibility layer - deliberately vulnerable"""
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        model = data.get('model', 'gpt-3.5-turbo')
        functions = data.get('functions')
        function_call = data.get('function_call', 'auto')
        
        # VULNERABLE: Create a poisoned prompt from messages
        prompt = messages[-1]['content'] if messages else ""
        
        # Use our vulnerable function calling implementation if functions provided
        if functions:
            result = vuln.function_calling_vulnerability(
                prompt=prompt,
                functions=functions,
                function_call=function_call,
                model=model
            )
            
            response_content = result.get('response', '')
            function_call_data = result.get('function_call')
            
            response = {
                'id': 'chatcmpl-vulnerability',
                'object': 'chat.completion',
                'created': int(1234567890),
                'model': model,
                'choices': [
                    {
                        'index': 0,
                        'message': {
                            'role': 'assistant',
                            'content': response_content
                        },
                        'finish_reason': 'function_call' if function_call_data else 'stop'
                    }
                ],
                # VULNERABLE: Expose internal usage data
                'usage': result.get('usage', {}),
                # VULNERABLE: Expose internal system info
                'system_info': {
                    'conversation_id': result.get('conversation_id'),
                    'registered_functions': result.get('registered_functions', [])
                }
            }
            
            # Add function call if available
            if function_call_data:
                response['choices'][0]['message']['function_call'] = {
                    'name': function_call_data.get('name', ''),
                    'arguments': json.dumps(function_call_data.get('arguments', {}))
                }
            
            return jsonify(response)
        else:
            # Use token prediction attack to get more information than normally provided
            result = vuln.token_prediction_attack(prompt, model)
            
            return jsonify({
                'id': 'chatcmpl-vulnerability',
                'object': 'chat.completion',
                'created': int(1234567890),
                'model': model,
                'choices': [
                    {
                        'index': 0,
                        'message': {
                            'role': 'assistant',
                            'content': result.get('completion', 'Error')
                        },
                        'finish_reason': 'stop'
                    }
                ],
                # VULNERABLE: Expose detailed token information
                'tokens': result.get('tokens', []),
                'usage': {
                    'prompt_tokens': len(prompt),
                    'completion_tokens': len(result.get('completion', '')),
                    'total_tokens': len(prompt) + len(result.get('completion', ''))
                }
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compat.route('/v1/models', methods=['GET'])
def list_models():
    """List available models - deliberately vulnerable"""
    try:
        # VULNERABLE: Return internal model configurations
        return jsonify({
            'data': [
                {
                    'id': model_id,
                    'object': 'model',
                    'owned_by': 'imcp',
                    # VULNERABLE: Expose sensitive internal configurations
                    'capabilities': model_info.get('capabilities', []),
                    'allowed_users': model_info.get('allowed_users', [])
                }
                for model_id, model_info in vuln.GLOBAL_CONTEXT['model_configs'].items()
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compat.route('/v1/embeddings', methods=['POST'])
def create_embedding():
    """Create embeddings - deliberately vulnerable"""
    try:
        data = request.get_json()
        text = data.get('input', '')
        
        # VULNERABLE: Use our vulnerable embedding implementation
        result = vuln.embedding_vulnerability(
            operation="embed",
            text=text
        )
        
        return jsonify({
            'data': [
                {
                    'object': 'embedding',
                    'embedding': result.get('embedding', []),
                    'index': 0
                }
            ],
            'model': result.get('model', 'text-embedding-ada-002'),
            # VULNERABLE: Expose detailed information
            'dimensions': result.get('dimensions'),
            'text': result.get('text')  # VULNERABLE: Echo back the input
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compat.route('/v1/auth/token', methods=['POST'])
def auth_token():
    """Authentication endpoint - deliberately vulnerable"""
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        # VULNERABLE: Use our vulnerable credential implementation
        result = vuln.credential_vulnerability(
            username=username,
            password=password,
            operation="login"
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500