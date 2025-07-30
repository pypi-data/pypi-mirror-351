# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-02

### Added
- Initial release of the Postchain Python Client
- Full asynchronous API support using `aiohttp`
- Secure transaction creation and signing
- GTV (Generic Type Value) encoding/decoding
- Comprehensive blockchain querying capabilities
- Transaction status polling and confirmation
- Failover strategies for node communication
- Extensive test coverage with pytest
- Type hints throughout for better development experience
- Example implementations in examples directory
- Comprehensive documentation in README.md

### Dependencies
- Python 3.7+
- aiohttp>=3.8.0
- cryptography>=3.4.7
- pyasn1>=0.4.8
- ecdsa>=0.18.0
- coincurve>=18.0.0
- python-dotenv>=0.19.0
- asn1crypto>=1.4.0
- asn1>=2.6.0

[0.1.0]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.0 

## [0.1.1] - 2025-01-10

### Added
- Added multi-signature support for transactions.
- Added pipeline on Bitbucket.
- Removed unused code.


[0.1.1]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.1 


## [0.1.2] - 2025-01-17

### Added
- Added CHANGELOG.md
- Added new versioning
- Added MIT license to README.md

[0.1.2]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.2 

## [0.1.3] - 2025-01-17

### Added
- Added pypirc configurations
- Updated README.md
- Unused module (common) removed

[0.1.3]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.3 

## [0.1.4] - 2025-01-20

### Fixed
- Added missing packages to the pyproject.toml

[0.1.4]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.4 

## [0.1.5] - 2025-01-22

### Added
- Added rich for pretty printing on tests (dev environment)
- Added integration tests for multi-signature transactions

### Fixed
- Fixed the multi signature transaction serialization to fix sending the transaction to the blockchain


[0.1.5]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.5 

## [0.1.6] - 2025-01-22

### Added
- Added integration tests for querying the blockchain

### Fixed
- Fixed the query response handling when getting singular type response
- Fixed add_signature method to handle multisig transactions

[0.1.6]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.6 

## [0.1.7] - 2025-01-28

### Added
- Added dynamic node discovery via directory node URL pools
- Added support for connecting to blockchain nodes through a directory service
- Added new test cases for node discovery functionality
- Added test for Merkle hash calculator and GTV hash verification

### Fixed
- Updated error message format for query parameter validation
- Improved node URL handling and validation

[0.1.7]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.7

## [0.1.8] - 2025-04-03

### User-Facing Changes
#### Added
- Added new configuration parameter for merkle hash version specification 'merkle_hash_version' (default is 1)
- A new function sign_and_send_transaction was added to simplify the process of signing and sending a transaction with a single function call.
- Important Note: Python client was already supporting merkle hash version 2 from start. If you select version 1 from configuration, it only adds one nop to operation list before signing and nothing else. This is not an actual support for merkle hash version 1 and if you use one element list within a query or operation argument, it will still not work even if you select version 1 when your dapp postchain node is configured to use version 1.
### Internal Changes
#### Added
- Added comprehensive test suite for Chromia Test Framework integration
- Implemented separate pipeline steps for different test environments
- Added proper logging configuration for test debugging

#### Changed
- Reorganized test structure to separate unit, integration, and framework tests
- Updated CI/CD pipeline to handle different test environments efficiently
- Improved test environment setup with docker-compose integration
- Now client query function requests are sent by /query_gtv endpoint to postchain node
[0.1.8]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.8

## [0.1.9] - 2025-04-11

### Changed
- Logger now does not print info level logs when verbose is set to False

[0.1.9]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.1.9

## [0.2.0] - 2025-05-09

### Added
- Added support for decimal values in GTV encoding/decoding
- Added `BigInt` type for handling large integers beyond standard int range
- Added `gtv_json` utility function for Rell compatibility with automatic type conversion
- Added comprehensive CI/CD pipeline for automated testing and PyPI deployment
- Added message field to TransactionReceipt for improved error reporting

### Changed
- Improved transaction handling with better error responses
- Enhanced send_transaction to return full response details (transaction_rid, status_code, body)
- Modified integer handling to automatically convert to BigInt when exceeding int64 range
- Improved transaction status polling to skip polling for immediately rejected transactions
- Upgraded test framework integration with latest Chromia Test Framework

### Fixed
- Fixed ResponseStatus enum value comparison in transaction status handling
- Fixed error handling for transaction rejections with proper status code checks

### Removed
- Removed dependencies on pyasn1 and asn1crypto packages

[0.2.0]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.2.0

## [0.2.1] - 2025-05-22

### Added
- Added `QueryObject` class for improved type safety and better IDE integration

### Changed
- Updated `to_query_object` function to handle the new QueryObject type
- Enhanced query method to accept QueryObject instances
- Improved backward compatibility for both 'name' and 'type' field names in query objects

[0.2.1]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.2.1

## [0.2.2] - 2025-05-30

### Changed
- Updated dependency supported versions(python_dotenv>=1.0.1, aiohttp>=3.11.11) to allow for greater flexibility and compatibility
- Updated the to_query_object function to handle the new QueryObject type without circular import errors using type checking
[0.2.2]: https://bitbucket.org/chromawallet/postchain-client-py/src/0.2.2
