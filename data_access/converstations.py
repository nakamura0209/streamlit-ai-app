from abc import ABC, abstractmethod


class AbstractConversations(ABC):
    @abstractmethod
    def build_message(self, history_messages):
        return NotImplementedError()


class AIMessage:
    def __init__(self, content):
        self.content = content


class HumanMessage:
    def __init__(self, content):
        self.content = content


class SystemMessage:
    def __init__(self, content):
        self.content = content
