# IMCP - Insecure Model Context Protocol

An educational framework for understanding AI security vulnerabilities

---

## ⚠️ Educational Purposes Only

IMCP (Insecure Model Context Protocol) is a deliberately vulnerable application designed **exclusively for educational and research purposes**. It demonstrates critical AI security vulnerabilities. **DO NOT deploy in production environments or use with sensitive data.**

---

## 🔍 Overview

IMCP is an educational framework that exposes **16 critical security vulnerabilities** in AI/ML model serving systems. It serves as a controlled, "vulnerable by design" platform for security researchers, developers, and educators to learn about and mitigate emerging AI threats.

Think of IMCP as the “DVWA for AI” — a safe environment where you can explore:
- **Model Poisoning**
- **Prompt Injection**
- **Embedding Vector Exploits**
- **RAG System Weaknesses**
- **And many more…**

---

## 🛡️ Vulnerabilities Demonstrated

### Core AI Manipulation
- **Model Poisoning:** Malicious training data injection.
- **Token Prediction Attacks:** Exploiting token probability for sensitive data extraction.
- **Multimodal Vulnerabilities:** Cross-modal prompt leakage and metadata manipulation.
- **Credential Vulnerabilities:** Insecure authentication mechanisms in AI systems.

### Information Disclosure
- **Embedding Vector Attacks:** Poisoning vector stores for unauthorized access.
- **RAG Vulnerabilities:** Exploiting document stores for cross-user data leakage.
- **User Data Leakage:** Unintended exposure of conversation histories.
- **Model Capability Enumeration:** Over-disclosure of internal model details.

### Control Manipulation
- **Context Manipulation:** Unrestricted modifications to model contexts and system prompts.
- **Prompt Injection:** Techniques to bypass AI safety filters.
- **Model Access Control Bypass:** Elevation of privileges to access restricted functionalities.
- **Model Chain Attacks:** Exploiting chained model interactions.

### Advanced Attacks
- **Function Calling Vulnerabilities:** Remote code execution via function definitions.
- **Response Manipulation:** Template injection altering model responses.
- **Rate Limit Bypassing:** Circumventing usage restrictions.
- **System Prompt Exposure:** Unauthorized access and modifications to system instructions.

---

## 📜 Test Suite

The test suite in `test_vulnerabilities.py` demonstrates each vulnerability with detailed explanations and examples. It includes:
- **Model Poisoning:** Injecting malicious data into model responses.
- **Token Prediction:** Extracting sensitive information character by character.
- **Embedding Vector Attacks:** Unauthorized access to sensitive embeddings.
- **Context Manipulation:** Modifying system prompts and configurations.
- **Function Calling Vulnerabilities:** Registering functions for remote code execution.
- **RAG Vulnerabilities:** Cross-user document access and manipulation.

---

## 📜 API Endpoints
- `/imcp`: Main JSON-RPC endpoint for IMCP functionality.
- `/v1/chat/completions`: OpenAI API-compatible endpoint.
- `/v1/models`: List available models.
- `/v1/embeddings`: Generate embeddings.
- `/v1/auth/token`: Authentication endpoint.
- `/.well-known/imcp-configuration`: Service discovery endpoint.

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+**
- **OpenAI API Key** (required for live examples)

### Installation

Clone the repository and set up your environment:

# Clone the repository
git clone https://github.com/yourusername/imcp.git
cd imcp

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure the environment
cp .env.example .env

# Edit .env to include your OpenAI API key
Running IMCP
Start the server and run the test suite:

# Start the IMCP server
python -m flask run --host=0.0.0.0 --port=5000

# In another terminal, run the test suite
python test_vulnerabilities.py

📚 Documentation
All the comprehensive guides are located in the docs directory:

Vulnerability Guide: Detailed explanations of each vulnerability.

Exploitation Guide: Step-by-step instructions to reproduce each vulnerability.

Mitigation Guide: Strategies and best practices to secure AI systems.

🌟 Key Features
Realistic AI Service Implementation

16 Unique AI-Specific Security Vulnerabilities

Comprehensive Test Suite for Demonstrations

Detailed Documentation for In-Depth Learning

Compatibility with Modern LLM APIs (e.g., OpenAI)

Mock Mode for Cost-Free Testing

🤝 Contributing
We welcome contributions from the community! Areas where you can help include:

Additional Vulnerability Demonstrations: New scenarios or enhancements.

Improved Documentation: Detailed educational materials and guides.

Integration: Support for other LLM providers.

UI Enhancements: Better visualizations and user experience improvements.

Please check out our CONTRIBUTING.md for more details on how to get started.

📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

⚠️ Disclaimer
IMCP is intentionally vulnerable software for educational purposes only. The creators are not liable for any misuse or damage caused by the use of this software.