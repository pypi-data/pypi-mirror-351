# Contributing to Humanize AI

Thank you for considering contributing to Humanize AI!

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/berrydev-ai/humanize-ai.git
   cd humanize-ai
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
python -m unittest discover
```

## Style Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) coding standards
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Include type hints where appropriate

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests to ensure they pass
5. Commit your changes (`git commit -am 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature`)
7. Create a new Pull Request

## License

By contributing, you agree that your contributions will be licensed under the project's MIT license.
