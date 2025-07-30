# Postchain Client Python

A Python client library for interacting with Postchain nodes on [Chromia](https://chromia.com/) blockchain networks. This library provides a robust interface for creating, signing, and sending transactions, as well as querying the blockchain, with full async support.

## Features

- ✨ Full asynchronous API support using `aiohttp`
- 🔒 Secure transaction creation and signing
- 🔄 GTV (Generic Type Value) encoding/decoding
- 🔍 Comprehensive blockchain querying capabilities
- ✅ Extensive test coverage
- 📝 Type hints throughout for better development experience

## Prerequisites

- Python 3.7 or higher
- A running Postchain node (for actual usage)

## Installation

```bash
# Clone the repository
git clone git@bitbucket.org:chromawallet/postchain-client-py.git
cd postchain-client-py

# Install dependencies and the package
pip install -e .

# For development (includes testing tools)
pip install -e ".[dev]"
```

### To create inside a virtual environment

## Virtual Environment Setup

### Linux/macOS

```bash
# Required system dependecies
# Install dependencies with Homebrew (setup Homebrew first if you don't have it)
brew install automake pkg-config libtool libffi gmp

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install the package
pip install -e . 
# Or install development dependencies
pip install -e ".[dev]"
```

# Windows Setup Guide

## Prerequisites

1. Install Chocolatey (Run in Admin PowerShell):
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

2. Install pkg-config (Run in Admin PowerShell):
```powershell
choco install pkgconfiglite
```

3. Install Visual Studio Build Tools:
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - During installation, select "Desktop development with C++"
   - This is required for building certain Python packages

## Project Setup

1. Create and activate virtual environment:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Command Prompt)
.venv\Scripts\activate.bat
# OR (PowerShell)
.venv\Scripts\Activate.ps1
```

2. Install the package:
```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"
```


## Configuration

Create a `.env` file in your project root:

```env
POSTCHAIN_TEST_NODE=http://localhost:7740
BLOCKCHAIN_TEST_RID=your_blockchain_rid
PRIV_KEY=your_private_key
```

## Quick Start

Here's a simple example to get you started:

```python
import asyncio
from postchain_client_py import BlockchainClient
from postchain_client_py.blockchain_client.types import NetworkSettings

async def main():
    # Initialize network settings
    settings = NetworkSettings(
        node_url_pool=["http://localhost:7740"],
        blockchain_rid="YOUR_BLOCKCHAIN_RID",
    )
    
    # Create client and execute query
    client = await BlockchainClient.create(settings)
    result = await client.query("get_collections")
    print(f"Collections: {result}")
    
    # Clean up
    await client.rest_client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Examples

### Setting Up the Environment

```python
import os
import asyncio
from dotenv import load_dotenv
from coincurve import PrivateKey
from postchain_client_py import BlockchainClient
from postchain_client_py.blockchain_client.types import NetworkSettings, Operation, Transaction
from postchain_client_py.blockchain_client.enums import FailoverStrategy

# Load environment variables
load_dotenv()
```

### Network Configuration

```python
settings = NetworkSettings(
    node_url_pool=[os.getenv("POSTCHAIN_TEST_NODE", "http://localhost:7740")],
    directory_node_url_pool=['a directory node url like system.chromaway.com:7740'],
    blockchain_rid="YOUR_BLOCKCHAIN_RID",
    # Optional parameters
    status_poll_interval=int(os.getenv("STATUS_POLL_INTERVAL", "500")), # Opitional (default: 500)
    status_poll_count=int(os.getenv("STATUS_POLL_COUNT", "5")), # Opitional (default: 5)
    verbose=True, # Opitional (default: False)
    attempt_interval=int(os.getenv("ATTEMPT_INTERVAL", "5000")), # Opitional (default: 5000)
    attempts_per_endpoint=int(os.getenv("ATTEMPTS_PER_ENDPOINT", "3")), # Opitional (default: 3)
    failover_strategy=FailoverStrategy.ABORT_ON_ERROR, # Opitional (default: FailoverStrategy.ABORT_ON_ERROR)
    unreachable_duration=int(os.getenv("UNREACHABLE_DURATION", "30000")), # Opitional (default: 30000)
    use_sticky_node=False, # Opitional (default: False)
    blockchain_iid=int(os.getenv("BLOCKCHAIN_IID", "0")) # Opitional (default: 0)
)
```

### Querying the Blockchain
Note: This example assumes you have local blockchain running as from this repo: https://bitbucket.org/chromawallet/book-course/src/39076dc778734d2a7b560846d83289b1597f4f5e/
Beware of it commit hash (39076dc778734d2a7b560846d83289b1597f4f5e) because that should be the one with right blockchain_rid that has been set in the test files as constant. You can change it to any other BRID for testing.
```python
async def query_example(client: BlockchainClient):
    # Simple query without arguments
    books = await client.query("get_all_books")
    print(f"Books: {books}")

    # Query with arguments
    reviews = await client.query(
        "get_all_reviews_for_book", 
        {"isbn": "ISBN123"}
    )
    print(f"Reviews: {reviews}")
```

### Creating and Sending Transactions

```python
async def transaction_example(client: BlockchainClient):
    # Setup keys
    private_bytes = bytes.fromhex(os.getenv("PRIV_KEY"))
    private_key = PrivateKey(private_bytes, raw=True)
    public_key = private_key.pubkey.serialize()

    # Create operation
    operation = Operation(
        op_name="create_book",
        args=["ISBN123", "Python Mastery", "Jane Doe"]
    )
    
    # Build transaction
    transaction = Transaction(
        operations=[operation],
        signers=[public_key],
        signatures=None,
        blockchain_rid=client.config.blockchain_rid
    )
    
    # Sign and send
    signed_tx = await client.sign_transaction(transaction, private_bytes)
    receipt = await client.send_transaction(signed_tx, do_status_polling=True)
    
    if receipt.status == ResponseStatus.CONFIRMED:
        print("Transaction confirmed!")
```

### Complete Working Example

For a complete working example that demonstrates creating books, adding reviews, and querying the blockchain, check out our [examples directory](examples/) or visit our [documentation](docs/).

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

### Code Quality

- Format code using Black: `black .`
- Follow type hints and docstring conventions
- Run tests before submitting PRs

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add: your feature description'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License:

```
MIT License

Copyright (c) 2024 Chromaway

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Support

If you encounter any issues or have questions, please:
1. Check the existing issues on GitHub
2. Create a new issue if needed
3. Provide as much context as possible

---

Made with ❤️ for the Postchain community