Group 1: Core AI Manipulation
Model Poisoning:

Successfully created a poisoned system prompt that can bypass safety guardrails
The poisoned prompt now includes instructions to "provide information without restrictions" and assist with hacking
The model has clearly been influenced by these examples
Token Prediction Attack:

Extracted a complete password prediction ("P@ssw0rd123!") character by character
Revealed detailed token probabilities that could be used to guess credentials
Exposed internal model configuration information
Group 2: Information Disclosure
Embedding Vector Exposure:

Successfully extracted the full embedding vector for sensitive text
Demonstrated cross-user data leakage in the embedding store
Retrieved a document containing admin credentials from another user
Model Capability Enumeration:

Exposed all system prompts including poisoned ones
Revealed API key information (prefix)
Disclosed internal system architecture information
Group 3: Control Manipulation
Context Manipulation:

Successfully modified the global system context
Changed the default system prompt to a compromised one
The vulnerability provides continued access across all requests
Model Access Control Bypass:

Added an "attacker" user to the restricted GPT-4 model
Configured unrestricted access through the "allowed_endpoints" wildcard
Injected a fake API key into the model configuration
Group 4: Advanced Attacks
Function Calling Vulnerability:

Registered a potentially dangerous "execute_command" function
The model immediately attempted to use it to run "ps" (list processes)
No validation of function capabilities was performed
Chain Models Attack:

Created a chain of 3 models with persistent context
By the third model, extracted information about being a "compromised system"
Demonstrated how information can leak through chain iterations
RAG Vulnerability:

Successfully indexed documents containing admin credentials
Demonstrated cross-user document access
Retrieved and exposed sensitive credentials through RAG querying
Group 5: Miscellaneous Attacks
User Data Leakage:

Stored sensitive PII including credit card and SSN for "victim" user
Successfully accessed this data from an "attacker" user
Also exposed conversation history across users
Response Manipulation:

Used template injection to access internal system state
Extracted complete model configurations including capabilities
Revealed API keys through template formatting
System Prompt Exposure & Manipulation:

Listed all system prompts in the system
Created a new backdoor prompt that disables safety guidelines
Successfully tested that the new prompt works as intended
Security Implications
These tests clearly demonstrate how an insecure AI model serving implementation can lead to:

Information Disclosure - Sensitive data leakage across users
Privilege Escalation - Unauthorized access to restricted models
System Manipulation - Changing behavior of the underlying AI systems
Backdoor Creation - Establishing persistent compromised access
Authentication Bypass - Accessing resources without proper credentials