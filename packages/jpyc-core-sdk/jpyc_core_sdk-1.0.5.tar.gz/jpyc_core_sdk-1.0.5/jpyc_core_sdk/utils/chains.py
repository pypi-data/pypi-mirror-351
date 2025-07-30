from typing import Final

from .errors import NetworkNotSupported
from .types import ChainMetadata, ChainName
from .validators import RpcEndpoint

##################
# Chain Metadata #
##################

SUPPORTED_CHAINS: Final[ChainMetadata] = {
    "ethereum": {
        "mainnet": {
            "id": 1,
            "name": "Ethereum Mainnet",
            "rpc_endpoints": ["https://ethereum-rpc.publicnode.com"],
        },
        "sepolia": {
            "id": 11155111,
            "name": "Ethereum Sepolia Testnet",
            "rpc_endpoints": ["https://ethereum-sepolia-rpc.publicnode.com"],
        },
    },
    "polygon": {
        "mainnet": {
            "id": 137,
            "name": "Polygon Mainnet",
            "rpc_endpoints": ["https://polygon-rpc.com"],
        },
        "amoy": {
            "id": 80002,
            "name": "Polygon Amoy Testnet",
            "rpc_endpoints": ["https://rpc-amoy.polygon.technology"],
        },
    },
    "gnosis": {
        "mainnet": {
            "id": 100,
            "name": "Gnosis Chain",
            "rpc_endpoints": ["https://rpc.gnosischain.com"],
        },
        "chiado": {
            "id": 10200,
            "name": "Gnosis Chiado Testnet",
            "rpc_endpoints": ["https://rpc.chiadochain.net"],
        },
    },
    "avalanche": {
        "mainnet": {
            "id": 43114,
            "name": "Avalanche C-Chain",
            "rpc_endpoints": ["https://api.avax.network/ext/bc/C/rpc"],
        },
        "fuji": {
            "id": 43113,
            "name": "Avalanche Fuji Testnet",
            "rpc_endpoints": ["https://api.avax-test.network/ext/bc/C/rpc"],
        },
    },
    "astar": {
        "mainnet": {
            "id": 592,
            "name": "Astar Network",
            "rpc_endpoints": ["https://astar.public.blastapi.io"],
        },
    },
    "shiden": {
        "mainnet": {
            "id": 336,
            "name": "Shiden Network",
            "rpc_endpoints": ["https://shiden.public.blastapi.io"],
        },
    },
    "localhost": {
        "devnet": {
            "id": 31337,
            "name": "Localhost Network",
            "rpc_endpoints": ["http://127.0.0.1:8545/"],
        },
    },
}
"""ChainMetadata: Supported chains & networks."""

##################################
# Chain-related helper functions #
##################################


def enumerate_supported_networks() -> str:
    """Enumerate all the supported networks.

    Returns:
        str: supported networks
    """
    return ", ".join(
        f"'{chain}' => {list(networks.keys())}"
        for chain, networks in SUPPORTED_CHAINS.items()
    )


def is_supported_network(
    chain_name: ChainName | None, network_name: str | None
) -> bool:
    """Check if the specified network is supported by the SDK.

    Args:
        chain_name (ChainName, optional): Chain name
        network_name (str, optional): Network name

    Returns:
        bool: True if supported, false otherwise
    """
    return (
        chain_name in SUPPORTED_CHAINS and network_name in SUPPORTED_CHAINS[chain_name]
    )


def get_default_rpc_endpoint(
    chain_name: ChainName | None, network_name: str | None
) -> RpcEndpoint:
    """Get the default RPC endpoint for the specified network.

    Args:
        chain_name (ChainName, optional): Chain name
        network_name (str, optional): Network name

    Returns:
        RpcEndpoint: RPC endpoint

    Raises:
        NetworkNotSupported: If the specified network is not supported by the SDK
    """
    if not is_supported_network(chain_name, network_name):
        raise NetworkNotSupported(chain_name, network_name)  # type: ignore[arg-type]

    return SUPPORTED_CHAINS[chain_name][network_name]["rpc_endpoints"][0]  # type: ignore[index]
