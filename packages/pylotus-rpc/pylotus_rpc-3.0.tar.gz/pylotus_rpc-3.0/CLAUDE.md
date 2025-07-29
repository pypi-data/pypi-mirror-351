# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyLotus-RPC is a Python client library for the Lotus JSON-RPC API, enabling Python applications to interact with Filecoin blockchain nodes. The library provides type-safe access to chain data, state queries, and network operations.

## Development Commands

**Testing:**
```bash
pytest                    # Run all tests
pytest -m integration     # Run integration tests only
python main.py           # Run example/test script with real blockchain data
```

**Build & Package:**
```bash
python -m build          # Build package
./build_publish.sh       # Build and publish to PyPI
python -m twine upload dist/*  # Manual upload
```

## Architecture

### 3-Layer Design Pattern

1. **HTTP JSON-RPC Connector** (`http_json_rpc_connector.py`)
   - Low-level HTTP communication with Lotus nodes
   - Handles authentication, error responses, and JSON-RPC payload construction
   - Entry point: `_make_payload()` method for all API calls

2. **Methods Layer** (`pylotus_rpc/methods/`)
   - `chain.py`: Blockchain operations (blocks, tipsets, messages)
   - `state.py`: State queries (miners, sectors, market data)  
   - `net.py`: Network operations (peers, bandwidth, connections)
   - All implementation functions prefixed with `_` (e.g., `_head()`, `_get_block()`)

3. **Client Interface** (`lotus_client.py`)
   - `LotusClient` main class with nested interfaces:
     - `LotusClient.Chain`: Chain operations
     - `LotusClient.State`: State queries
     - `LotusClient.Net`: Network management

### Type System (`pylotus_rpc/types/`)

All Filecoin entities are dataclasses with `from_dict()` factory methods:
- **Core Types**: `Tipset`, `BlockHeader`, `Message`, `Cid`
- **Miner/Sector Types**: `MinerInfo`, `MinerPower`, `Sector`, `Deadline`
- **Market Types**: `DealProposal`, `DealState`

## Code Conventions

- **Private Methods**: Implementation methods prefixed with `_`
- **Type Safety**: Use `Optional[Tipset]` for blockchain state parameters
- **Error Handling**: Use `ApiCallError` for API-related exceptions
- **Testing**: Mark integration tests with `@pytest.mark.integration`
- **JSON-RPC**: All API calls go through `_make_payload()` in the connector

## Key Files

- `main.py`: Comprehensive usage examples and manual testing
- `lotus_client.py`: Primary user interface
- `http_json_rpc_connector.py`: Core communication layer
- `requirements.txt`: Only `requests` and `pytest` dependencies