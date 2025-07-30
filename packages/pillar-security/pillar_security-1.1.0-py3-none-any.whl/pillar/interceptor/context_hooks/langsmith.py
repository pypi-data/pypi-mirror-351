from typing import TYPE_CHECKING, Any
from uuid import UUID

from wrapt import wrap_function_wrapper

# Pillar context
from pillar import context_vars as cv
from pillar.interceptor.context_hooks.context_framework_adapter import ContextData, ContextFrameworkAdapter
from pillar.interceptor.context_hooks.context_hook_factory import create_context_hook

if TYPE_CHECKING:
    from pillar.client import Pillar


class LangSmithContextAdapter(ContextFrameworkAdapter):
    """Adapter for LangSmith context hooks."""

    @property
    def provider_name(self) -> str:
        return "langsmith"

    def extract_context(self, run_obj: Any, args: tuple, kwargs: dict) -> ContextData:
        """Extract run_id and root status from LangSmith create_run arguments."""
        # check if the run is a root run
        is_root_run = kwargs.get("parent_run_id") is None

        run_id: str | None = None
        if hasattr(run_obj, "id") and run_obj.id is not None:
            run_id = str(run_obj.id)
        elif "id" in kwargs and isinstance(kwargs["id"], UUID):
            run_id = str(kwargs["id"])

        return ContextData(
            context_id=run_id,
            is_root=is_root_run,
            original_kwargs=kwargs,
        )

    def process_context(self, pillar: "Pillar", context_data: ContextData) -> None:
        """Process LangSmith context data and update Pillar's session ID,
        we are overriding the session ID with the run ID.
        """
        if context_data.context_id and context_data.is_root:
            current_session_id = cv.pillar_session_id.get()
            new_session_id = context_data.context_id
            if current_session_id is not None:
                pillar.logger.warning(f"Overriding session ID: {current_session_id} with {new_session_id}")
            cv.session_id_token(new_session_id)

    async def process_context_async(self, pillar: "Pillar", context_data: ContextData) -> None:
        """Async version of process_context."""
        self.process_context(pillar, context_data)


def _register_langsmith_context_hook(pillar: "Pillar") -> None:
    """
    Register LangSmith hook to intercept run_id and bind to Pillar session.
    """
    try:
        import langsmith.client
    except ImportError:
        return

    has_hooks = False

    def is_valid_class(client_str: str):
        """Check if the class exists and has a create_run method."""
        try:
            client_class = getattr(langsmith.client, client_str)
        except AttributeError:
            return None
        if not hasattr(client_class, "create_run"):
            return None
        return client_class

    # Ensure the Client class and create_run method exist
    sync_client_class = is_valid_class("Client")
    if sync_client_class is not None:
        # Create sync adapter and hook
        sync_adapter = LangSmithContextAdapter(is_async=False, logger=pillar.logger)
        sync_hook = create_context_hook(pillar, sync_adapter)

        # Register sync client hook
        wrap_function_wrapper(
            "langsmith.client",
            "Client.create_run",
            sync_hook,
        )
        has_hooks = True

    # Register async client hook if available
    async_client_class = is_valid_class("AsyncClient")
    if async_client_class is not None:
        # Create async adapter and hook
        async_adapter = LangSmithContextAdapter(is_async=True, logger=pillar.logger)
        async_hook = create_context_hook(pillar, async_adapter)

        wrap_function_wrapper(
            "langsmith.client",
            "AsyncClient.create_run",
            async_hook,
        )
        has_hooks = True

    if has_hooks:
        pillar.logger.debug("Registered LangSmith context hook")
    else:
        pillar.logger.warning("LangSmith not installed, skipping LangSmith context hook")
