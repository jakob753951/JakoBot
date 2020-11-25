from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserWarning:
    time: datetime
    reason: str = '[no reason given]'
    strikes: int = 1