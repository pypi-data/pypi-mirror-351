from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

TMessage = TypeVar("TMessage")


class ABCQueueProducer(Generic[TMessage], metaclass=ABCMeta):
    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    async def publish(self, request: TMessage) -> None: ...
