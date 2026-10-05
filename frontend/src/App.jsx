import { useEffect, useState } from "react";
import { formatEther, parseEther } from "ethers";
import {
  connectWallet,
  getReadContract,
  getWriteContract,
  switchToLocalNetwork,
} from "./blockchain/contract";
import "./App.css";

function App() {
  const [account, setAccount] = useState("");
  const [chainId, setChainId] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [eventId, setEventId] = useState("1");
  const [event, setEvent] = useState(null);

  const [tokenId, setTokenId] = useState("0");
  const [ticket, setTicket] = useState(null);
  const [owner, setOwner] = useState("");
  const [history, setHistory] = useState([]);

  const [transferTo, setTransferTo] = useState("");
  const [resalePrice, setResalePrice] = useState("");

  const [eventName, setEventName] = useState("");
  const [eventVenue, setEventVenue] = useState("");
  const [eventDate, setEventDate] = useState("");
  const [eventPrice, setEventPrice] = useState("");
  const [totalTickets, setTotalTickets] = useState("");

  const [mintTo, setMintTo] = useState("");
  const [mintEventId, setMintEventId] = useState("");
  const [ticketType, setTicketType] = useState("");
  const [seatNumber, setSeatNumber] = useState("");
  const [mintEventDate, setMintEventDate] = useState("");

  const [verifyEventId, setVerifyEventId] = useState("");

  useEffect(() => {
    if (!window.ethereum) return;

    window.ethereum
      .request({ method: "eth_accounts" })
      .then((accounts) => {
        if (accounts.length > 0) {
          setAccount(accounts[0]);
        }
      });

    window.ethereum
      .request({ method: "eth_chainId" })
      .then((id) => {
        setChainId(parseInt(id, 16));
      });

    window.ethereum.on?.("accountsChanged", (accounts) => {
      setAccount(accounts[0] || "");
    });

    window.ethereum.on?.("chainChanged", (id) => {
      setChainId(parseInt(id, 16));
    });
  }, []);

  const handleConnect = async () => {
    try {
      setError("");
      setMessage("Connecting wallet...");

      const result = await connectWallet();

      setAccount(result.account);
      setChainId(result.chainId);
      setMessage("Wallet connected.");
    } catch (err) {
      console.error(err);
      setError(err.message);
      setMessage("");
    }
  };

  const loadEvent = async () => {
    try {
      setError("");
      setMessage("Loading event...");

      const contract = getReadContract();

      const data = await contract.getEventDetails(eventId);
      const remaining = await contract.getTicketsRemaining(eventId);
      const revenue = await contract.getEventRevenue(eventId);

      setEvent({
        id: data.eventId.toString(),
        name: data.name,
        venue: data.venue,
        date: new Date(
          Number(data.eventDate) * 1000
        ).toLocaleString(),
        price: formatEther(data.ticketPrice),
        totalTickets: data.totalTickets.toString(),
        ticketsSold: data.ticketsSold.toString(),
        remaining: remaining.toString(),
        revenue: formatEther(revenue),
        active: data.active,
      });

      setMessage("Event loaded.");
    } catch (err) {
      console.error(err);
      setError(err.shortMessage || err.message);
      setMessage("");
    }
  };

  const loadTicket = async () => {
    try {
      setError("");
      setMessage("Loading ticket...");

      const contract = getReadContract();

      const data = await contract.getTicketDetails(tokenId);
      const currentOwner = await contract.getTicketOwner(tokenId);
      const owners = await contract.getOwnershipHistory(tokenId);
      const timestamps =
        await contract.getOwnershipTimestamps(tokenId);

      setTicket({
        eventId: data.eventId.toString(),
        ticketType: data.ticketType,
        seatNumber: data.seatNumber,
        eventDate: new Date(
          Number(data.eventDate) * 1000
        ).toLocaleString(),
        organizer: data.organizer,
        used: data.isUsed,
      });

      setOwner(currentOwner);

      setHistory(
        owners.map((address, index) => ({
          address,
          time: new Date(
            Number(timestamps[index]) * 1000
          ).toLocaleString(),
        }))
      );

      setMessage("Ticket loaded.");
    } catch (err) {
      console.error(err);
      setError(err.shortMessage || err.message);
      setMessage("");
    }
  };

  const sendTransaction = async (action) => {
    try {
      setError("");

      if (!account) {
        throw new Error("Connect your wallet first.");
      }

      await switchToLocalNetwork();

      const contract = await getWriteContract();

      setMessage("Waiting for wallet confirmation...");

      const tx = await action(contract);

      setMessage("Transaction submitted. Waiting...");

      await tx.wait();

      setMessage("Transaction confirmed.");
    } catch (err) {
      console.error(err);
      setError(
        err.shortMessage ||
          err.reason ||
          err.message ||
          "Transaction failed."
      );
      setMessage("");
    }
  };

  const transferTicket = () =>
    sendTransaction((contract) =>
      contract.transferTicket(transferTo, tokenId)
    );

  const listForResale = () =>
    sendTransaction((contract) =>
      contract.listTicketForResale(
        tokenId,
        parseEther(resalePrice)
      )
    );

  const cancelResale = () =>
    sendTransaction((contract) =>
      contract.cancelResale(tokenId)
    );

  const buyResale = async () => {
    await sendTransaction(async (contract) => {
      const listing =
        await contract.getResaleListing(tokenId);

      return contract.buyResaleTicket(tokenId, {
        value: listing.price,
      });
    });
  };

  const createEvent = () =>
    sendTransaction((contract) =>
      contract.createEvent(
        eventName,
        eventVenue,
        Math.floor(new Date(eventDate).getTime() / 1000),
        parseEther(eventPrice),
        totalTickets
      )
    );

  const mintTicket = () =>
    sendTransaction((contract) =>
      contract.mintTicket(
        mintTo,
        mintEventId,
        ticketType,
        seatNumber,
        Math.floor(
          new Date(mintEventDate).getTime() / 1000
        )
      )
    );

  const verifyTicket = () =>
    sendTransaction((contract) =>
      contract.verifyTicket(
        tokenId,
        verifyEventId
      )
    );

  return (
    <div className="app">
      <header>
        <div>
          <h1>ETIX</h1>
          <p>Blockchain Event Ticketing</p>
        </div>

        <div className="wallet">
          {account ? (
            <>
              <span>Chain {chainId}</span>
              <strong>
                {account.slice(0, 6)}...
                {account.slice(-4)}
              </strong>
            </>
          ) : (
            <button onClick={handleConnect}>
              Connect Wallet
            </button>
          )}
        </div>
      </header>

      <section className="hero">
        <h2>Own the ticket. Verify the owner.</h2>
        <p>
          NFT ticketing with ownership, resale and
          on-chain entry verification.
        </p>
      </section>

      <main>
        <section className="card">
          <h3>Event Lookup</h3>

          <input
            value={eventId}
            onChange={(e) => setEventId(e.target.value)}
            placeholder="Event ID"
          />

          <button onClick={loadEvent}>
            Load Event
          </button>

          {event && (
            <div className="details">
              <p><b>Name:</b> {event.name}</p>
              <p><b>Venue:</b> {event.venue}</p>
              <p><b>Date:</b> {event.date}</p>
              <p><b>Price:</b> {event.price} ETH</p>
              <p><b>Total:</b> {event.totalTickets}</p>
              <p><b>Sold:</b> {event.ticketsSold}</p>
              <p><b>Remaining:</b> {event.remaining}</p>
              <p><b>Revenue:</b> {event.revenue} ETH</p>
            </div>
          )}
        </section>

        <section className="card">
          <h3>Ticket Lookup</h3>

          <input
            value={tokenId}
            onChange={(e) => setTokenId(e.target.value)}
            placeholder="Token ID"
          />

          <button onClick={loadTicket}>
            Load Ticket
          </button>

          {ticket && (
            <div className="details">
              <p><b>Event ID:</b> {ticket.eventId}</p>
              <p><b>Type:</b> {ticket.ticketType}</p>
              <p><b>Seat:</b> {ticket.seatNumber}</p>
              <p><b>Date:</b> {ticket.eventDate}</p>
              <p><b>Used:</b> {ticket.used ? "Yes" : "No"}</p>
              <p><b>Owner:</b> {owner}</p>
            </div>
          )}
        </section>

        <section className="card">
          <h3>Transfer Ticket</h3>

          <input
            value={transferTo}
            onChange={(e) => setTransferTo(e.target.value)}
            placeholder="Recipient 0x..."
          />

          <button onClick={transferTicket}>
            Transfer
          </button>
        </section>

        <section className="card">
          <h3>Resale</h3>

          <input
            value={resalePrice}
            onChange={(e) => setResalePrice(e.target.value)}
            placeholder="Price in ETH"
          />

          <button onClick={listForResale}>
            List for Resale
          </button>

          <button onClick={cancelResale}>
            Cancel Listing
          </button>

          <button onClick={buyResale}>
            Buy Listed Ticket
          </button>
        </section>

        <section className="card">
          <h3>Create Event</h3>

          <input
            placeholder="Event name"
            value={eventName}
            onChange={(e) => setEventName(e.target.value)}
          />

          <input
            placeholder="Venue"
            value={eventVenue}
            onChange={(e) => setEventVenue(e.target.value)}
          />

          <input
            type="datetime-local"
            value={eventDate}
            onChange={(e) => setEventDate(e.target.value)}
          />

          <input
            placeholder="Ticket price ETH"
            value={eventPrice}
            onChange={(e) => setEventPrice(e.target.value)}
          />

          <input
            placeholder="Total tickets"
            value={totalTickets}
            onChange={(e) => setTotalTickets(e.target.value)}
          />

          <button onClick={createEvent}>
            Create Event
          </button>
        </section>

        <section className="card">
          <h3>Mint Ticket</h3>

          <input
            placeholder="Recipient 0x..."
            value={mintTo}
            onChange={(e) => setMintTo(e.target.value)}
          />

          <input
            placeholder="Event ID"
            value={mintEventId}
            onChange={(e) => setMintEventId(e.target.value)}
          />

          <input
            placeholder="Ticket type"
            value={ticketType}
            onChange={(e) => setTicketType(e.target.value)}
          />

          <input
            placeholder="Seat number"
            value={seatNumber}
            onChange={(e) => setSeatNumber(e.target.value)}
          />

          <input
            type="datetime-local"
            value={mintEventDate}
            onChange={(e) =>
              setMintEventDate(e.target.value)
            }
          />

          <button onClick={mintTicket}>
            Mint NFT Ticket
          </button>
        </section>

        <section className="card">
          <h3>Verify Ticket</h3>

          <input
            placeholder="Expected Event ID"
            value={verifyEventId}
            onChange={(e) =>
              setVerifyEventId(e.target.value)
            }
          />

          <button onClick={verifyTicket}>
            Verify & Mark Used
          </button>
        </section>

        {history.length > 0 && (
          <section className="card">
            <h3>Ownership History</h3>

            {history.map((item, index) => (
              <div key={index} className="historyRow">
                <b>{index + 1}</b>
                <span>{item.address}</span>
                <span>{item.time}</span>
              </div>
            ))}
          </section>
        )}
      </main>

      {message && (
        <div className="status success">
          {message}
        </div>
      )}

      {error && (
        <div className="status error">
          {error}
        </div>
      )}
    </div>
  );
}

export default App;