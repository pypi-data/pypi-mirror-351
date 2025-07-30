# Solentra - DeSci AI Agent

A powerful Python package for creating science-themed AI agents with advanced research and experimentation capabilities. Solentra enables automated scientific workflows, experiment simulation, research paper analysis, and collaborative research.

## Features

- **Core AI & Agent Capabilities**
  - Specialized agent personas (physicist, biologist, etc.)
  - Context-aware conversation management
  - Multi-agent collaboration capabilities
  - Async processing for complex tasks
  - Model training and evaluation
  - Custom persona creation and management
  - Experiment history tracking
  - Advanced context management

- **Research & Experimentation Tools**
  - Structured research task planning
  - Experiment design and management
  - Scientific paper analysis and parsing
  - Citation handling and formatting
  - Data cleaning and preprocessing
  - ArXiv paper search integration
  - PDF parsing and analysis
  - Literature review automation

- **Data Science & ML Tools**
  - Data validation and cleaning
  - Model training and evaluation
  - Hyperparameter tuning
  - Performance metrics analysis
  - Dataset preparation and management
  - Jupyter notebook integration
  - Git repository management

- **Social Integration**
  - Twitter research updates and engagement
  - Media sharing capabilities
  - Content calendar management
  - Engagement analytics
  - Hashtag performance tracking
  - Audience demographics analysis
  - Tweet scheduling and automation

## Installation

### From PyPI (Recommended)

```bash
pip install solentra
```

### From Source

```bash
git clone https://github.com/solentra/solentra.git
cd solentra
pip install -e .
```

### Development Installation

```bash
pip install solentra[dev]
```

## Quick Start

```python
from solentra import SolentraAgent

# Initialize agent
agent = SolentraAgent(
    agent_name="Research Scientist",
    model_name="solentra-70b",
    tools_enabled=True
)

# Create and run an experiment
protocol = agent.create_experiment(
    steps=["Sample preparation", "Data collection"],
    materials=["Reagent A", "Equipment B"],
    duration="2 hours",
    conditions={"temperature": 25}
)

results = agent.run_experiment(
    protocol=protocol,
    variables={"concentration": 0.5},
    iterations=3
)

# Analyze results
analysis = agent.analyze_data(
    [r['variables']['concentration'] for r in results['results']]
)
```

## Documentation

For detailed documentation, visit our [documentation site](https://solentra.ai/docs) or explore the following guides:

- [Agent Documentation](docs/agent.md) - Comprehensive guide to SolentraAgent features and usage
- [Tools Documentation](docs/tools.md) - Detailed information about research and ML tools
- [Social Media Integration](docs/social.md) - Guide to Twitter integration and social features
- [Examples](docs/examples.md) - Code examples and use cases

### Key Documentation Topics

1. **Agent Setup and Configuration**
   - Agent initialization and customization
   - Persona management
   - Context handling
   - Error handling and debugging

2. **Research Tools**
   - Experiment management
   - Paper analysis
   - Citation formatting
   - Data validation and cleaning

3. **Machine Learning**
   - Model training and evaluation
   - Data preparation
   - Performance analysis
   - Hyperparameter optimization

4. **Social Media**
   - Twitter integration
   - Content management
   - Analytics and engagement
   - Best practices

## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- Email: contact@solentra.ai
- Twitter: [@Solentra](https://x.com/SolentraAI)
- GitHub: [solentra/solentra](https://github.com/solentra/solentra)
