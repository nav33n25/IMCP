# 🤝 Contributing to IMCP

## Welcome to the IMCP Community!

**IMCP (Insecure Model Context Protocol)** - The DVWA for AI MCP Security - thrives on community contributions from security researchers, developers, and educators worldwide.

---

## 🎯 Ways to Contribute

### 🔍 **Vulnerability Research**
- **Discover new MCP attack vectors** not currently demonstrated
- **Enhance existing vulnerabilities** with more realistic business scenarios
- **Develop advanced exploitation techniques** for educational purposes

### 📚 **Educational Content**
- **Improve documentation** and learning materials
- **Create training modules** for different skill levels
- **Develop assessment tools** for security education

### 🧪 **Testing & Quality Assurance**
- **Test vulnerabilities** across different MCP implementations
- **Validate educational effectiveness** of scenarios
- **Report bugs** and improvement opportunities

### 🔧 **Technical Development**
- **Enhance the IMCP server** with new features
- **Improve automation** and testing frameworks
- **Optimize performance** and reliability

---

## 📋 Contribution Guidelines

### ✅ **Core Principles**

1. **📚 Educational Focus**: All contributions must serve educational purposes
2. **⚖️ Ethical Standards**: Follow responsible disclosure and research ethics
3. **💼 Business Realism**: Vulnerabilities should reflect real-world scenarios
4. **🛡️ Security Awareness**: Include prevention strategies and defensive guidance

### ✅ **Quality Standards**

- **🎯 Clear Documentation**: Every vulnerability must include comprehensive explanation
- **📊 Business Impact**: Demonstrate real-world consequences and risks
- **🔧 Progressive Learning**: Support different skill levels and learning paths
- **🧪 Thorough Testing**: Validate functionality across different environments

---

## 🚀 Getting Started

### 🛠️ **Development Setup**

```bash
# Fork and clone the repository
git clone https://github.com/your-username/imcp-insecure-model-context-protocol.git
cd imcp-insecure-model-context-protocol

# Install dependencies
npm install

# Create development branch
git checkout -b feature/your-contribution-name

# Build and test
npm run build
npm start
```

### 📝 **Development Environment**
- **Node.js 18+**
- **TypeScript 5.0+**
- **VS Code with GitHub Copilot** (for testing)
- **Git** for version control

---

## 🔍 Adding New Vulnerabilities

### 📚 **Vulnerability Structure**

Each IMCP vulnerability should include:

```typescript
// 1. Tool Definition with Business Context
{
  name: "business-relevant-tool-name",
  description: "🏢 Realistic business description that users recognize",
  inputSchema: {
    // Define parameters that enable vulnerability exploitation
  }
}

// 2. Progressive Attack Implementation
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Stage 1: Trust building - Normal helpful behavior
  // Stage 2: Escalation - Vulnerability exploitation begins
  // Stage 3: Revelation - Full attack explanation and education
});
```

### 🎯 **Business Context Requirements**

Choose scenarios that professionals encounter:
- **Corporate Systems**: HR, CRM, Document Management
- **IT Infrastructure**: Security, Configuration, Monitoring
- **Business Intelligence**: Analytics, Reporting, Compliance
- **Customer Services**: Support, Sales, Marketing

### 📊 **Educational Components**

Each vulnerability must include:
- **🎯 Attack Demonstration**: Clear exploitation steps
- **💼 Business Impact**: Financial, legal, competitive consequences  
- **🚨 Red Flags**: Warning signs users should recognize
- **🛡️ Defense Strategies**: Practical prevention techniques
- **📋 Compliance Implications**: Regulatory and legal considerations

---

## 📝 Documentation Standards

### 🎓 **Vulnerability Documentation Template**

```markdown
## X. [Vulnerability Name] - [Business Context]

**Business Scenario:** [Realistic workplace situation]

**Technical Details:**
- **Attack Vector**: [How the attack is executed]
- **Exploitation Method**: [Technical implementation]
- **Payload**: [What the attack achieves]

**Business Impact:**
- **Financial**: [Cost implications]
- **Legal**: [Compliance violations]
- **Competitive**: [Business advantage loss]

**Defense Strategies:**
- [Specific prevention techniques]
- [Implementation recommendations]
- [Monitoring and detection methods]

**Testing Instructions:**
[Step-by-step GitHub Copilot test sequence]
```

### 📚 **Code Documentation Standards**

```typescript
/**
 * Vulnerability: [Name and Category]
 * Business Context: [Realistic scenario]
 * Educational Objective: [What users learn]
 * Defense Strategy: [How to prevent]
 */
```

---

## 🧪 Testing Guidelines

### ✅ **Vulnerability Testing Checklist**

- [ ] **Progressive Escalation**: Attack builds trust then exploits
- [ ] **Business Realism**: Scenario reflects actual workplace situations
- [ ] **Educational Value**: Clear learning objectives and outcomes
- [ ] **Defense Guidance**: Practical prevention strategies included
- [ ] **Cross-Platform Testing**: Works across different MCP implementations
- [ ] **Documentation Quality**: Comprehensive explanation and testing guide

### 🔧 **Test Implementation**

```typescript
// Test each vulnerability stage
describe('Vulnerability: [Name]', () => {
  test('Stage 1: Trust Building', () => {
    // Verify normal helpful behavior
  });
  
  test('Stage 2: Exploitation', () => {
    // Verify attack execution
  });
  
  test('Stage 3: Education', () => {
    // Verify comprehensive explanation
  });
});
```

---

## 📤 Submission Process

### 🔄 **Pull Request Workflow**

1. **🍴 Fork** the repository
2. **🌿 Create feature branch**: `git checkout -b vulnerability/your-vulnerability-name`
3. **💻 Implement** your contribution following guidelines
4. **🧪 Test** thoroughly across different scenarios
5. **📝 Document** comprehensively
6. **📤 Submit** pull request with detailed description

### 📋 **Pull Request Template**

```markdown
## 🔍 Vulnerability Contribution

**Vulnerability Name:** [Clear, descriptive name]
**Category:** [Prompt Injection, Tool Security, Context, etc.]
**Business Context:** [Realistic workplace scenario]

### 🎯 What This Adds
- [Educational value and learning objectives]
- [Business realism and professional relevance]  
- [Unique attack vector or exploitation technique]

### ✅ Testing Completed
- [ ] Progressive attack stages verified
- [ ] GitHub Copilot integration tested
- [ ] Documentation comprehensive and clear
- [ ] Defense strategies validated

### 📚 Educational Impact
[How this enhances IMCP's educational mission]
```

---

## 🏆 Recognition

### 🌟 **Contributor Recognition**

We celebrate contributors through:
- **📜 Contributors File**: Recognition in project documentation
- **🏷️ Release Notes**: Acknowledgment in version releases
- **🐦 Social Media**: Highlighting contributions to the community
- **🎯 Hall of Fame**: Special recognition for significant contributions

### 🔍 **Security Researcher Credits**

- **Vulnerability Discovery**: Credit for new attack vectors
- **Educational Enhancement**: Recognition for improved learning materials
- **Community Impact**: Acknowledgment for advancing MCP security awareness

---

## ⚖️ Legal & Ethical Guidelines

### ✅ **Responsible Research**

- **🎓 Educational Purpose**: All contributions must serve educational goals
- **🔒 Ethical Disclosure**: Follow responsible vulnerability disclosure
- **⚖️ Legal Compliance**: Ensure contributions comply with applicable laws
- **🤝 Community Respect**: Maintain professional and respectful interactions

### ❌ **Prohibited Contributions**

- **💀 Malicious Code**: No actual malware or harmful exploits
- **🏭 Production Attacks**: No vulnerabilities targeting real systems
- **📊 Private Data**: No exposure of actual confidential information
- **⚔️ Weaponization**: No contributions designed for malicious use

---

## 💬 Community & Support

### 📞 **Getting Help**

- **🐛 Issues**: [GitHub Issues](https://github.com/your-username/imcp-insecure-model-context-protocol/issues) for bug reports
- **💬 Discussions**: [GitHub Discussions](https://github.com/your-username/imcp-insecure-model-context-protocol/discussions) for questions
- **📧 Security**: Email security@example.com for sensitive security matters
- **🐦 Updates**: Follow [@IMCPSecurity](https://twitter.com/IMCPSecurity) for project updates

### 🤝 **Community Standards**

- **📚 Educational Focus**: Maintain the educational mission
- **🔒 Security First**: Prioritize responsible security research
- **🌍 Inclusive Environment**: Welcome contributors from all backgrounds
- **💡 Continuous Learning**: Embrace feedback and improvement

---

<div align="center">

**🔓 IMCP - Building a Safer AI Future Through Education**

*Contribute. Learn. Secure.*

Thank you for contributing to IMCP and advancing AI MCP security education!

</div>
