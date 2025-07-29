# Memra SDK

A declarative orchestration framework for AI-powered business workflows. Think of it as "Kubernetes for business logic" where agents are the pods and departments are the deployments.

## 🚀 Quick Start

```python
from memra import Agent, Department, LLM
from memra.execution import ExecutionEngine

# Define your agents declaratively
data_engineer = Agent(
    role="Data Engineer",
    job="Extract invoice schema from database",
    llm=LLM(model="llama-3.2-11b-vision-preview", temperature=0.1),
    tools=[
        {"name": "DatabaseQueryTool", "hosted_by": "memra"}
    ],
    output_key="invoice_schema"
)

invoice_parser = Agent(
    role="Invoice Parser", 
    job="Extract structured data from invoice PDF",
    llm=LLM(model="llama-3.2-11b-vision-preview", temperature=0.0),
    tools=[
        {"name": "PDFProcessor", "hosted_by": "memra"},
        {"name": "InvoiceExtractionWorkflow", "hosted_by": "memra"}
    ],
    input_keys=["file", "invoice_schema"],
    output_key="invoice_data"
)

# Create a department
ap_department = Department(
    name="Accounts Payable",
    mission="Process invoices accurately into financial system",
    agents=[data_engineer, invoice_parser],
    workflow_order=["Data Engineer", "Invoice Parser"]
)

# Execute the workflow
engine = ExecutionEngine()
result = engine.execute_department(ap_department, {
    "file": "invoice.pdf",
    "connection": "postgresql://user@host/db"
})

if result.success:
    print("✅ Invoice processed successfully!")
    print(f"Data: {result.data}")
```

## 📦 Installation

```bash
pip install memra-sdk
```

## 🔑 Configuration

### Step 1: Get Your API Key
Contact **info@memra.co** to request an API key for early access.

### Step 2: Set Your API Key
Once you receive your API key, configure it:

```bash
export MEMRA_API_KEY="your-api-key-here"
export MEMRA_API_URL="https://api.memra.co"  # Optional, defaults to production
```

Or in Python:

```python
import os
os.environ["MEMRA_API_KEY"] = "your-api-key-here"
```

## 🎯 Key Features

- **Declarative**: Define workflows like Kubernetes YAML
- **AI-Powered**: Built-in LLM integrations for document processing
- **Conversational**: Agents explain what they're doing in real-time
- **Production Ready**: Real database connectivity and file processing
- **Scalable**: Tools execute on Memra's cloud infrastructure

## 🏗️ Core Concepts

### Agents
Agents are the workers in your workflow. Each agent has:
- **Role**: What they do (e.g., "Data Engineer")
- **Job**: Their specific responsibility
- **Tools**: What capabilities they use
- **LLM**: Their AI model configuration

### Departments
Departments coordinate multiple agents:
- **Mission**: Overall goal
- **Workflow Order**: Sequence of agent execution
- **Manager**: Optional oversight and validation

### Tools
Tools are hosted capabilities:
- **memra**: Hosted by Memra (PDF processing, LLMs, databases)
- **mcp**: Customer-hosted via Model Context Protocol

## 📊 Example Output

```
🏢 Starting Accounts Payable Department
📋 Mission: Process invoices accurately into financial system
👥 Team: Data Engineer, Invoice Parser
🔄 Workflow: Data Engineer → Invoice Parser

👤 Data Engineer: Hi! I'm starting my work now...
💭 Data Engineer: My job is to extract invoice schema from database
⚡ Data Engineer: Using tool 1/1: DatabaseQueryTool
✅ Data Engineer: Great! DatabaseQueryTool did real work and gave me useful results
🎉 Data Engineer: Perfect! I completed my work with real data processing

👤 Invoice Parser: Hi! I'm starting my work now...
💭 Invoice Parser: My job is to extract structured data from invoice pdf
⚡ Invoice Parser: Using tool 1/2: PDFProcessor
✅ Invoice Parser: Great! PDFProcessor did real work and gave me useful results
```

## 🔍 Tool Discovery

Discover available tools:

```python
from memra import discover_tools, get_api_status

# Check API health
status = get_api_status()
print(f"API Health: {status['api_healthy']}")
print(f"Tools Available: {status['tools_available']}")

# Discover tools
tools = discover_tools()
for tool in tools:
    print(f"- {tool['name']}: {tool['description']}")
```

## 📚 Examples

See the `examples/` directory for complete workflows:

- `accounts_payable_client.py`: Invoice processing with database integration
- More examples coming soon!

## 🆘 Support

- **Support**: info@memra.co

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ by the Memra team** 
**Note**: The SDK will not work without a valid API key.
