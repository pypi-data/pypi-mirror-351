from asyncio import Queue
from typing import  Optional, Type, Callable
from ws_bom_robot_app.llm.models.api import LlmAppTool
from ws_bom_robot_app.llm.providers.llm_manager import LlmInterface
from ws_bom_robot_app.llm.vector_store.db.manager import VectorDbManager
from ws_bom_robot_app.llm.tools.utils import getRandomWaitingMessage, translate_text
from ws_bom_robot_app.llm.tools.models.main import NoopInput,DocumentRetrieverInput,ImageGeneratorInput
from pydantic import BaseModel, ConfigDict

class ToolConfig(BaseModel):
    function: Callable
    model: Optional[Type[BaseModel]] = NoopInput
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

class ToolManager:
    """
    ToolManager is responsible for managing various tools used in the application.

    Attributes:
        app_tool (LlmAppTool): The application tool configuration.
        api_key (str): The API key for accessing external services.
        callbacks (list): A list of callback functions to be executed.

    Methods:
        document_retriever(query: str): Asynchronously retrieves documents based on the query.
        image_generator(query: str, language: str = "it"): Asynchronously generates an image based on the query.
        get_coroutine(): Retrieves the coroutine function based on the tool configuration.
    """

    def __init__(
        self,
        llm: LlmInterface,
        app_tool: LlmAppTool,
        callbacks: list,
        queue: Optional[Queue] = None
    ):
        self.llm = llm
        self.app_tool = app_tool
        self.callbacks = callbacks
        self.queue = queue


    #region functions
    async def document_retriever(self, query: str) -> list:
        """
        Asynchronously retrieves documents based on the provided query using the specified search settings.

        Args:
          query (str): The search query string.

        Returns:
          list: A list of retrieved documents based on the search criteria.

        Raises:
          ValueError: If the configuration for the tool is invalid or the vector database is not found.

        Notes:
          - The function supports different search types such as "similarity", "similarity_score_threshold", "mmr", and "mixed".
          - The search settings can be customized through the `app_tool.search_settings` attribute.
          - If a queue is provided, a waiting message is put into the queue before invoking the search.
        """
        if (
            self.app_tool.type == "function" and self.app_tool.vector_db
            #and self.settings.get("dataSource") == "knowledgebase"
        ):
            search_type = "similarity"
            search_kwargs = {"k": 4}
            if self.app_tool.search_settings:
                search_settings = self.app_tool.search_settings # type: ignore
                if search_settings.search_type == "similarityScoreThreshold":
                    search_type = "similarity_score_threshold"
                    search_kwargs = {
                        "score_threshold": search_settings.score_threshold_id if search_settings.score_threshold_id else  0.5,
                        "k": search_settings.search_k if search_settings.search_k else 100
                    }
                elif search_settings.search_type == "mmr":
                    search_type = "mmr"
                    search_kwargs = {"k": search_settings.search_k if search_settings.search_k else 4}
                elif search_settings.search_type == "default":
                    search_type = "similarity"
                    search_kwargs = {"k": search_settings.search_k if search_settings.search_k else 4}
                else:
                    search_type = "mixed"
                    search_kwargs = {"k": search_settings.search_k if search_settings.search_k else 4}
            if self.queue:
              await self.queue.put(getRandomWaitingMessage(self.app_tool.waiting_message, traduction=False))

            return await VectorDbManager.get_strategy(self.app_tool.vector_type).invoke(
                self.llm.get_embeddings(),
                self.app_tool.vector_db,
                query,
                search_type,
                search_kwargs,
                app_tool=self.app_tool,
                llm=self.llm.get_llm(),
                source=self.app_tool.function_id,
                )
        return []
        #raise ValueError(f"Invalid configuration for {self.settings.name} tool of type {self.settings.type}. Must be a function or vector db not found.")

    async def image_generator(self, query: str, language: str = "it"):
        """
        Asynchronously generates an image based on the query.
        set OPENAI_API_KEY in your environment variables
        """
        from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
        model = self.app_tool.model or "dall-e-3"
        random_waiting_message = getRandomWaitingMessage(self.app_tool.waiting_message, traduction=False)
        if not language:
            language = "it"
        await translate_text(
            self.llm, language, random_waiting_message, self.callbacks
        )
        try:
            #set os.environ.get("OPENAI_API_KEY")!
            image_url = DallEAPIWrapper(model=model).run(query)  # type: ignore
            return image_url
        except Exception as e:
            return f"Error: {str(e)}"

    #endregion

    #class variables (static)
    _list: dict[str,ToolConfig] = {
        "document_retriever": ToolConfig(function=document_retriever, model=DocumentRetrieverInput),
        "image_generator": ToolConfig(function=image_generator, model=ImageGeneratorInput),
    }

    #instance methods
    def get_coroutine(self):
        tool_cfg = self._list.get(self.app_tool.function_name)
        return getattr(self, tool_cfg.function.__name__)  # type: ignore
