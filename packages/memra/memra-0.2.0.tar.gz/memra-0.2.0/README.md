# Memra SDK

A declarative orchestration framework for AI-powered business workflows. Think of it as "Kubernetes for business logic" where agents are the pods and departments are the deployments.

## 🚀 Team Setup

**New team member?** See the complete setup guide: **[TEAM_SETUP.md](TEAM_SETUP.md)**

This includes:
- Database setup (PostgreSQL + Docker)
- Local development environment
- Testing instructions
- Troubleshooting guide

## Quick Start

```python
from memra.sdk.models import Agent, Department, Tool

# Define your agents
data_extractor = Agent(
    role="Data Extraction Specialist",
    job="Extract and validate data",
    tools=[Tool(name="DataExtractor", hosted_by="memra")],
    input_keys=["input_data"],
    output_key="extracted_data"
)

# Create a department
dept = Department(
    name="Data Processing",
    mission="Process and validate data",
    agents=[data_extractor]
)

# Run the workflow
result = dept.run({"input_data": {...}})
```

## Installation

```bash
pip install memra
```

## API Access

Memra requires an API key to execute workflows on the hosted infrastructure.

### Get Your API Key
Contact [info@memra.co](mailto:info@memra.co) for API access.

### Set Your API Key
```bash
# Set environment variable
export MEMRA_API_KEY="your-api-key-here"

# Or add to your shell profile for persistence
echo 'export MEMRA_API_KEY="your-api-key-here"' >> ~/.zshrc
```

### Test Your Setup
```bash
python examples/accounts_payable_client.py
```

## Documentation

Documentation is coming soon. For now, see the examples below and in the `examples/` directory.

## Example: Propane Delivery Workflow

See the `examples/propane_delivery.py` file for a complete example of how to use Memra to orchestrate a propane delivery workflow.

## Contributing

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Examples

```
├── examples/
│   ├── accounts_payable_client.py  # API-based example
│   ├── accounts_payable.py         # Local example
│   ├── invoice_processing.py       # Simple workflow
│   └── propane_delivery.py         # Domain example
├── memra/                  # Core SDK
├── logic/                  # Tool implementations  
├── local/dependencies/     # Database setup & schemas
└── docker-compose.yml      # Database setup
```

## ✨ New: MCP Integration

Memra now supports **Model Context Protocol (MCP)** integration, allowing you to execute operations on your local infrastructure while leveraging Memra's cloud-based AI processing.

**Key Benefits:**
- 🔒 **Keep sensitive data local** - Your databases stay on your infrastructure
- ⚡ **Hybrid processing** - AI processing in the cloud, data operations locally  
- 🔐 **Secure communication** - HMAC-authenticated requests between cloud and local
- 🛠️ **Easy setup** - Simple bridge server connects your local resources

**Quick Example:**
```python
# Agent that uses local database via MCP
agent = Agent(
    role="Data Writer",
    tools=[{
        "name": "PostgresInsert",
        "hosted_by": "mcp",  # Routes to your local infrastructure
        "config": {
            "bridge_url": "http://localhost:8081",
            "bridge_secret": "your-secret"
        }
    }]
)
```

📖 **[Complete MCP Integration Guide →](docs/mcp_integration.md)**
