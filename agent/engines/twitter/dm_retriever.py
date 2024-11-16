import os
from typing import List, Dict
from twitter.account import Account
from sqlalchemy.orm import Session
from models import Message
import requests
from engines.twitter.utils import user_id_by_usernames
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class DMRetreiver:
    def __init__(self):
        pass

    def retrieve_last_parsed_time(self, db: Session) -> int:
        """Fetch the last parsed time for the user from DB"""
        last_parsed_time = db.query(Message).order_by(Message.created_at.desc()).first()
        return last_parsed_time.created_at if last_parsed_time else 0

    def fetch_latest_dms(self, db: Session, account: Account) -> List[Dict]:
        """Fetch DMs for the user after latest message"""
        return self.fetch_dms_from(account, self.retrieve_last_parsed_time(db))

    def fetch_dms_from(self, account: Account, from_ms: int) -> List[Dict]:
        """Get latest DMs"""
        inbox = account.dm_inbox()

        messages = []
        if inbox['inbox_initial_state'] and inbox['inbox_initial_state']['entries']:
            messages = self.parse_dm_data(inbox['inbox_initial_state']['entries'], from_ms, user_id_by_usernames(account, [os.getenv("X_USERNAME")]))
        return messages

    def parse_dm_data(self, inbox_entries, from_ms: int, account_id):
        # TODO: Implement pagination, can't find any info on how to do this in the Twitter API repo
        """Parse DM data"""
        messages = []
        print (inbox_entries, account_id)

        for dm in inbox_entries:
            if 'message' in dm and 'message_data' in dm['message'] and 'time' in dm['message']['message_data'] and int(dm['message']['message_data']['time']) > from_ms:
                user = dm['message']['message_data']['sender_id']
                if user == account_id:
                    user = dm['message']['message_data']['recipient_id']
                msg = dm['message']
                msg_data = msg['message_data']
                message = Message(
                    id=msg_data['id'],
                    conversation_id=msg['conversation_id'],
                    user_id=user,
                    text=msg_data['text'],
                    # python datetime is in seconds, twitter is in ms
                    created_at=datetime.fromtimestamp(
                        int(msg_data['time']) / 1000
                    ).strftime('%Y-%m-%d %H:%M:%S')
                )
                messages.append(message)
        return messages

    def store_processed_messages(self, db: Session, messages: List[Dict]):
        """Store the processed messages in DB"""
        try:
            db.add_all(messages)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error storing messages: {e}")

    def retrieve_messages_by_users(self, db: Session, user_ids: List) -> Dict:
        """Retrieve DM messages for the users from DB"""
        messages = db.query(Message).filter(Message.user_id.in_(user_ids)).all()
        return {user_id: [self.message_to_dict(message) for message in messages] for user_id in user_ids}

    def retrieve_messages_by_user(self, db: Session, user_id: int) -> List[Dict]:
        """Retrieve DM messages for the user from DB"""
        messages = db.query(Message).filter(Message.user_id == user_id).all()
        return [self.message_to_dict(message) for message in messages]
    
    def message_to_dict(self, message: Message) -> Dict:
        """Convert a Message object to a dictionary"""
        return {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "user_id": message.user_id,
            "text": message.text,
            "created_at": message.created_at
        }

    def create_teleport_check_prompt(self, messages: List[Dict]):
        """Creates a prompt to check if user provided teleport NFT"""

        prompt = f"""
        Analyze the following recent direct messages: 

        Direct Messages:
        {messages}

        Based on this information, decide if there was a teleport NFT id.

        Remember that this is a crutial information and teleport NFT id will be a number.

        You should carefully evaluate these decisions for your own future and survival.

        If you found a teleport NFT id, you must return ONLY a JSON object with the 'teleport_nft_id' key and the value of the teleport NFT id.

        If you did not find a teleport NFT id, you must return ONLY a JSON object with an empty string as the value.

        If multiple teleport NFT ids were found, return the first one found.

        Only return the correctly formatted JSON object in any case. Do not give any other information.

        Example Response if atleast one teleport NFT id was found:

        {{
            "teleport_nft_id": 123456789
        }}

        Example Response if no teleport NFT id was found:    

        {{}}
        """
        return prompt.format(
            messages=messages
        )

    def decide_teleport_availability(self, messages: List[Dict], openrouter_api_key: str):
        """Decides if teleport NFT id is available"""
        # TODO: Verify if this is correct

        prompt = self.create_teleport_check_prompt(messages)

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
            },
            json={
                "model": "meta-llama/llama-3.1-70b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            },
        )   

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Error generating decision: {response.text}")