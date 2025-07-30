from .exception import *
import uiautomation as auto

__all__ = ['timeout', 'findElement']

timeout: int

def findElement(selectorString: str = None, fromElement: auto.Control = None, timeout: int = None) -> auto.Control | None: ...
