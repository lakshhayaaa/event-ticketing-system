import pytest
import time
from brownie import EventTicketNFT, accounts, reverts


@pytest.fixture
def ticket_contract():
    ticket = EventTicketNFT.deploy({'from': accounts[0]})
    ticket.addOrganizer(accounts[1], {'from': accounts[0]})
    return ticket

def test_organizer_can_mint(ticket_contract):
    future_date = int(time.time()) + 86400
    tx = ticket_contract.mintTicket(
        accounts[2], 1, "VIP", "A12", future_date, {'from': accounts[1]}
    )

    assert ticket_contract.ownerOf(0) == accounts[2]
    assert tx.events['TicketMinted']['eventId'] == 1
    assert tx.events['TicketMinted']['organizer'] == accounts[1]

def test_non_organizer_cannot_mint(ticket_contract):
    future_date = int(time.time()) + 86400
    with reverts():
        ticket_contract.mintTicket(
            accounts[2], 1, "VIP", "A13", future_date, {'from': accounts[2]}
        )

def test_cannot_mint_past_date(ticket_contract):
    past_date = int(time.time()) - 86400
    with reverts("Event date must be in the future"):
        ticket_contract.mintTicket(
            accounts[2], 1, "VIP", "A14", past_date, {'from': accounts[1]}
        )

def test_ticket_data_stored_correctly(ticket_contract):
    future_date = int(time.time()) + 86400
    ticket_contract.mintTicket(
        accounts[2], 5, "General", "B07", future_date, {'from': accounts[1]}
    )

    ticket_data = ticket_contract.getTicketDetails(0)

    assert ticket_data['eventId'] == 5
    assert ticket_data['ticketType'] == "General"
    assert ticket_data['seatNumber'] == "B07"
    assert ticket_data['organizer'] == accounts[1]
    assert ticket_data['isUsed'] == False

def test_admin_can_add_organizer(ticket_contract):
    ticket_contract.addOrganizer(accounts[3], {'from': accounts[0]})
    assert ticket_contract.hasRole(ticket_contract.ORGANIZER_ROLE(), accounts[3]) == True


def test_non_admin_cannot_add_organizer(ticket_contract):
    with reverts():
        ticket_contract.addOrganizer(accounts[3], {'from': accounts[2]})
