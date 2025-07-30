from .client import SquaredClient


def SquaredSDK(api_key: str):
    return SquaredClient(api_key)
