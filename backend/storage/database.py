import sqlalchemy as alchemy
from sqlalchemy import Engine, MetaData, Table, Column, String, ForeignKey, DateTime, \
    func, JSON, desc, Boolean, select
from sqlalchemy.orm import sessionmaker

from chat.conversation import Conversation
from chat.messages import ColdMessage

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', String(36), primary_key=True),
    Column('name', String, nullable=True),
    Column('preferred_username', String, nullable=True),
    Column('given_name', String, nullable=True),
    Column('family_name', String, nullable=True),
    Column('email', String, nullable=True),
    Column('temp', Boolean, default=False),
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
    Column('type', String(32), primary_key=True),
    Column('tool', String(32), primary_key=True),
    Column('frontend_messages', JSON, nullable=False),
    Column('openai_messages', JSON, nullable=False),
    Column('created', DateTime, default=func.now()),
)


class DatabaseEngine:
    engine: Engine

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.sessions = sessionmaker(engine)

        metadata.create_all(self.engine)

    def user_exists(self, user_id: str):
        with self.sessions.begin() as session:
            query = (users.select()
                     .where(users.c.id == user_id)
                     .where(users.c.temp == False))

            result = session.execute(query, {"user_id": user_id}).fetchall()

            return len(result) == 1

    def temp_user_exists(self, user_id: str):
        with self.sessions.begin() as session:
            query = (users.select()
                     .where(users.c.id == user_id)
                     .where(users.c.temp)
                     .limit(1))

            result = session.execute(query, {"user_id": user_id}).fetchall()

            return len(result) == 1

    def get_user(self, user_id: str):
        with self.sessions.begin() as session:
            query = (users.select()
                     .where(users.c.id == user_id)
                     .where(users.c.temp == False)
                     .limit(1))

            result = session.execute(query, {"user_id": user_id})

            return result.fetchall()

    def insert_user(self, data: dict):
        with self.sessions.begin() as session:
            session.execute(users.insert().values(data))
            return self.user_exists(data['id'])

    def write_message_to_storage(self, cold_message: ColdMessage, conversation_id: str):
        new_message = {
            "id": cold_message.read("message_id"),
            "conversation_id": conversation_id,
            "type": cold_message.read("type"),
            "tool": cold_message.read("tool_name"),
            "frontend_messages": cold_message.read("frontend_messages"),
            "openai_messages": cold_message.read("openai_messages")
        }

        with self.sessions.begin() as session:
            session.execute(messages.insert().values(new_message))

    def get_conversation_history(self, conversation_id: str) -> Conversation:
        cold_messages = []
        with self.sessions.begin() as session:
            query = (messages.select()
                     .where(messages.c.conversation_id == conversation_id))

            result = session.execute(query)
            conversation_messages = result.fetchall()

            for message in conversation_messages:
                message_dict = message._asdict()
                cold_messages.append(ColdMessage(
                    id=message_dict["id"],
                    type=message_dict["type"],
                    tool_name=message_dict["tool"],
                    openai_messages=message_dict["openai_messages"],
                    frontend_messages=message_dict["frontend_messages"]
                ))

            conversation = Conversation(
                history=cold_messages,
                recorder=self.write_message_to_storage,
                conversation_id=conversation_id
            )

            return conversation

    def stream_conversation_for_frontend(self, conversation_id: str) -> list[dict[str, str]]:
        with self.sessions.begin() as session:
            query = (select(messages.c.frontend_messages)
                     .where(messages.c.conversation_id == str(conversation_id)))

            for message in session.execute(query).yield_per(10):
                yield message[0]

    def conversation_history_exists(self, conversation_id: str):
        with self.sessions.begin() as session:
            query = (conversations.select()
                     .where(conversations.c.id == conversation_id)
                     .limit(1))

            result = session.execute(query).fetchall()

            return len(result) == 1

    def create_conversation_history(self, conversation_id: str, user_id: str, title: str):
        new_conversation = {
            'id': conversation_id,
            'user_id': user_id,
            'title': title
        }

        with self.sessions.begin() as session:
            session.execute(conversations.insert().values(new_conversation))

    def get_or_create_conversation(self, conversation_id: str, user_id: str) -> Conversation:
        if not self.conversation_history_exists(conversation_id):
            self.create_conversation_history(conversation_id, user_id, "New Chat")
        return self.get_conversation_history(conversation_id)

    def get_user_conversations(self, user_id: str) -> list[dict[str, str]]:
        with self.sessions.begin() as session:
            query = (alchemy.select(conversations.c.id, conversations.c.title)
                     .where(conversations.c.user_id == user_id)
                     .order_by(desc(conversations.c.created)))

            result = session.execute(query)

            ids = [{"id": row[0], "title": row[1]} for row in result.fetchall()]
            return ids
