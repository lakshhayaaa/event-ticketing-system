import json
import sys

import qrcode


def generate_ticket_qr(token_id, event_id):
    """
    Generate a QR code containing the NFT ticket information.

    The QR contains only:
    - tokenId
    - eventId

    It does NOT contain any private key or secret information.
    """

    ticket_data = {
        "tokenId": int(token_id),
        "eventId": int(event_id)
    }

    qr_data = json.dumps(ticket_data)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    image = qr.make_image()

    filename = f"ticket_{token_id}.png"
    image.save(filename)

    print("QR code generated successfully.")
    print(f"Token ID : {token_id}")
    print(f"Event ID : {event_id}")
    print(f"Saved as : {filename}")


def main():
    """
    Command-line entry point.

    Usage:
        python3 scripts/generate_qr.py <token_id> <event_id>

    Example:
        python3 scripts/generate_qr.py 0 1
    """

    if len(sys.argv) != 3:
        print("Usage:")
        print("python3 scripts/generate_qr.py <token_id> <event_id>")
        return

    token_id = sys.argv[1]
    event_id = sys.argv[2]

    try:
        int(token_id)
        int(event_id)
    except ValueError:
        print("Error: tokenId and eventId must be numbers.")
        return

    generate_ticket_qr(
        token_id,
        event_id
    )


if __name__ == "__main__":
    main()