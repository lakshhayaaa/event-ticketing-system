import { useState } from "react";
import { BrowserProvider } from "ethers";
import "./App.css";

function App() {
  const [account, setAccount] = useState("");
  const [error, setError] = useState("");

  const connectWallet = async () => {
    try {
      setError("");

      if (!window.ethereum) {
        setError("MetaMask is not installed.");
        return;
      }

      const provider = new BrowserProvider(window.ethereum);

      const accounts = await provider.send("eth_requestAccounts", []);

      setAccount(accounts[0]);
    } catch (err) {
      console.error(err);
      setError("Could not connect wallet.");
    }
  };

  return (
    <div className="app">
      <h1>🎟️ Blockchain Event Ticketing</h1>

      <p>NFT-based ticket ownership and verification system</p>

      {!account ? (
        <button onClick={connectWallet}>Connect MetaMask</button>
      ) : (
        <div>
          <h3>Wallet Connected ✅</h3>
          <p>{account}</p>
        </div>
      )}

      {error && <p>{error}</p>}
    </div>
  );
}

export default App;