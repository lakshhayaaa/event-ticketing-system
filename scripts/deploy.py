from brownie import EventTicketNFT, accounts, network, config
import os


def main():
    if network.show_active() == "sepolia":
        deployer = accounts.add(os.getenv("PRIVATE_KEY"))
    else:
        deployer = accounts[0]

    ticket = EventTicketNFT.deploy({'from': deployer})
    print(f"EventTicketNFT deployed at: {ticket.address}")

    if network.show_active() != "sepolia":
        organizer = accounts[1]
        ticket.addOrganizer(organizer, {'from': deployer})
        print(f"Organizer role granted to: {organizer.address}")

    return ticket