// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract EventTicketNFT is ERC721, AccessControl {

    bytes32 public constant ORGANIZER_ROLE =
        keccak256("ORGANIZER_ROLE");

    struct Ticket {
        uint256 eventId;
        string ticketType;
        string seatNumber;
        uint256 eventDate;
        address organizer;
        bool isUsed;
    }

    // Resale listing information
    struct ResaleListing {
        address seller;
        uint256 price;
        bool active;
    }

    mapping(uint256 => Ticket) public tickets;

    // tokenId => resale information
    mapping(uint256 => ResaleListing) public resaleListings;

    // tokenId => list of previous/current owners
    mapping(uint256 => address[]) private ownershipHistory;

    // tokenId => timestamp for each ownership record
    mapping(uint256 => uint256[]) private ownershipTimestamps;

    uint256 private _nextTokenId;

    // --------------------------------------------------
    // EVENTS
    // --------------------------------------------------

    event TicketMinted(
        uint256 indexed tokenId,
        uint256 indexed eventId,
        address indexed organizer
    );

    event TicketTransferred(
        uint256 indexed tokenId,
        address indexed from,
        address indexed to
    );

    event TicketListedForResale(
        uint256 indexed tokenId,
        address indexed seller,
        uint256 price
    );

    event TicketResaleCancelled(
        uint256 indexed tokenId,
        address indexed seller
    );

    event TicketResold(
        uint256 indexed tokenId,
        address indexed seller,
        address indexed buyer,
        uint256 price
    );

    // --------------------------------------------------
    // PERSON 3 - TICKET VERIFICATION EVENT
    // --------------------------------------------------

    event TicketVerified(
        uint256 indexed tokenId,
        uint256 indexed eventId,
        address indexed owner
    );

    constructor() ERC721("EventTicketNFT", "ETIX") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    // --------------------------------------------------
    // ORGANIZER FUNCTIONS
    // --------------------------------------------------

    function addOrganizer(address organizer)
        public
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        _grantRole(ORGANIZER_ROLE, organizer);
    }

    function mintTicket(
        address to,
        uint256 eventId,
        string memory ticketType,
        string memory seatNumber,
        uint256 eventDate
    )
        public
        onlyRole(ORGANIZER_ROLE)
        returns (uint256)
    {
        require(
            to != address(0),
            "Cannot mint to zero address"
        );

        require(
            eventDate > block.timestamp,
            "Event date must be in the future"
        );

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

        emit TicketMinted(
            tokenId,
            eventId,
            msg.sender
        );

        return tokenId;
    }

    // --------------------------------------------------
    // TICKET DETAILS
    // --------------------------------------------------

    function getTicketDetails(uint256 tokenId)
        public
        view
        returns (Ticket memory)
    {
        _requireOwned(tokenId);

        return tickets[tokenId];
    }

    // --------------------------------------------------
    // PERSON 3 - VERIFY TICKET
    // --------------------------------------------------

    function verifyTicket(
        uint256 tokenId,
        uint256 expectedEventId
    )
        public
        onlyRole(ORGANIZER_ROLE)
        returns (
            bool valid,
            address owner,
            uint256 eventId
        )
    {
        // Check that the NFT actually exists.
        _requireOwned(tokenId);

        // Get ticket information.
        Ticket storage ticket = tickets[tokenId];

        // Check that the ticket belongs to the correct event.
        require(
            ticket.eventId == expectedEventId,
            "Ticket belongs to another event"
        );

        // Check that the ticket has not already been used.
        require(
            !ticket.isUsed,
            "Ticket already used"
        );

        // Get the current owner.
        owner = ownerOf(tokenId);

        // Mark ticket as used.
        ticket.isUsed = true;

        // Record successful entry on the blockchain.
        emit TicketVerified(
            tokenId,
            ticket.eventId,
            owner
        );

        return (
            true,
            owner,
            ticket.eventId
        );
    }

    // --------------------------------------------------
    // CHECK WHETHER TICKET IS USED
    // --------------------------------------------------

    function isTicketUsed(uint256 tokenId)
        public
        view
        returns (bool)
    {
        _requireOwned(tokenId);

        return tickets[tokenId].isUsed;
    }

    // --------------------------------------------------
    // OWNERSHIP
    // --------------------------------------------------

    // Get current owner of a ticket
    function getTicketOwner(uint256 tokenId)
        public
        view
        returns (address)
    {
        return ownerOf(tokenId);
    }

    // Get complete ownership history
    function getOwnershipHistory(uint256 tokenId)
        public
        view
        returns (address[] memory)
    {
        _requireOwned(tokenId);

        return ownershipHistory[tokenId];
    }

    function getOwnershipTimestamps(uint256 tokenId)
        public
        view
        returns (uint256[] memory)
    {
        _requireOwned(tokenId);

        return ownershipTimestamps[tokenId];
    }

    // --------------------------------------------------
    // TICKET TRANSFER
    // --------------------------------------------------

    // Transfer ticket from current owner to another user
    function transferTicket(
        address to,
        uint256 tokenId
    )
        public
    {
        require(
            ownerOf(tokenId) == msg.sender,
            "Not ticket owner"
        );

        require(
            to != address(0),
            "Invalid recipient"
        );

        // Cancel any active resale listing
        if (resaleListings[tokenId].active) {
            delete resaleListings[tokenId];
        }

        _transfer(
            msg.sender,
            to,
            tokenId
        );
    }

    // --------------------------------------------------
    // RESALE
    // --------------------------------------------------

    // Owner lists ticket for resale
    function listTicketForResale(
        uint256 tokenId,
        uint256 price
    )
        public
    {
        require(
            ownerOf(tokenId) == msg.sender,
            "Not ticket owner"
        );

        require(
            price > 0,
            "Price must be greater than zero"
        );

        Ticket memory ticket = tickets[tokenId];

        require(
            !ticket.isUsed,
            "Used ticket cannot be resold"
        );

        require(
            block.timestamp < ticket.eventDate,
            "Event has already started"
        );

        resaleListings[tokenId] = ResaleListing({
            seller: msg.sender,
            price: price,
            active: true
        });

        emit TicketListedForResale(
            tokenId,
            msg.sender,
            price
        );
    }

    // Get resale listing
    function getResaleListing(uint256 tokenId)
        public
        view
        returns (ResaleListing memory)
    {
        return resaleListings[tokenId];
    }

    // Cancel resale listing
    function cancelResale(uint256 tokenId)
        public
    {
        require(
            resaleListings[tokenId].seller == msg.sender,
            "Not the seller"
        );

        require(
            resaleListings[tokenId].active,
            "Ticket is not listed"
        );

        delete resaleListings[tokenId];

        emit TicketResaleCancelled(
            tokenId,
            msg.sender
        );
    }

    // Buy a resale ticket
    function buyResaleTicket(uint256 tokenId)
        public
        payable
    {
        ResaleListing memory listing =
            resaleListings[tokenId];

        require(
            listing.active,
            "Ticket is not for sale"
        );

        require(
            msg.sender != listing.seller,
            "Seller cannot buy own ticket"
        );

        require(
            msg.value == listing.price,
            "Incorrect payment"
        );

        Ticket memory ticket =
            tickets[tokenId];

        require(
            !ticket.isUsed,
            "Ticket already used"
        );

        require(
            block.timestamp < ticket.eventDate,
            "Event has already started"
        );

        address seller = listing.seller;

        // Remove listing BEFORE transfer/payment
        delete resaleListings[tokenId];

        // Transfer NFT to buyer
        _transfer(
            seller,
            msg.sender,
            tokenId
        );

        // Pay seller
        (bool success, ) =
            payable(seller).call{
                value: msg.value
            }("");

        require(
            success,
            "Payment failed"
        );

        emit TicketResold(
            tokenId,
            seller,
            msg.sender,
            msg.value
        );
    }

    // --------------------------------------------------
    // OWNERSHIP HISTORY TRACKING
    // --------------------------------------------------

    function _update(
        address to,
        uint256 tokenId,
        address auth
    )
        internal
        override
        returns (address)
    {
        address previousOwner =
            super._update(
                to,
                tokenId,
                auth
            );

        // Store new owner in history
        if (to != address(0)) {

            ownershipHistory[tokenId].push(to);

            ownershipTimestamps[tokenId].push(
                block.timestamp
            );

            if (previousOwner != address(0)) {

                emit TicketTransferred(
                    tokenId,
                    previousOwner,
                    to
                );
            }
        }

        return previousOwner;
    }

    // --------------------------------------------------
    // INTERFACE SUPPORT
    // --------------------------------------------------

    function supportsInterface(
        bytes4 interfaceId
    )
        public
        view
        override(ERC721, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}