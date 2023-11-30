from abc import ABC, abstractmethod


class AbstractConversations(ABC):
    @abstractmethod
    def build_message(self, history_messages):
        return NotImplementedError()


class Conversations(AbstractConversations):
    def build_message(self, history_messages):
        print("test")
