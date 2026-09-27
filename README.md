# event-ticketing-system
The ticketing system is designed using NFT's, smart contract and block-chain based  ownership of tickets to prevent double selling, faking of tickets and to prohibit bypassing if the owner's resale rules.

## Development Setup (Smart Contract Module)

This project uses **Brownie** (Python-based Ethereum development framework) with **Solidity** contracts.

### Prerequisites
- Python 3.8–3.10 (Brownie doesn't fully support 3.11+ yet)
- `pip`
- Git

### 1. Clone the repo
\`\`\`bash
git clone <repo-url>
cd event-ticketing-system
\`\`\`

### 2. Create and activate a virtual environment
\`\`\`bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\Activate.ps1     # Windows PowerShell
\`\`\`
You should see `(venv)` in your terminal prompt once activated.

### 3. Install Brownie
\`\`\`bash
pip install eth-brownie
\`\`\`

Verify:
\`\`\`bash
brownie --version
\`\`\`

### 4. Install project dependencies (OpenZeppelin contracts)
The dependency is already declared in `brownie-config.yaml`. Just run:
\`\`\`bash
brownie pm install OpenZeppelin/openzeppelin-contracts@5.0.2
\`\`\`

Confirm it installed:
\`\`\`bash
brownie pm list
\`\`\`

### 5. Compile contracts
\`\`\`bash
brownie compile
\`\`\`

### 6. Run tests
\`\`\`bash
brownie test
\`\`\`

### 7. Run scripts (e.g. local deployment)
\`\`\`bash
brownie run scripts/deploy.py
\`\`\`

### 8. Interactive console (for manual testing/debugging)
\`\`\`bash
brownie console
\`\`\`

---

### Project structure
| Folder | Purpose |
|---|---|
| `contracts/` | Solidity smart contracts |
| `interfaces/` | Solidity interface files |
| `scripts/` | Python deployment/interaction scripts |
| `tests/` | Python (pytest) test files |
| `build/` | Auto-generated compiled artifacts — do not edit manually |
| `reports/` | Auto-generated gas/coverage reports |

### Notes
- Never commit `venv/` (or your local env folder), `build/`, `reports/`, or `.env` — these are in `.gitignore`.
- If you add a new dependency (e.g. another OpenZeppelin module or library), add it to `brownie-config.yaml` under `dependencies:` and `compiler.solc.remappings:` so everyone stays in sync — don't install it locally only.
- Testnet deployment (Sepolia) requires a `.env` file with an RPC URL and a funded test wallet's private key — ask [whoever owns deployment] for the shared `.env.example` template before creating your own.