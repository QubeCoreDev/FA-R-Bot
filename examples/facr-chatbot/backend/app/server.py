"""ChatKit server for the FAČR knowledge-base chatbot."""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, AsyncIterator

from agents import RunConfig, Runner
from agents.model_settings import ModelSettings
from chatkit.agents import AgentContext, ThreadItemConverter, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)

from .facr_agent import build_facr_agent
from .knowledge_base import KnowledgeBase, build_knowledge_base
from .memory_store import MemoryStore
from .title_agent import title_agent

logger = logging.getLogger(__name__)

DEFAULT_DOCS_DIR = str(
    Path(__file__).resolve().parent.parent.parent.parent.parent.parent
    / "Podklady FAČR"
    / "Podklady MD FAČR"
)


class FACRServer(ChatKitServer[dict[str, Any]]):
    """ChatKit server that powers the FAČR knowledge-base chatbot."""

    def __init__(self, kb: KnowledgeBase) -> None:
        store = MemoryStore()
        super().__init__(store)
        self.store = store
        self.kb = kb
        self.agent = build_facr_agent(kb)
        self.title_agent = title_agent
        self.thread_item_converter = ThreadItemConverter()

    async def respond(
        self,
        thread: ThreadMetadata,
        user_message: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        title_task: asyncio.Task[None] | None = None
        if user_message is not None and thread.title is None:
            title_task = asyncio.create_task(
                self._maybe_update_thread_title(thread, user_message)
            )

        items_page = await self.store.load_thread_items(
            thread.id, None, 20, "desc", context
        )
        items = list(reversed(items_page.data))

        input_items = await self.thread_item_converter.to_agent_input(items)

        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        result = Runner.run_streamed(
            self.agent,
            input_items,
            context=agent_context,
            run_config=RunConfig(model_settings=ModelSettings(temperature=0.3)),
        )

        async for event in stream_agent_response(agent_context, result):
            yield event

        if title_task:
            await title_task

    async def _maybe_update_thread_title(
        self, thread: ThreadMetadata, user_message: UserMessageItem | None
    ) -> None:
        if user_message is None or thread.title is not None:
            return

        run = await Runner.run(
            self.title_agent,
            input=await self.thread_item_converter.to_agent_input(user_message),
        )
        model_result: str = run.final_output
        model_result = model_result[:1].upper() + model_result[1:]
        thread.title = model_result.strip(".")


def create_facr_server() -> FACRServer:
    """Build the knowledge base and return a configured server instance."""
    docs_dir = os.environ.get("FACR_DOCS_DIR", DEFAULT_DOCS_DIR)
    logger.info("Loading FAČR knowledge base from: %s", docs_dir)
    kb = build_knowledge_base(docs_dir)
    return FACRServer(kb)
