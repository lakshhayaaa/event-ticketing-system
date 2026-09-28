from brownie import EventTicketNFT, accounts, chain, Wei, reverts


def test_transfer_and_ownership_history():

    deployer = accounts[0]
    organizer = accounts[1]
    owner = accounts[2]
    new_owner = accounts[3]

    # Deploy contract
    contract = EventTicketNFT.deploy({"from": deployer})

    # Add organizer
    contract.addOrganizer(
        organizer,
        {"from": deployer}
    )

    # Create future event date
    event_date = chain.time() + 86400

    # Mint ticket
    tx = contract.mintTicket(
        owner,
        1,
        "VIP",
        "A1",
        event_date,
        {"from": organizer}
    )

    token_id = tx.events["TicketMinted"]["tokenId"]

    # Check initial owner
    assert contract.ownerOf(token_id) == owner

    # Transfer ticket
    contract.transferTicket(
        new_owner,
        token_id,
        {"from": owner}
    )

    # Check new owner
    assert contract.ownerOf(token_id) == new_owner

    # Check ownership history
    history = contract.getOwnershipHistory(token_id)

    assert history[0] == owner
    assert history[1] == new_owner

    # Check ownership timestamps
    timestamps = contract.getOwnershipTimestamps(token_id)

    assert len(timestamps) == 2
    assert timestamps[0] > 0
    assert timestamps[1] >= timestamps[0]


def test_ticket_resale():

    deployer = accounts[0]
    organizer = accounts[1]
    seller = accounts[2]
    buyer = accounts[3]

    # Deploy contract
    contract = EventTicketNFT.deploy({"from": deployer})

    # Add organizer
    contract.addOrganizer(
        organizer,
        {"from": deployer}
    )

    # Future event
    event_date = chain.time() + 86400

    # Mint ticket
    tx = contract.mintTicket(
        seller,
        1,
        "VIP",
        "B1",
        event_date,
        {"from": organizer}
    )

    token_id = tx.events["TicketMinted"]["tokenId"]

    # Set resale price
    price = Wei("0.01 ether")

    # Seller lists ticket
    contract.listTicketForResale(
        token_id,
        price,
        {"from": seller}
    )

    # Check listing
    listing = contract.getResaleListing(token_id)

    assert listing[0] == seller
    assert listing[1] == price
    assert listing[2] is True

    # Buyer purchases ticket
    contract.buyResaleTicket(
        token_id,
        {"from": buyer, "value": price}
    )

    # Check new owner
    assert contract.ownerOf(token_id) == buyer

    # Listing should be inactive/deleted
    listing = contract.getResaleListing(token_id)

    assert listing[2] is False

    # Check ownership history after resale
    history = contract.getOwnershipHistory(token_id)

    assert history[0] == seller
    assert history[1] == buyer

    # Check ownership timestamps after resale
    timestamps = contract.getOwnershipTimestamps(token_id)

    assert len(timestamps) == 2
    assert timestamps[0] > 0
    assert timestamps[1] >= timestamps[0]


def test_only_owner_can_transfer():

    deployer = accounts[0]
    organizer = accounts[1]
    owner = accounts[2]
    attacker = accounts[3]

    # Deploy contract
    contract = EventTicketNFT.deploy({"from": deployer})

    # Add organizer
    contract.addOrganizer(
        organizer,
        {"from": deployer}
    )

    # Future event
    event_date = chain.time() + 86400

    # Mint ticket
    tx = contract.mintTicket(
        owner,
        1,
        "VIP",
        "C1",
        event_date,
        {"from": organizer}
    )

    token_id = tx.events["TicketMinted"]["tokenId"]

    # Attacker should not be able to transfer the ticket
    with reverts("Not ticket owner"):
        contract.transferTicket(
            attacker,
            token_id,
            {"from": attacker}
        )

    # Ownership must remain unchanged
    assert contract.ownerOf(token_id) == owner

