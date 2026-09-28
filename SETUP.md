# Event Ticketing System — Setup Guide

This document explains how to set up and run the Event Ticketing System locally.

The project uses:

- Solidity smart contracts
- Ethereum-compatible local blockchain
- Web3.py
- OpenZeppelin Contracts
- QR code generation
- QR code scanning
- Python testing

---

# 1. Project Structure

After cloning the repository, the project should look approximately like this:

```text
event-ticketing-system/
│
├── contracts/
│   └── EventTicketNFT.sol
│
├── scripts/
│   ├── generate_qr.py
│   ├── scan_qr.py
│   └── test_verification_local.py
│
├── tests/
│   ├── test_minting.py
│   ├── test_ticket_management.py
│   └── test_ticket_verification.py
│
├── lib/
│   └── openzeppelin-contracts/
│
├── build/
│   ├── EventTicketNFT.abi
│   └── EventTicketNFT.bin
│
├── requirements.txt
├── brownie-config.yaml
├── SETUP.md
└── README.md
