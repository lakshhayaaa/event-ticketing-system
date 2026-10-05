import {
  BrowserProvider,
  Contract,
  JsonRpcProvider,
} from "ethers";

import { CONTRACT_ABI } from "./abi";

export const LOCAL_RPC_URL =
  import.meta.env.VITE_RPC_URL || "http://127.0.0.1:8545";

export const LOCAL_CHAIN_ID = Number(
  import.meta.env.VITE_CHAIN_ID || 31337
);

export const LOCAL_CHAIN_ID_HEX =
  `0x${LOCAL_CHAIN_ID.toString(16)}`;

export const CONTRACT_ADDRESS =
  import.meta.env.VITE_CONTRACT_ADDRESS ||
  "0x5FbDB2315678afecb367f032d93F642f64180aa3";

export function getReadContract() {
  const provider = new JsonRpcProvider(LOCAL_RPC_URL);

  return new Contract(
    CONTRACT_ADDRESS,
    CONTRACT_ABI,
    provider
  );
}

export async function connectWallet() {
  if (!window.ethereum) {
    throw new Error(
      "No wallet detected. Install Rabby or MetaMask."
    );
  }

  const provider = new BrowserProvider(window.ethereum);

  const accounts = await provider.send(
    "eth_requestAccounts",
    []
  );

  const network = await provider.getNetwork();

  return {
    provider,
    account: accounts[0],
    chainId: Number(network.chainId),
  };
}

export async function switchToLocalNetwork() {
  if (!window.ethereum) {
    throw new Error("No wallet detected.");
  }

  try {
    await window.ethereum.request({
      method: "wallet_switchEthereumChain",
      params: [
        {
          chainId: LOCAL_CHAIN_ID_HEX,
        },
      ],
    });
  } catch (error) {
    if (error.code === 4902) {
      await window.ethereum.request({
        method: "wallet_addEthereumChain",
        params: [
          {
            chainId: LOCAL_CHAIN_ID_HEX,
            chainName: "Anvil Local",
            nativeCurrency: {
              name: "Ethereum",
              symbol: "ETH",
              decimals: 18,
            },
            rpcUrls: [LOCAL_RPC_URL],
          },
        ],
      });
    } else {
      throw error;
    }
  }
}

export async function getWriteContract() {
  if (!window.ethereum) {
    throw new Error("No wallet detected.");
  }

  await switchToLocalNetwork();

  const provider =
    new BrowserProvider(window.ethereum);

  const signer = await provider.getSigner();

  return new Contract(
    CONTRACT_ADDRESS,
    CONTRACT_ABI,
    signer
  );
}