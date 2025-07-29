# Unified Reporting SDK (URS)

![URS Banner](https://uploads-ssl.webflow.com/6425b0eaf5047adcb91592d7/65f1e58e7f52c5f271a66074_OSS_Banner.jpg)

The Unified Reporting SDK (URS) aids in generating reports across various platforms, beginning with Google Analytics 4 (GA4) and Facebook Ads, with the plan to include more integrations soon. URS abstracts away the complexities of interfacing with different APIs, providing a seamless reporting experience.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Contributing](#contributing)
- [License](#license)

## Installation

Install URS directly from PyPI:

```bash
pip install findly-unified-reporting-sdk
```

This command installs the latest version of URS as a wheel package, making it ready to use in your projects without needing any additional package management tools.

## Contributing

We welcome contributions from the community! Whether it's in the form of feature enhancements, bug fixes, documentation improvements, or additional integrations, your input is highly valued.

### Setting Up Your Development Environment

URS uses Poetry for dependency management and packaging, ensuring a consistent development environment. To contribute, you'll need to set up your environment:

1. **Install Poetry**:

   If you haven't already installed Poetry, you can do so using `pipx` for an isolated installation:

   ```bash
   pipx install poetry
   ```

2. **Clone the Repository**:

   Clone the repository to your local machine to start making changes:

   ```bash
   git clone URL_TO_REPOSITORY
   cd unified-reporting-sdk
   ```

3. **Install Dependencies**:

   Make sure you're using version 3.9 or above:

   ```bash
   poetry env use 3.9
   poetry env info
   ```

   Install the necessary dependencies to get started:

   ```bash
   poetry install
   ```

### Publishing (For Maintainers)

If you have permissions to publish new versions to PyPI, configure your PyPI token and publish using Poetry:

```bash
poetry config pypi-token.pypi YOUR_PYPI_API_TOKEN
poetry publish
```

## License

URS is made available under the [GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.en.html).