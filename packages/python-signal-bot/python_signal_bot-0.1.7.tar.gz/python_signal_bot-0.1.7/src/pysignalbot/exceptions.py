""""""
class SignalBotError(Exception):
    """"""

class DispatcherError(SignalBotError):
    """"""

class SocketError(DispatcherError):
    """"""

class RpcCallTimeoutError(SignalBotError):
    """"""

class ConversationError(SignalBotError):
    """"""

class RecipientsError(SignalBotError):
    """"""

class RpcCallError(SignalBotError):
    """"""
    def __init__(self, message: str, error: "ErrorResponse") -> None:
        self.error = error
        super().__init__(message)

class SendError(SignalBotError):
    """"""
    def __init__(self, message: str, results: "PrettyNamespace") -> None:
        self.results = results
        super().__init__(message)

class GroupSendError(RpcCallError):
    """"""
