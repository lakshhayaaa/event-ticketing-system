export const CONTRACT_ABI = [
  "function getEventDetails(uint256 eventId) view returns (tuple(uint256 eventId,string name,string venue,uint256 eventDate,uint256 ticketPrice,uint256 totalTickets,uint256 ticketsSold,bool active))",
  "function getTicketsRemaining(uint256 eventId) view returns (uint256)",
  "function getEventRevenue(uint256 eventId) view returns (uint256)",

  "function getTicketDetails(uint256 tokenId) view returns (tuple(uint256 eventId,string ticketType,string seatNumber,uint256 eventDate,address organizer,bool isUsed))",
  "function getTicketOwner(uint256 tokenId) view returns (address)",
  "function getOwnershipHistory(uint256 tokenId) view returns (address[])",
  "function getOwnershipTimestamps(uint256 tokenId) view returns (uint256[])",
  "function isTicketUsed(uint256 tokenId) view returns (bool)",

  "function transferTicket(address to,uint256 tokenId)",

  "function listTicketForResale(uint256 tokenId,uint256 price)",
  "function getResaleListing(uint256 tokenId) view returns (tuple(address seller,uint256 price,bool active))",
  "function cancelResale(uint256 tokenId)",
  "function buyResaleTicket(uint256 tokenId) payable",

  "function createEvent(string name,string venue,uint256 eventDate,uint256 ticketPrice,uint256 totalTickets) returns (uint256)",
  "function mintTicket(address to,uint256 eventId,string ticketType,string seatNumber,uint256 eventDate) returns (uint256)",
  "function verifyTicket(uint256 tokenId,uint256 expectedEventId) returns (bool valid,address owner,uint256 eventId)"
];