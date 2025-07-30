from abs_integration_core.repository import SubscriptionsRepository
from abs_repository_core.services.base_service import BaseService
from abs_integration_core.schema import Subscription


class SubscriptionService(BaseService):
    def __init__(self, subscription_repository: SubscriptionsRepository):
        super().__init__(subscription_repository)

    def add(self, schema: Subscription) -> Subscription:
        return super().add(schema)

    def remove_by_uuid(self, uuid: str) -> Subscription:
        id = self.get_by_attr("uuid", uuid).id
        return super().remove_by_id(id)
