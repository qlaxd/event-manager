from abc import ABC, abstractmethod


class ChatbotClient(ABC):
    @abstractmethod
    async def get_response(self, message: str, session_id: str) -> dict:
        pass

    @abstractmethod
    async def get_session(self) -> dict:
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> dict:
        pass

    @abstractmethod
    async def create_session(self) -> dict:
        pass