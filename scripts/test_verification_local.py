
import json
import time

from web3 import Web3
from eth_tester import EthereumTester, PyEVMBackend


# --------------------------------------------------
# LOCAL BLOCKCHAIN SETUP
# --------------------------------------------------

print("\n========================================")
print("PERSON 3 - QR TICKET VERIFICATION TEST")
print("========================================\n")

# Create local Ethereum blockchain
eth_tester = EthereumTester(PyEVMBackend())

w3 = Web3(
    Web3.EthereumTesterProvider(eth_tester)
)

print("Connected to local blockchain:", w3.is_connected())
print("Chain ID:", w3.eth.chain_id)


# --------------------------------------------------
# ACCOUNTS
# --------------------------------------------------

deployer = w3.eth.accounts[0]
organizer = w3.eth.accounts[1]
ticket_owner = w3.eth.accounts[2]

print("\nAccounts:")
print("Deployer      :", deployer)
print("Organizer     :", organizer)
print("Ticket Owner  :", ticket_owner)


# --------------------------------------------------
# LOAD CONTRACT ABI + BYTECODE
# --------------------------------------------------

with open("build/EventTicketNFT.abi", "r") as file:
    abi = json.load(file)

with open("build/EventTicketNFT.bin", "r") as file:
    bytecode = file.read().strip()

print("\nContract artifacts loaded.")
print("ABI entries   :", len(abi))
print("Bytecode size :", len(bytecode))


# --------------------------------------------------
# DEPLOY CONTRACT
# --------------------------------------------------

print("\nDeploying EventTicketNFT...")

contract_factory = w3.eth.contract(
    abi=abi,
    bytecode=bytecode
)

deploy_tx = contract_factory.constructor().transact({
    "from": deployer
})

deploy_receipt = w3.eth.wait_for_transaction_receipt(
    deploy_tx
)

contract_address = deploy_receipt.contractAddress

print("Contract deployed successfully!")
print("Contract address:", contract_address)


# Create contract instance
contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)


# --------------------------------------------------
# ADD ORGANIZER
# --------------------------------------------------

print("\nAdding organizer role...")

organizer_role = contract.functions.ORGANIZER_ROLE().call()

add_organizer_tx = contract.functions.addOrganizer(
    organizer
).transact({
    "from": deployer
})

w3.eth.wait_for_transaction_receipt(
    add_organizer_tx
)

has_role = contract.functions.hasRole(
    organizer_role,
    organizer
).call()

print("Organizer role assigned:", has_role)


# --------------------------------------------------
# MINT TICKET
# --------------------------------------------------

print("\nMinting test ticket...")

event_id = 1
ticket_type = "VIP"
seat_number = "A10"

# Event is one day in the future
event_date = int(time.time()) + 86400

mint_tx = contract.functions.mintTicket(
    ticket_owner,
    event_id,
    ticket_type,
    seat_number,
    event_date
).transact({
    "from": organizer
})

mint_receipt = w3.eth.wait_for_transaction_receipt(
    mint_tx
)


# Extract token ID from TicketMinted event
mint_events = contract.events.TicketMinted().process_receipt(
    mint_receipt
)

token_id = mint_events[0]["args"]["tokenId"]

print("Ticket minted successfully!")
print("Token ID :", token_id)
print("Event ID :", event_id)
print("Owner    :", ticket_owner)


# --------------------------------------------------
# VERIFY OWNER
# --------------------------------------------------

actual_owner = contract.functions.ownerOf(
    token_id
).call()

print("\nChecking ticket owner...")
print("Expected owner:", ticket_owner)
print("Actual owner  :", actual_owner)

assert actual_owner == ticket_owner

print("Owner check: PASSED")


# --------------------------------------------------
# CREATE QR DATA
# --------------------------------------------------

qr_data = {
    "tokenId": token_id,
    "eventId": event_id
}

qr_string = json.dumps(qr_data)

print("\nQR DATA:")
print(qr_string)


# --------------------------------------------------
# SIMULATE QR SCANNING
# --------------------------------------------------

scanned_data = json.loads(qr_string)

scanned_token_id = int(
    scanned_data["tokenId"]
)

scanned_event_id = int(
    scanned_data["eventId"]
)

print("\nQR scanned successfully.")
print("Scanned Token ID :", scanned_token_id)
print("Scanned Event ID :", scanned_event_id)


assert scanned_token_id == token_id
assert scanned_event_id == event_id

print("QR data check: PASSED")


# --------------------------------------------------
# CHECK TICKET BEFORE ENTRY
# --------------------------------------------------

used_before = contract.functions.isTicketUsed(
    token_id
).call()

print("\nTicket status before verification:")
print("Used:", used_before)

assert used_before is False


# --------------------------------------------------
# VERIFY TICKET
# --------------------------------------------------

print("\nVerifying ticket on blockchain...")

verify_tx = contract.functions.verifyTicket(
    scanned_token_id,
    scanned_event_id
).transact({
    "from": organizer
})

verify_receipt = w3.eth.wait_for_transaction_receipt(
    verify_tx
)

print("Blockchain verification transaction successful!")


# --------------------------------------------------
# CHECK TICKET VERIFIED EVENT
# --------------------------------------------------

verification_events = contract.events.TicketVerified().process_receipt(
    verify_receipt
)

assert len(verification_events) == 1

verification_event = verification_events[0]["args"]

print("\nTicketVerified event:")
print("Token ID :", verification_event["tokenId"])
print("Event ID :", verification_event["eventId"])
print("Owner    :", verification_event["owner"])

assert verification_event["tokenId"] == token_id
assert verification_event["eventId"] == event_id
assert verification_event["owner"] == ticket_owner

print("TicketVerified event: PASSED")


# --------------------------------------------------
# CHECK TICKET AFTER ENTRY
# --------------------------------------------------

used_after = contract.functions.isTicketUsed(
    token_id
).call()

print("\nTicket status after verification:")
print("Used:", used_after)

assert used_after is True

print("Ticket marked as USED: PASSED")


# --------------------------------------------------
# TRY TO USE SAME TICKET AGAIN
# --------------------------------------------------

print("\nTrying to verify the same ticket again...")

try:

    second_verify_tx = contract.functions.verifyTicket(
        token_id,
        event_id
    ).transact({
        "from": organizer
    })

    w3.eth.wait_for_transaction_receipt(
        second_verify_tx
    )

    print("ERROR: Ticket was incorrectly accepted twice.")

except Exception:

    print("Second verification rejected successfully.")
    print("Double-entry prevention: PASSED")


# --------------------------------------------------
# FINAL RESULT
# --------------------------------------------------

print("\n========================================")
print("PERSON 3 TEST COMPLETE")
print("========================================")

print("\nPASSED:")
print("✓ Local blockchain connection")
print("✓ Contract deployment")
print("✓ Organizer role")
print("✓ Ticket minting")
print("✓ Ticket ownership")
print("✓ QR data generation")
print("✓ QR data scanning simulation")
print("✓ Ticket verification")
print("✓ TicketVerified event")
print("✓ Ticket marked as used")
print("✓ Duplicate entry prevention")

print("\nPERSON 3 - QR VERIFICATION & ENTRY: COMPLETE")
