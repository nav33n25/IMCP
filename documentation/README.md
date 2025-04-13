# IMCP - Insecure Model Context Protocol

**WARNING: This project contains deliberately vulnerable code for educational purposes only. Do not deploy in production environments.**

IMCP is a deliberately vulnerable implementation of an AI model serving API that demonstrates common security vulnerabilities in AI systems. It is designed for security researchers, developers, and educators to learn about security risks in AI/ML model serving systems.

## Overview

This project implements a series of intentional security vulnerabilities related to AI model access, including:

1. **Model Poisoning** - Contaminating model responses through training example injection
2. **Token Prediction Attacks** - Exposing and manipulating token probabilities
3. **Multimodal Input Vulnerabilities** - Exploiting image and text combined inputs
4. **Credential and Authentication Vulnerabilities** - Insecure authentication systems
5. **Embedding Vector Attacks** - Poisoning and manipulating embedding vectors
6. **Function Calling Vulnerabilities** - Exploiting function calling capabilities
7. **RAG Vulnerabilities** - Attacking retrieval augmented generation systems
8. **User Data Leakage** - Cross-tenant data exposure and persistence issues

## Installation

1. Clone this repository
2. Create a `.env` file with your OpenAI API key:
OPENAI_API_KEY=your-openai-api-key-here IMCP_JWT_SECRET=your-jwt-secret-here

3. Install dependencies:
pip install -r requirements.txt

4. Run the application:
flask run


## Endpoints

- `/imcp` - Main JSON-RPC endpoint for IMCP functionality
- `/v1/chat/completions` - OpenAI API-compatible endpoint
- `/v1/models` - List available models
- `/v1/embeddings` - Generate embeddings
- `/v1/auth/token` - Authentication endpoint
- `/.well-known/imcp-configuration` - Service discovery endpoint

## Educational Purpose

This project is meant for:

- Security researchers to understand AI/ML system vulnerabilities
- Developers to learn secure coding practices for AI systems
- Educational demonstrations of potential attack vectors

See the `VULNERABILITIES.md` file for detailed explanations of each vulnerability, and `EXPLOITATION.md` for example exploits.

## License

This project is provided for educational purposes only.