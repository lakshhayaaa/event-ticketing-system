import json
import sys

import cv2


def scan_ticket_qr(image_path):
    """
    Read a QR code from an image and extract
    the NFT tokenId and eventId.
    """

    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Could not open image '{image_path}'.")
        return None

    detector = cv2.QRCodeDetector()

    data, points, _ = detector.detectAndDecode(image)

    if not data:
        print("Error: No QR code could be detected.")
        return None

    try:
        ticket_data = json.loads(data)
    except json.JSONDecodeError:
        print("Error: QR code does not contain valid ticket data.")
        return None

    if "tokenId" not in ticket_data:
        print("Error: QR code is missing tokenId.")
        return None

    if "eventId" not in ticket_data:
        print("Error: QR code is missing eventId.")
        return None

    try:
        token_id = int(ticket_data["tokenId"])
        event_id = int(ticket_data["eventId"])
    except (ValueError, TypeError):
        print("Error: tokenId and eventId must be numbers.")
        return None

    print("QR code scanned successfully.")
    print(f"Token ID : {token_id}")
    print(f"Event ID : {event_id}")

    return token_id, event_id


def main():
    """
    Command-line entry point.

    Usage:
        python3 scripts/scan_qr.py <qr_image>

    Example:
        python3 scripts/scan_qr.py ticket_0.png
    """

    if len(sys.argv) != 2:
        print("Usage:")
        print("python3 scripts/scan_qr.py <qr_image>")
        return

    image_path = sys.argv[1]

    scan_ticket_qr(image_path)


if __name__ == "__main__":
    main()