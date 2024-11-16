from web3 import Web3
import requests
import json
from sqlalchemy.orm import Session

class TeleportManager:
    def __init__(self, teleport_address, rpc_url):
        self.teleport_address = teleport_address
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.teleport_abi = '[{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_symbol","type":"string"},{"internalType":"address","name":"initialOwner","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"name":"ERC721IncorrectOwner","type":"error"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ERC721InsufficientApproval","type":"error"},{"inputs":[{"internalType":"address","name":"approver","type":"address"}],"name":"ERC721InvalidApprover","type":"error"},{"inputs":[{"internalType":"address","name":"operator","type":"address"}],"name":"ERC721InvalidOperator","type":"error"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"ERC721InvalidOwner","type":"error"},{"inputs":[{"internalType":"address","name":"receiver","type":"address"}],"name":"ERC721InvalidReceiver","type":"error"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"ERC721InvalidSender","type":"error"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ERC721NonexistentToken","type":"error"},{"inputs":[],"name":"NonExistentTokenURI","type":"error"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"OwnableInvalidOwner","type":"error"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"OwnableUnauthorizedAccount","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"x_id","type":"uint256"},{"indexed":false,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"string","name":"policy","type":"string"},{"indexed":false,"internalType":"string","name":"name","type":"string"},{"indexed":false,"internalType":"string","name":"username","type":"string"},{"indexed":false,"internalType":"string","name":"pfp","type":"string"}],"name":"NewTokenData","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"x_id","type":"uint256"},{"indexed":false,"internalType":"string","name":"policy","type":"string"},{"indexed":false,"internalType":"string","name":"tweetId","type":"string"}],"name":"RedeemLike","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"x_id","type":"uint256"},{"indexed":false,"internalType":"address","name":"addr","type":"address"},{"indexed":false,"internalType":"string","name":"policy","type":"string"},{"indexed":false,"internalType":"string","name":"content","type":"string"}],"name":"RedeemTweet","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"minter","type":"address"}],"name":"RemoveMinter","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"minter","type":"address"}],"name":"WhitelistMinter","type":"event"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"currentTokenId","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"isWhitelisted","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"x_id","type":"uint256"},{"internalType":"string","name":"policy","type":"string"},{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"username","type":"string"},{"internalType":"string","name":"pfp","type":"string"},{"internalType":"bytes32","name":"nftIdHash","type":"bytes32"}],"name":"mintTo","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"nftIdMap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"string","name":"content","type":"string"},{"internalType":"enum NFT.TokenType","name":"tokenType","type":"uint8"}],"name":"redeem","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"minter","type":"address"}],"name":"removeMinter","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"minter","type":"address"}],"name":"whitelistMinter","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
        self.contract_instance = self.w3.eth.contract(address=self.teleport_address, abi=self.teleport_abi)

    def find_teleport_user(self, teleport_id) -> str:
        """Find the user who minted the teleport"""

        try:
            token_uri = self.contract_instance.functions.tokenURI(teleport_id).call()
            metadata = self.parse_token_metadata(token_uri)
            
            for attribute in metadata['attributes']:
                if attribute['trait_type'] == 'X Username':
                    return attribute['value']
            return None
        except Exception as e:
            print(f"Failed to find teleport: {str(e)}")
            return None

    def parse_token_metadata(self, token_uri):
        """Parse the token URI to extract the user"""
        prefix = "data:application/json;base64,"
        if not token_uri.startswith(prefix):
            print("Invalid token URI")
            return None
        else:
            token_uri = token_uri[len(prefix):]

        # Parse JSON
        data = json.loads(token_uri)

        return data
    
    def get_follower_score(self, username: str, api_key: str = "0c6a2742-8b82-4497-b28e-35764c9b356f") -> int:
        """
        Fetch the follower score for a given Twitter username.
        
        Args:
            username (str): Twitter username to lookup
            api_key (str): API key for authentication
            
        Returns:
            int: The follower score
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the follower score cannot be extracted from the response
        """
        headers = {
            "accept": "application/json",
            "Api-Key": api_key
        }
        
        url = f"https://api.discover.getmoni.io/api/v1/twitters/{username}/info/"
        
        response = requests.get(url, headers=headers)
        
        if not response.ok:
            raise requests.RequestException(f"API request failed with status: {response.status_code}")
        
        data = response.json()
        follower_score = data.get("followersScore")
        
        if follower_score is None:
            raise ValueError("Failed to extract follower score from response")
            
        return int(follower_score)
    
    def query_events(self, db: Session, from_block: int, agent_address) -> int:
        to_block = self.get_last_block()
        
        if from_block >= to_block:
            return from_block

        events = self.contract_instance.events.NewTokenData().get_logs(
            argument_filters={"to": agent_address},
            from_block=from_block,
            to_block=to_block
        )

        for event in events:
            teleport_id = event["args"]["tokenId"]
            user = self.find_teleport_user(teleport_id)
            print(f"Found teleport user: {user}")
            # set teleport flag on address to true if it already exists otherwise create and set to true
            db.execute(f"INSERT INTO teleport (username, teleport) VALUES ({user}, true) ON CONFLICT (address) DO UPDATE SET teleport = true")
            # TODO NOW: Tweet about the teleport

        db.commit()
        
        return to_block+1

    def get_last_block(self):
        return self.w3.eth.get_block("latest").number