from uuid import uuid4

import sqlalchemy as alchemy
from sqlalchemy import Engine, MetaData, Table, Column, String, ForeignKey, DateTime, \
    func, JSON, insert, text, desc

from chat.conversation import Conversation
from chat.messages import ColdMessage
from chat.tools.gen_conversation_title import _ask_llm_to_generate_title
from nlp.ai import AI

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', String(36), primary_key=True),
    Column('name', String, nullable=False),
    Column('preferred_username', String, nullable=False),
    Column('given_name', String, nullable=False),
    Column('family_name', String, nullable=False),
    Column('email', String, nullable=False),
    Column('created', DateTime, default=func.now()),
)

conversations = Table(
    'conversations', metadata,
    Column('id', String(36), primary_key=True),
    Column('user_id', String(36), ForeignKey('users.id'), nullable=False),
    Column('created', DateTime, default=func.now()),
    Column('title', String(36), nullable=False)
)

messages = Table(
    'messages', metadata,
    Column('id', String(36), primary_key=True),
    Column('conversation_id', String(36), ForeignKey('conversations.id'), nullable=False),
    Column('type', String, nullable=False),
    Column('value', JSON, nullable=False),
    Column('created', DateTime, default=func.now()),
    Column('tool', String, nullable=False),
    Column('role_and_content', JSON, nullable=False),
)


class DatabaseEngine:
    engine: Engine

    def __init__(self, engine) -> None:
        self.engine = engine
        # metadata.drop_all(self.engine)
        metadata.create_all(self.engine)

    def user_exists(self, user_id: str):
        with self.engine.connect() as conn:
            query = text("""
                        SELECT 1
                        FROM users
                        WHERE id = :user_id
                        LIMIT 1;
                    """)
            result = conn.execute(query, {"user_id": user_id}).fetchall()

            if len(result) == 1:
                return True
            return False

    def get_user(self, user_id: str):
        with self.engine.connect() as conn:
            query = text("""
                        SELECT *
                        FROM users
                        WHERE user_id = :user_id;
                    """)
            result = conn.execute(query, {"user_id": user_id})

            return result.fetchall()

    def insert_user(self, user):
        new_user = {
            "id": user['id'],
            "name": user['name'],
            "preferred_username": user['preferred_username'],
            "given_name": user['given_name'],
            "family_name": user['family_name'],
            "email": user['email']
        }

        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                result = conn.execute(insert(users).values(new_user))
                trans.commit()
            except Exception as e:
                trans.rollback()
                print("Error inserting user:", e)

        return self.user_exists(user['id'])

    def write_message_to_storage(self, cold_message: ColdMessage, conversation_id: str):
        cold_message_dict = cold_message.read_all()
        new_message = {
            "id": str(uuid4()),
            "conversation_id": conversation_id,
            "type": cold_message_dict['type'],
            "value": cold_message_dict['type_and_value']['value'],
            "tool": cold_message_dict['tool_name'],
            "role_and_content": cold_message_dict['role_and_content']
        }

        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                result = conn.execute(insert(messages).values(new_message))
                trans.commit()
            except Exception as e:
                trans.rollback()
                print("Error inserting message:", e)

    def get_conversation_history(self, conversation_id: str) -> Conversation:
        cold_messages = []
        with self.engine.connect() as conn:
            query = messages.select().where(messages.c.conversation_id == conversation_id)
            result = conn.execute(query)
            conversation_messages = result.fetchall()

            for message in conversation_messages:
                message_dict = dict(message._mapping)
                cold_messages.append(ColdMessage(
                    type=message_dict['type'],
                    tool_name=message_dict['tool'],
                    show_user="",
                    role_and_content=message_dict['role_and_content'],
                    type_and_value={
                        'type': message_dict['type'],
                        'value': message_dict['value']
                    }
                ))
        history = Conversation(
            history=cold_messages,
            recorder=self.write_message_to_storage,
            conversation_id=conversation_id
        )
        return history

    def get_conversation_messages(self, conversation_id: str) -> Conversation:
        with self.engine.connect() as conn:
            query = messages.select().where(messages.c.conversation_id == str(conversation_id))
            result = conn.execute(query)
            conversation_messages = result.fetchall()
            simplified_messages = [
                {
                    'type': message._mapping['type'],
                    'value': message._mapping['value']
                }
                for message in conversation_messages
            ]

        return simplified_messages

    def conversation_history_exists(self, conversation_id: str):
        with self.engine.connect() as conn:
            query = text("""
                        SELECT 1
                        FROM conversations
                        WHERE id = :conversation_id
                        LIMIT 1;
                    """)
            result = conn.execute(query, {"conversation_id": conversation_id}).fetchall()

            if len(result) == 1:
                return True
            return False

    def create_conversation_history(self, conversation_id: str, user_id: str, title: str):
        new_conversation = {
            'id': conversation_id,
            'user_id': user_id,
            'title': title
        }

        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                result = conn.execute(insert(conversations).values(new_conversation))
                trans.commit()
            except Exception as e:
                trans.rollback()
                print("Error inserting conversation:", e)

    def get_or_create_conversation(self, conversation_id: str, user_id: str, ai: AI,
                                   user_message: str = None, ) -> Conversation:
        if not self.conversation_history_exists(conversation_id):
            title = _ask_llm_to_generate_title(ai=ai, request=user_message)

            self.create_conversation_history(conversation_id, user_id, title)
        return self.get_conversation_history(conversation_id)

    def get_user_conversations(self, user_id: str) -> list[str]:
        with self.engine.connect() as conn:
            query = alchemy.select(conversations.c.id, conversations.c.title).where(
                conversations.c.user_id == user_id).order_by(desc(conversations.c.created))
            result = conn.execute(query)

            ids = [{"id": row[0], "title": row[1]} for row in result.fetchall()]
        return ids
