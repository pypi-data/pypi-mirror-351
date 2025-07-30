import os
from dotenv import load_dotenv
from langchain_gigachat.chat_models.gigachat import GigaChat
from langchain_openai.chat_models import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack, asynccontextmanager
from httpx import Client
# ─────────── Универсальные импорты чекпоинтера ────────────
AsyncSqliteSaver = None
try:                               # новое расположение (>= 0.4)
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver  # type: ignore
except ImportError:
    try:                           # промежуточное расположение (~0.3)
        from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver  # type: ignore
    except ImportError:
        pass                       # останемся без async-версии

from langgraph.checkpoint.sqlite import SqliteSaver               # sync-вариант# <- NEW
import aiosqlite                                         # <- NEW

load_dotenv()

LLM_PROXY_BASE_URL = os.environ["LLM_PROXY_API_BASE_URL"]
LLM_PROXY_API_KEY = os.environ["LLM_PROXY_API_KEY"]

MCP_SERVERS = {
    "search": {
        "command": "npx",
        "args": ["@playwright/mcp@latest"],
        "env": {
            # Принудительный headless режим для сервера
            "PLAYWRIGHT_HEADLESS": "true",
            "PLAYWRIGHT_TIMEOUT": "30000",
            "PLAYWRIGHT_NO_SANDBOX": "true",
            "PLAYWRIGHT_DISABLE_WEB_SECURITY": "true",
            "PLAYWRIGHT_DISABLE_DEV_SHM_USAGE": "true",
            "PLAYWRIGHT_BROWSER_TIMEOUT": "30000",
            "PLAYWRIGHT_PAGE_TIMEOUT": "20000",
            "PLAYWRIGHT_NAVIGATION_TIMEOUT": "15000"
        }
    },
   "chroma": {
    "command": "uvx",
    "args": [
        "chroma-mcp",
        "--client-type",
        "persistent",
        "--data-dir",
        "/Users/Sergej/codex_cli/mcp-cl/chroma"
    ],
    "env": {"CHROMA_OPENAI_API_KEY": os.environ.get("CHROMA_OPENAI_API_KEY", "")}
}
}
# model = GigaChat(
#     model="GigaChat-2-Max",
#     credentials=os.getenv("GIGACHAT_AUTH"),
#     scope=os.getenv("GIGACHAT_SCOPE"),
#     verify_ssl_certs=False,
#     top_p=0,
#     streaming=False,
#     max_tokens=8000,
#     temperature=1,
#     timeout=600
# )

client = Client(verify=False)
model = ChatOpenAI(
    model_name="gpt-4.1-2025-04-14",
    base_url=f"{LLM_PROXY_BASE_URL}/openai/v1",
    api_key=LLM_PROXY_API_KEY,
    max_tokens=8192,
    http_client=client,
)

@asynccontextmanager
async def setup_agent():
    """
    Создаёт LangGraph-агента с MCP-инструментами.
    Контекст гарантирует закрытие всех ресурсов после использования.
    """
    stack = AsyncExitStack()
    await stack.__aenter__()
    DB_PATH = "./lg_checkpoints.sqlite"

    if AsyncSqliteSaver is not None:                     # асинхронный saver
        saver_cm = AsyncSqliteSaver.from_conn_string(DB_PATH)     # контекст-менеджер
        checkpointer = await stack.enter_async_context(saver_cm)  # открываем и сохраняем
    else:                                                # fallback на синхронный
        checkpointer = SqliteSaver.from_conn_string(DB_PATH)
        # регистрируем закрытие соединения
        stack.push_callback(checkpointer.conn.close)     # type: ignore[attr-defined]


    tools = []

    for config in MCP_SERVERS.values():
        server_params = StdioServerParameters(
            command=config["command"],
            args=config["args"],
            env={**os.environ, **config.get("env", {})}
        )

        # Стартуем MCP-сервер
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport

        # Создаём MCP-сессию
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        # Загружаем инструменты
        server_tools = await load_mcp_tools(session)
        tools.extend(server_tools)

    # Создаём агента с объединёнными инструментами
    agent = create_react_agent(model, tools, checkpointer=checkpointer)

    async def run_agent(prompt: str, *, thread_id: str) -> str:
        """Запускает один шаг агента в контексте указанного thread_id."""
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config={"configurable": {"thread_id": thread_id}},
        )
        return result["messages"][-1].content

    try:
        yield run_agent
    finally:
        await stack.aclose()

