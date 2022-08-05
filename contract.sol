// SPDX-License-Identifier: MIT
pragma solidity ^0.8.14;


import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";


/*                                                                                                   
          赤塾の                    赤塾の                    赤塾の                    赤塾の                    赤塾の                    赤塾の                    赤塾の                    赤塾の          
         /\    \                  /\    \                  /\    \                  /\    \                  /\    \                  /\    \                  /\    \                  /\    \         
        /::\    \                /::\____\                /::\    \                /::\    \                /::\____\                /::\____\                /::\____\                /::\    \        
       /::::\    \              /:::/    /               /::::\    \               \:::\    \              /:::/    /               /:::/    /               /:::/    /               /::::\    \       
      /::::::\    \            /:::/    /               /::::::\    \               \:::\    \            /:::/    /               /:::/    /               /:::/    /               /::::::\    \      
     /:::/\:::\    \          /:::/    /               /:::/\:::\    \               \:::\    \          /:::/    /               /:::/    /               /:::/    /               /:::/\:::\    \     
    /:::/__\:::\    \        /:::/____/               /:::/__\:::\    \               \:::\    \        /:::/    /               /:::/____/               /:::/    /               /:::/__\:::\    \    
   /::::\   \:::\    \      /::::\    \              /::::\   \:::\    \              /::::\    \      /:::/    /               /::::\    \              /:::/    /                \:::\   \:::\    \   
  /::::::\   \:::\    \    /::::::\____\________    /::::::\   \:::\    \    _____   /::::::\    \    /:::/    /      _____    /::::::\____\________    /:::/    /      _____    ___\:::\   \:::\    \  
 /:::/\:::\   \:::\    \  /:::/\:::::::::::\    \  /:::/\:::\   \:::\    \  /\    \ /:::/\:::\    \  /:::/____/      /\    \  /:::/\:::::::::::\    \  /:::/____/      /\    \  /\   \:::\   \:::\    \ 
/:::/  \:::\   \:::\____\/:::/  |:::::::::::\____\/:::/  \:::\   \:::\____\/::\    /:::/  \:::\____\|:::|    /      /::\____\/:::/  |:::::::::::\____\|:::|    /      /::\____\/::\   \:::\   \:::\____\
\::/    \:::\  /:::/    /\::/   |::|~~~|~~~~~     \::/    \:::\  /:::/    /\:::\  /:::/    \::/    /|:::|____\     /:::/    /\::/   |::|~~~|~~~~~     |:::|____\     /:::/    /\:::\   \:::\   \::/    /
 \/____/ \:::\/:::/    /  \/____|::|   |           \/____/ \:::\/:::/    /  \:::\/:::/    / \/____/  \:::\    \   /:::/    /  \/____|::|   |           \:::\    \   /:::/    /  \:::\   \:::\   \/____/ 
          \::::::/    /         |::|   |                    \::::::/    /    \::::::/    /            \:::\    \ /:::/    /         |::|   |            \:::\    \ /:::/    /    \:::\   \:::\    \     
           \::::/    /          |::|   |                     \::::/    /      \::::/    /              \:::\    /:::/    /          |::|   |             \:::\    /:::/    /      \:::\   \:::\____\    
           /:::/    /           |::|   |                     /:::/    /        \::/    /                \:::\__/:::/    /           |::|   |              \:::\__/:::/    /        \:::\  /:::/    /    
          /:::/    /            |::|   |                    /:::/    /          \/____/                  \::::::::/    /            |::|   |               \::::::::/    /          \:::\/:::/    /     
         /:::/    /             |::|   |                   /:::/    /                                     \::::::/    /             |::|   |                \::::::/    /            \::::::/    /      
        /:::/    /              \::|   |                  /:::/    /                                       \::::/    /              \::|   |                 \::::/    /              \::::/    /       
        \::/    /                \:|   |                  \::/    /                                         \::/____/                \:|   |                  \::/____/                \::/    /        
         \/____/                  \|___|                   \/____/                                           ~~                       \|___|                   ~~                       \/____/         
*/



contract akajukus is ERC721Enumerable, ReentrancyGuard, Ownable, ERC2981 {
    using Strings for uint256;
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    string public _cid;
    string public _nonRevealedURI = "" //  e.g.  "https://smolr.mypinata.cloud/ipfs/QmRvRFUsEhgc45";
    mapping(address => bool) public _owners;
    string public extension = ".json"; // 
    bool public revealed = false;
    bool public mintOpen = false;

    uint256 public maxSupply = 0;
    uint256 public price = 0 ether;

    uint96 public tokenRoyalties = 750;  // = denominator is 10_000, so 750 / 10_000 is 7.5%
    address public royaltyPayout = some_address; 

    ///////// WL /////////
    uint256 public _maxWL_Mintable = 500; 
    mapping(address => bool) public whiteListed;
    bool public isWL = true;


    constructor() ERC721("AKAJUKUS", "AKA") {
        internalMint(i); 
        internalMint(nostri); 
        internalMint(wallets);
        _setDefaultRoyalty(royaltyPayout, tokenRoyalties);
    }

    // MODIFIERS

    modifier callerIsUser() {
        require(tx.origin == msg.sender, "The caller is another contract");
        _;
    }

    // URI

    function setBaseURI(string memory _uri) external onlyOwner {
        _cid = _uri;
    }

    function _baseURI() internal view virtual override returns (string memory) {
        return _cid;
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721)
        returns (string memory)
    {
        require(_exists(tokenId), "Token does not exist");

        if (revealed == false) {
            return _nonRevealedURI;
        }

        string memory baseURI = _baseURI();
        return
            bytes(baseURI).length > 0
                ? string(
                    abi.encodePacked(baseURI, tokenId.toString(), extension)
                )
                : "";
    }

    function setExtension(string memory _extension) external onlyOwner {
        extension = _extension;
    }

    function setNotRevealedURI(string memory _uri) external onlyOwner {
        _nonRevealedURI = _uri;
    }

    function reveal() external onlyOwner {
        revealed = true;
    }
    
    // OPEN MINT

    function openSale() external onlyOwner {
        mintOpen = true;
    }

    function closeSale() external onlyOwner {
        mintOpen = false;
    }

    // WITHDRAW

    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "Nothing to withdraw");

        require(payable(msg.sender).send(address(this).balance));
    }

    // MINT

    function mint(uint256 count) external callerIsUser nonReentrant {
        require(!_owners[msg.sender], "This address already minted");
        require(mintOpen, "Mint is not active");
        require(count <= 2, "Only 2 allowed");
        require(totalSupply() <= maxSupply, "All Cupid Eggs have been minted");

         if (isWL) {
            require(
                whiteListed[msg.sender] == true,
                "Your wallet is not a white listed."
            );
            require(count == 1, "Only 1 allowed");
        }

        for (uint256 i = 0; i < count; i++) {
            internalMint(msg.sender);
        }
        
        _owners[msg.sender] = true;
    }

    function internalMint(address _addr) internal {
        _tokenIds.increment();
        uint256 newItemId = _tokenIds.current();

        if (isWL) {
            require(
                newItemId <= _maxWL_Mintable,
                "WL mint is finished or mint amount is over the limit"
            );
        }

        _safeMint(_addr, newItemId);
    }

    // ROYALTIES

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721Enumerable, ERC2981)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function setTokenRoyalties(uint96 _royalties) external onlyOwner {
        tokenRoyalties = _royalties;
        _setDefaultRoyalty(royaltyPayout, tokenRoyalties);
    }

    function setRoyaltyPayoutAddress(address _payoutAddress)
        external
        onlyOwner
    {
        royaltyPayout = _payoutAddress;
        _setDefaultRoyalty(royaltyPayout, tokenRoyalties);
    }



    /////////// for WL
    function setWLStatus() external onlyOwner {
        isWL = !isWL;
    }

    function updateWLSupply(uint256 supply) public onlyOwner {
        _maxWL_Mintable = supply;
    }

    function addWhiteList(address[] memory _addressList) external onlyOwner {
        require(_addressList.length > 0, "Error: list is empty");

        for (uint256 i = 0; i < _addressList.length; i++) {
            require(_addressList[i] != address(0), "Address cannot be 0.");
            whiteListed[_addressList[i]] = true;
        }
    }

    function removeWhiteList(address[] memory addressList) external onlyOwner {
        require(addressList.length > 0, "Error: list is empty");
        for (uint256 i = 0; i < addressList.length; i++)
            whiteListed[addressList[i]] = false;
    }
}
