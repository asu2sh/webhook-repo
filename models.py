from pydantic import BaseModel
from datetime import datetime


class GitHubEvent(BaseModel):
    request_id: str
    author: str
    action: str
    from_branch: str = None
    to_branch: str
    timestamp: datetime
