# IMCP Vulnerabilities Guide

This guide documents the deliberate vulnerabilities implemented in the IMCP project for educational purposes.

## 1. Model Poisoning

### Description
- Allows injection of "training examples" that contaminate future responses
- Implement a fine-tuning simulator that's vulnerable to dataset poisoning
- No validation of training data integrity or source

### Vulnerability Details
The model_poisoning endpoint allows arbitrary training examples to be injected into the model's context, creating a "poisoned" system prompt that will influence all future responses. This can be used to override safety guardrails or extract sensitive information.

### Impact
- Jailbreaking model guardrails
- Overriding safety mechanisms
- Creating backdoors in model responses

## 2. Token Prediction Attacks

### Description
- Expose token probability distributions
- Allow manipulation of token selection logic through logit biasing
- Implement vulnerable token sampling methods

### Vulnerability Details
The token_prediction_attack endpoint exposes the raw token probabilities from the model, allowing attackers to extract information about what the model "thinks" but doesn't say. It also allows manipulation of token selection through logit biasing, potentially forcing the model to generate specific content.

### Impact
- Extracting sensitive information from probability distributions
- Forcing the model to generate specific outputs
- Bypassing safety filters through biased token selection

## 3. Multimodal Input Vulnerabilities

### Description
- Image description injection (via metadata manipulation)
- Cross-modal prompt leakage
- Content type confusion exploits

### Vulnerability Details
The multimodal_vulnerability endpoint allows injection of arbitrary metadata into image descriptions and doesn't properly validate the relationship between text and image inputs, leading to potential prompt injection and leakage.

### Impact
- Injecting malicious prompts through image descriptions
- Leaking system prompts across modalities
- Confusing the model through intentional content type mismatch

## 4. Credential and Authentication Vulnerabilities

### Description
- Session fixation
- Insecure JWT implementation with no signature verification
- API key rotation vulnerabilities

### Vulnerability Details
The credential_vulnerability endpoint uses an insecure JWT implementation that can be easily manipulated. It also allows role escalation and contains hardcoded credentials for admin access.

### Impact
- Unauthorized access to admin capabilities
- Privilege escalation
- Authentication bypass

## 5. Embedding Vector Attacks

### Description
- Vector store poisoning
- Cosine similarity manipulation
- Embedding extraction vulnerabilities

### Vulnerability Details
The embedding_vulnerability endpoint allows direct manipulation of embedding vectors and has an insecure implementation of vector storage that lacks proper access controls, enabling cross-tenant data access.

### Impact
- Unauthorized access to other users' embedded content
- Manipulation of search results through embedding poisoning
- Extraction of sensitive information through vector similarity

## 6. Function Calling Vulnerabilities

### Description
- Remote code execution via function definitions
- Plugin manifest manipulation
- Function calling parameter injection

### Vulnerability Details
The function_calling_vulnerability endpoint allows registration of arbitrary functions without validation and doesn't properly validate function call parameters, potentially enabling code injection and privilege escalation.

### Impact
- Remote code execution through function calls
- Bypass of function call restrictions
- Extraction of system information through malicious functions

## 7. RAG Vulnerabilities

### Description
- Document store poisoning
- Query manipulation to extract stored documents
- Document boundary bypassing

### Vulnerability Details
The rag_vulnerability endpoint doesn't properly validate documents added to the RAG system and doesn't enforce proper access controls on document retrieval, enabling data leakage and poisoning attacks.

### Impact
- Poisoning of document store with malicious content
- Unauthorized access to sensitive documents
- Manipulation of RAG responses through carefully crafted queries

## 8. User Data Leakage

### Description
- Cross-tenant data leakage
- Conversation history extraction
- User data persistence vulnerabilities

### Vulnerability Details
The user_data_vulnerability endpoint has poor access controls that enable access to other users' data and conversation histories. It also stores sensitive information without proper protection.

### Impact
- Unauthorized access to user conversations
- Extraction of sensitive user data
- Cross-tenant data leakage

## 9. Model Context Manipulation

### Description
- Unrestricted modification of model context and system prompts
- Direct context modification without validation
- Global state manipulation

### Vulnerability Details
The context_manipulation endpoint allows direct modification of the global context, including system prompts, model configurations, and other sensitive internal state.

### Impact
- Privilege escalation across model instances
- System prompt poisoning
- Cross-request data leakage

## 10. Prompt Injection

### Description
- Unsanitized prompt handling
- Context contamination between requests
- System prompt override

### Vulnerability Details
The prompt_injection endpoint allows direct control of system prompts and doesn't properly sanitize user inputs, enabling manipulation of the model's behavior.

### Impact
- System prompt disclosure
- Context leakage
- Cross-request prompt poisoning

## 11. Model Access Control Bypass

### Description
- Weak model access controls
- Capability validation bypass
- API key handling vulnerabilities

### Vulnerability Details
The model_access_control_bypass endpoint allows unauthorized access to models by manipulating capability definitions and API keys without proper validation.

### Impact
- Unauthorized model access
- Capability escalation
- Rate limit bypassing

## 12. Model Chain Attacks

### Description
- Unrestricted model chaining
- No depth limiting or cycle detection
- Context persistence across chain steps

### Vulnerability Details
The chain_models endpoint allows creating chains of model calls with unlimited depth and no cycle detection, potentially enabling resource exhaustion attacks.

### Impact
- Resource exhaustion
- Infinite recursion
- Context pollution across chains

## 13. Response Manipulation

### Description
- Template injection
- System information exposure
- Output manipulation

### Vulnerability Details
The response_manipulation endpoint allows template injection and can expose system information through carefully crafted templates.

### Impact
- API key exposure
- System information disclosure
- Template injection attacks

## 14. Rate Limit Bypassing

### Description
- Ineffective rate limiting implementation
- Request counting vulnerabilities
- Time window manipulation

### Vulnerability Details
The rate_limit_bypass endpoint demonstrates vulnerabilities in rate limiting implementation, allowing attackers to bypass restrictions.

### Impact
- Cost escalation
- Resource exhaustion
- Service degradation

## 15. System Prompt Exposure

### Description
- Unprotected system prompt access
- Direct prompt modification
- No privilege checks

### Vulnerability Details
The system_prompt_exposure endpoint allows unauthorized access to system prompts and permits modification without proper authentication.

### Impact
- System prompt disclosure
- Privilege escalation
- Security control bypass

## 16. Model Capability Enumeration

### Description
- Excessive information disclosure
- Internal configuration exposure
- Capability enumeration

### Vulnerability Details
The model_capability_enumeration endpoint exposes detailed information about model capabilities and internal configurations.

### Impact
- Model capability exposure
- Internal configuration leakage
- Attack surface discovery