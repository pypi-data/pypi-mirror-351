import enum
from datetime import datetime
from uuid import UUID

from pydantic.v1 import Field

from fiddler.schemas.base import BaseModel


@enum.unique
class WebhookProvider(str, enum.Enum):
    # provider is 'SLACK' or 'MS_TEAMS' as of May 2025.
    # keeping OTHER in enum for existing webhooks for backwards compatibility
    SLACK = 'SLACK'
    MS_TEAMS = 'MS_TEAMS'
    OTHER = 'OTHER'


class WebhookResp(BaseModel):
    id: UUID = Field(alias='uuid')
    name: str
    url: str
    provider: WebhookProvider
    created_at: datetime
    updated_at: datetime
