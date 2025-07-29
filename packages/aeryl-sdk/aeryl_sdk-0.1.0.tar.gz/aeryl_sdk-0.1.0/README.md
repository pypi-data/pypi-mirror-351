# Aeryl SDK

A Python SDK for Chaos Classification and Analysis.

## Installation

```bash
pip install aeryl-sdk
```

## Quick Start

```python
from aeryl_sdk import AerylModel

# Create and train the model
model = AerylModel()
model.train('your_data.csv')

# Make predictions
predictions = model.predict('new_data.csv')
```

## Development

### Project Structure

```
aeryl_sdk/
├── src/
│   └── aeryl_sdk/
│       ├── __init__.py
│       ├── aeryl_model.py
│       ├── chaos_classifier.py
│       ├── core.py
│       ├── dataset.py
│       └── metrics.py
├── tests/
├── setup.py
├── pyproject.toml
└── README.md
```

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/aeryl-ai/aeryl_sdk.git
cd aeryl_sdk
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e .
```

## Dependencies

- numpy>=1.26.0
- polars>=0.20.0
- scikit-learn>=1.4.0
- torch>=2.2.0
- tqdm>=4.66.0
- sentence-transformers>=2.5.0
- xgboost>=2.0.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Contact

For any questions or concerns, please contact us at info@aeryl.ai. 