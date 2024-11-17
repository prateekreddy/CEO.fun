
import os
import re
import json
from typing import List, Tuple, Dict
import requests
from web3 import Web3
from ens import ENS
from eth_keys import keys
import secrets
import hashlib
from engines.prompts.prompts import get_wallet_decision_prompt
from sqlalchemy.orm import Session
from models import User
from engines.wallet.find_teleport import TeleportManager

class WalletManager:

    rpc_dict = {
        "sepolia": "wss://ethereum-sepolia-rpc.publicnode.com",
        "polygon-amoy": "https://polygon-amoy.drpc.org",
        "arb-sepolia": "https://endpoints.omniatech.io/v1/arbitrum/sepolia/public",
        "gnosis-chiado": "https://gnosis-chiado-rpc.publicnode.com",
        "unichain-sepolia": "https://sepolia.unichain.org",
        "base-sepolia": "https://sepolia.base.org"
    }

    def __init__(self):
        pass

    def get_wallet_balance(self, private_key, eth_mainnet_rpc_url):
        w3 = Web3(Web3.HTTPProvider(eth_mainnet_rpc_url))
        public_address = w3.eth.account.from_key(private_key).address

        # Retrieve and print the balance of the account in Ether
        balance_wei = w3.eth.get_balance(public_address)
        balance_ether = w3.from_wei(balance_wei, 'ether')

        return balance_ether


    def transfer_eth(self, private_key, eth_mainnet_rpc_url, to_address, amount_in_ether):
        """
        Transfers Ethereum from one account to another.

        Parameters:
        - private_key (str): The private key of the sender's Ethereum account in hex format.
        - to_address (str): The Ethereum address or ENS name of the recipient.
        - amount_in_ether (float): The amount of Ether to send.

        Returns:
        - str: The transaction hash as a hex string if the transaction was successful.
        - str: "Transaction failed" or an error message if the transaction was not successful or an error occurred.
        """
        try:
            w3 = Web3(Web3.HTTPProvider(eth_mainnet_rpc_url))
            print("starting tx")
            # Check if connected to blockchain
            if not w3.is_connected():
                print("Failed to connect to ETH Mainnet")
                return "Connection failed"

            # Set up ENS
            # w3.ens = ENS.fromWeb3(w3)

            print("about to resolve")
            # # Resolve ENS name to Ethereum address if necessary
            # if Web3.is_address(to_address):
            #     # The to_address is a valid Ethereum address
            #     resolved_address = Web3.to_checksum_address(to_address)
            #     print(resolved_address)
            # else:
            #     # Try to resolve as ENS name
            #     resolved_address = w3.ens.address(to_address)
            #     if resolved_address is None:
            #         return f"Could not resolve ENS name: {to_address}"

            print(f"Transferring to {to_address}")

            # Convert the amount in Ether to Wei
            amount_in_wei = w3.to_wei(amount_in_ether, 'ether')

            # Get the public address from the private key
            account = w3.eth.account.from_key(private_key)
            public_address = account.address

            # Get the nonce for the transaction
            nonce = w3.eth.get_transaction_count(public_address)

            # Build the transaction
            transaction = {
                'to': to_address,
                'value': amount_in_wei,
                'gas': 21000,
                'gasPrice': int(w3.eth.gas_price * 1.1),
                'nonce': nonce,
                'chainId': 15107  # Mainnet chain ID
            }

            # Sign the transaction
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

            # Send the transaction
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

            # Wait for the transaction receipt
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            # Check the status of the transaction
            if tx_receipt['status'] == 1:
                return tx_hash.hex()
            else:
                return "Transaction failed"
        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error occurred: {e}"

    def wallet_address_in_post(self, posts, teleport_users_string, private_key, eth_mainnet_rpc_url: str,llm_api_key: str):
        """
        Detects wallet addresses or ENS domains from a list of posts.
        Converts all items to strings first, then checks for matches.

        Parameters:
        - posts (List): List of posts of any type

        Returns:
        - List[Dict]: List of dicts with 'address' and 'amount' keys
        """

        # Convert everything to strings first
        str_posts = [str(post) for post in posts]

        # Then look for matches in all the strings
        eth_pattern = re.compile(r'\b0x[a-fA-F0-9]{40}\b|\b\S+\.eth\b')
        matches = []

        for post in str_posts:
            found_matches = eth_pattern.findall(post)
            matches.extend(found_matches)

        wallet_balance = self.get_wallet_balance(private_key, eth_mainnet_rpc_url)
        prompt = get_wallet_decision_prompt(posts, teleport_users_string, matches, wallet_balance)

        response = requests.post(
            url="https://api.hyperbolic.xyz/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {llm_api_key}",
            },
            json={
                "messages": [
                    {
                        "role": "system",
            	        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": "Respond only with the wallet address(es) and amount(s) you would like to send to."
                    }
                ],
                "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
                "presence_penalty": 0,
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
            }
        )

        if response.status_code == 200:
            print(f"ETH Addresses and amounts chosen from Posts: {response.json()}")
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Error generating short-term memory: {response.text}")

    def find_user_list(self, notif_context: List[str]) -> List[str]:
        """Find the list of users from the notification context."""
        user_names = []
        for context in notif_context:
            user_match = re.search(r'@(\w+)', context)
            if user_match:
                user_names.append(user_match.group(1))
        return user_names

    def _handle_wallet_transactions(self, db: Session, notif_context: List[str], config) -> None:
        """Process and execute wallet transactions if conditions are met."""
        user_names = self.find_user_list(notif_context)
        # for each user in user_names, filter users with teleport=True
        teleport_users_raw = db.query(User).filter(User.username.in_(user_names), User.teleport == False).all()
        # create dictionary with username and teleport status
        teleport_user_scores = {user.username: TeleportManager.get_follower_score(user.username, "0c6a2742-8b82-4497-b28e-35764c9b356f") for user in teleport_users_raw}

        balance_ether = self.get_wallet_balance(
            config.private_key_hex,
            config.eth_mainnet_rpc_url
        )
        print(f"Agent wallet balance is {balance_ether} ETH now.\n")
        if balance_ether <= config.min_eth_balance:
            return
        for _ in range(2):  # Max 2 attempts
            try:
                wallet_data = self.wallet_address_in_post(
                    notif_context,
                    json.dumps(teleport_user_scores),
                    config.private_key_hex,
                    config.eth_mainnet_rpc_url,
                    config.llm_api_key
                )
                print(wallet_data)
                wallets = json.loads(wallet_data)
                print(wallets)
                if not wallets:
                    print("No wallet addresses or amounts to send ETH to.")
                    break
                for wallet in wallets:
                    print(f"Sent {wallet['amount']} ETH to {wallet['address']}")
                    tx = self.transfer_eth(
                        config.private_key_hex,
                        config.eth_mainnet_rpc_url,
                        wallet["address"],
                        wallet["amount"]
                    )
                    print(f"Sent {wallet['amount']} ETH to {wallet['address']}")
                break
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing wallet data: {e}")
                continue
    
    def generate_eth_account(self) -> Tuple[str, str]:
        """Generate a new Ethereum account with private key and address."""
        random_seed = secrets.token_bytes(32)
        hashed_output = hashlib.sha256(random_seed).digest()
        private_key = keys.PrivateKey(hashed_output)
        private_key_hex = private_key.to_hex()
        eth_address = private_key.public_key.to_checksum_address()
        return private_key_hex, eth_address
    
    def get_wallet_information(self) -> Tuple[str, str]:
        """Retrieve wallet information from environment variables."""
        private_key_hex = os.getenv("AGENT_WALLET_PRIVATE_KEY")
        eth_address = os.getenv("AGENT_WALLET_ADDRESS")
        return private_key_hex, eth_address
