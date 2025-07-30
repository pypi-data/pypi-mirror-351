import asyncio
import logging

from h_message_bus import NatsPublisherAdapter

from ...domain.messaging.flows.init_knowledgebase_request import InitKnowledgeBaseRequestMessage
from ...domain.messaging.web.web_get_docs_request_message import WebGetDocsRequestMessage
from ...domain.messaging.web.web_search_request_message import WebSearchRequestMessage


class WebService:
    def __init__(self, nats_publisher_adapter: NatsPublisherAdapter):
        self.nats_publisher_adapter = nats_publisher_adapter
        self.logger = logging.getLogger(__name__)


    async def discover_documentation(self, twitter_user_name: str):
        request = WebGetDocsRequestMessage.create_message(
            twitter_user=twitter_user_name,
            collection_name=f"docs_{twitter_user_name}",
            root_url=None)

        await self.nats_publisher_adapter.publish(request)
        self.logger.info("Requested discovering documentation request for twitter user")
        await asyncio.sleep(0.5)

    async def discover_ecosystem(self, query: str):
        request = WebSearchRequestMessage.create_message(query=query)
        await self.nats_publisher_adapter.publish(request)
        self.logger.info("Requested initial websearch")
        await asyncio.sleep(0.5)

    async def init_knowledge(self, user_name: str):
        request = InitKnowledgeBaseRequestMessage.create_message()
        request.payload["twitter_user"]=user_name
        await self.nats_publisher_adapter.publish(request)
        self.logger.info("Requested init knowledge")
        await asyncio.sleep(0.5)
