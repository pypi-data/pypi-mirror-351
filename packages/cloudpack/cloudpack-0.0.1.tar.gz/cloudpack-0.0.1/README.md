# CloudPack

![Project Status](https://img.shields.io/badge/status-pre--alpha-red)
![Tests](https://github.com/atar4xis/cloudpack/actions/workflows/python-app.yml/badge.svg)

**CloudPack** is an open-source, multi-cloud file vault. It encrypts your files, splits them into chunks, and stores those chunks across different cloud providers. You hold the only key - your master password.

> ⚠️ **Project Status: Pre-Alpha**  
> CloudPack is in active early development and is **not ready to use**. Expect incomplete features, placeholder code, and rapid breaking changes. Contributions and feedback are welcome.

## Features

- 🔐 **End-to-End Encryption** - AES-256 encryption before upload
- 🧩 **Chunked Storage** - Files are split and distributed across providers
- ☁️ **Multi-Cloud Support** - Use Google Drive, Dropbox, OneDrive, and more
- 🔄 **Cross-Platform** - Works on macOS, Linux, and Windows
- 🛠 **CLI and API** - Full control for power users and integrations

## Installation

**Requirements:**

- Python 3.10 or higher
- pip (Python package installer)
- Git (to clone the repository)

**Steps:**

1. Clone the repository:

   ```bash
   git clone https://github.com/atar4xis/cloudpack.git
   cd cloudpack
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run cloudpack:

   ```bash
   python cloudpack.py
   ```

## Usage/Examples

⚠️ This section is under development.

## Supported Providers

⚠️ This section is under development.

## License

CloudPack is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome!

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and setup instructions.

## Roadmap

- [x] Command-Line Interface
- [ ] Core Encryption & Chunking
- [ ] Basic Vault Operations
- [ ] Configuration Management
- [ ] Google Drive Support
- [ ] Dropbox Support
- [ ] Documentation & Tutorials
- [ ] API Development
- [ ] Desktop GUI
