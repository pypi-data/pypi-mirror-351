from .exception import *
from playwright.sync_api._generated import ElementHandle, Page

__all__ = ['timeout', 'findElement']

timeout: int

def findElement(selectorString: str, fromElement: Page | ElementHandle, timeout: int = None) -> ElementHandle | None: ...
