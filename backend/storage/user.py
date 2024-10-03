from chat.conversation import Conversation


class User:
    user_id: str
    history: Conversation

    def __init__(self, user_id: str, history: Conversation):
        self.user_id = user_id
        self.history = history
