// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract EventTicketNFT is ERC721, AccessControl {

    bytes32 public constant ORGANIZER_ROLE = keccak256("ORGANIZER_ROLE");

    struct Ticket {
        uint256 eventId;
        string ticketType;
        string seatNumber;
        uint256 eventDate;
        address organizer;
        bool isUsed;
    }

    mapping(uint256 => Ticket) public tickets;

    uint256 private _nextTokenId;

    event TicketMinted(uint256 indexed tokenId, uint256 indexed eventId, address indexed organizer);

    constructor() ERC721("EventTicketNFT", "ETIX") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function addOrganizer(address organizer) public onlyRole(DEFAULT_ADMIN_ROLE) {
        _grantRole(ORGANIZER_ROLE, organizer);
    }

    function mintTicket(
        address to,
        uint256 eventId,
        string memory ticketType,
        string memory seatNumber,
        uint256 eventDate
    ) public onlyRole(ORGANIZER_ROLE) returns (uint256) {
        require(to != address(0), "Cannot mint to zero address");
        require(eventDate > block.timestamp, "Event date must be in the future");

        uint256 tokenId = _nextTokenId;
        _nextTokenId++;

        _safeMint(to, tokenId);

        tickets[tokenId] = Ticket({
            eventId: eventId,
            ticketType: ticketType,
            seatNumber: seatNumber,
            eventDate: eventDate,
            organizer: msg.sender,
            isUsed: false
        });

        emit TicketMinted(tokenId, eventId, msg.sender);
        return tokenId;
    }

    function getTicketDetails(uint256 tokenId) public view returns (Ticket memory) {
        _requireOwned(tokenId);
        return tickets[tokenId];
    }

    function supportsInterface(bytes4 interfaceId)
        public view override(ERC721, AccessControl) returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}