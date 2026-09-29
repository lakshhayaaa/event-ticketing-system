from brownie import EventTicketNFT, accounts, chain
import pytest


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def deploy_contract():
    deployer = accounts[0]
    organizer = accounts[1]

    contract = EventTicketNFT.deploy({"from": deployer})
    contract.addOrganizer(organizer, {"from": deployer})

    return contract, deployer, organizer


# --------------------------------------------------
# CREATE EVENT
# --------------------------------------------------

def test_organizer_can_create_event():
    contract, deployer, organizer = deploy_contract()

    event_date = chain.time() + 86400

    tx = contract.createEvent(
        "Music Festival",
        "Coimbatore Stadium",
        event_date,
        500,
        100,
        {"from": organizer}
    )

    event_id = tx.return_value

    assert event_id == 1

    event = contract.getEventDetails(event_id)

    assert event[0] == 1
    assert event[1] == "Music Festival"
    assert event[2] == "Coimbatore Stadium"
    assert event[3] == event_date
    assert event[4] == 500
    assert event[5] == 100
    assert event[6] == 0
    assert event[7] is True


# --------------------------------------------------
# ACCESS CONTROL
# --------------------------------------------------

def test_non_organizer_cannot_create_event():
    contract, deployer, organizer = deploy_contract()

    event_date = chain.time() + 86400

    with pytest.raises(Exception):
        contract.createEvent(
            "Music Festival",
            "Coimbatore Stadium",
            event_date,
            500,
            100,
            {"from": accounts[2]}
        )


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def test_past_event_rejected():
    contract, deployer, organizer = deploy_contract()

    past_date = chain.time() - 86400

    with pytest.raises(Exception):
        contract.createEvent(
            "Music Festival",
            "Coimbatore Stadium",
            past_date,
            500,
            100,
            {"from": organizer}
        )


def test_empty_event_name_rejected():
    contract, deployer, organizer = deploy_contract()

    event_date = chain.time() + 86400

    with pytest.raises(Exception):
        contract.createEvent(
            "",
            "Coimbatore Stadium",
            event_date,
            500,
            100,
            {"from": organizer}
        )


def test_empty_venue_rejected():
    contract, deployer, organizer = deploy_contract()

    event_date = chain.time() + 86400

    with pytest.raises(Exception):
        contract.createEvent(
            "Music Festival",
            "",
            event_date,
            500,
            100,
            {"from": organizer}
        )


def test_zero_total_tickets_rejected():
    contract, deployer, organizer = deploy_contract()

    event_date = chain.time() + 86400

    with pytest.raises(Exception):
        contract.createEvent(
            "Music Festival",
            "Coimbatore Stadium",
            event_date,
            500,
            0,
            {"from": organizer}
        )


# --------------------------------------------------
# EVENT QUERIES
# --------------------------------------------------

def test_event_exists():
    contract, deployer, organizer = deploy_contract()

    event_date = chain.time() + 86400

    contract.createEvent(
        "Music Festival",
        "Coimbatore Stadium",
        event_date,
        500,
        100,
        {"from": organizer}
    )

    assert contract.eventExists(1) is True
    assert contract.eventExists(999) is False


def test_tickets_remaining():
    contract, deployer, organizer = deploy_contract()

    event_date = chain.time() + 86400

    contract.createEvent(
        "Music Festival",
        "Coimbatore Stadium",
        event_date,
        500,
        100,
        {"from": organizer}
    )

    assert contract.getTicketsRemaining(1) == 100


def test_event_revenue_initially_zero():
    contract, deployer, organizer = deploy_contract()

    event_date = chain.time() + 86400

    contract.createEvent(
        "Music Festival",
        "Coimbatore Stadium",
        event_date,
        500,
        100,
        {"from": organizer}
    )

    assert contract.getEventRevenue(1) == 0


def test_nonexistent_event_rejected():
    contract, deployer, organizer = deploy_contract()

    with pytest.raises(Exception):
        contract.getEventDetails(999)

    with pytest.raises(Exception):
        contract.getTicketsRemaining(999)

    with pytest.raises(Exception):
        contract.getEventRevenue(999)