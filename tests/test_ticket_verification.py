import time

from brownie import EventTicketNFT, accounts, reverts


def deploy_ticket():
    """
    Deploy the EventTicketNFT contract and create
    one organizer account.
    """

    deployer = accounts[0]
    organizer = accounts[1]

    contract = EventTicketNFT.deploy(
        {"from": deployer}
    )

    contract.addOrganizer(
        organizer,
        {"from": deployer}
    )

    return contract, deployer, organizer


def mint_test_ticket(contract, organizer):
    """
    Mint one test ticket for accounts[2].
    """

    owner = accounts[2]

    future_date = int(time.time()) + 86400

    tx = contract.mintTicket(
        owner,
        1,
        "VIP",
        "A10",
        future_date,
        {"from": organizer}
    )

    token_id = tx.events["TicketMinted"]["tokenId"]

    return token_id, owner


def test_organizer_can_verify_valid_ticket():

    contract, deployer, organizer = deploy_ticket()

    token_id, owner = mint_test_ticket(
        contract,
        organizer
    )

    # Ticket should initially be unused
    assert contract.isTicketUsed(token_id) is False

    # Organizer verifies the ticket
    tx = contract.verifyTicket(
        token_id,
        1,
        {"from": organizer}
    )

    # Ticket should now be marked as used
    assert contract.isTicketUsed(token_id) is True

    # Check TicketVerified event
    assert tx.events["TicketVerified"]["tokenId"] == token_id
    assert tx.events["TicketVerified"]["owner"] == owner
    assert tx.events["TicketVerified"]["organizer"] == organizer
    assert tx.events["TicketVerified"]["eventId"] == 1


def test_wrong_event_id_is_rejected():

    contract, deployer, organizer = deploy_ticket()

    token_id, owner = mint_test_ticket(
        contract,
        organizer
    )

    # QR contains the wrong event ID
    with reverts("Ticket belongs to another event"):
        contract.verifyTicket(
            token_id,
            999,
            {"from": organizer}
        )

    # Ticket must remain unused
    assert contract.isTicketUsed(token_id) is False


def test_already_used_ticket_is_rejected():

    contract, deployer, organizer = deploy_ticket()

    token_id, owner = mint_test_ticket(
        contract,
        organizer
    )

    # First verification
    contract.verifyTicket(
        token_id,
        1,
        {"from": organizer}
    )

    # Second verification should fail
    with reverts("Ticket already used"):
        contract.verifyTicket(
            token_id,
            1,
            {"from": organizer}
        )

    # Ticket remains used
    assert contract.isTicketUsed(token_id) is True


def test_non_organizer_cannot_verify_ticket():

    contract, deployer, organizer = deploy_ticket()

    token_id, owner = mint_test_ticket(
        contract,
        organizer
    )

    non_organizer = accounts[3]

    # Non-organizer should not be allowed
    # to verify or consume tickets
    with reverts():
        contract.verifyTicket(
            token_id,
            1,
            {"from": non_organizer}
        )

    # Ticket must remain unused
    assert contract.isTicketUsed(token_id) is False


def test_ticket_owner_is_correct_before_verification():

    contract, deployer, organizer = deploy_ticket()

    token_id, owner = mint_test_ticket(
        contract,
        organizer
    )

    # The QR scanner should verify the current
    # owner of the NFT
    assert contract.ownerOf(token_id) == owner

    # Ticket has not been used yet
    assert contract.isTicketUsed(token_id) is False


def test_nonexistent_ticket_cannot_be_verified():

    contract, deployer, organizer = deploy_ticket()

    nonexistent_token_id = 999

    with reverts():
        contract.verifyTicket(
            nonexistent_token_id,
            1,
            {"from": organizer}
        )