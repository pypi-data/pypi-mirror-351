from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv
import httpx
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.requests import Request

from challenge_mcp.authfastmcp import AuthFastMCP

# Load environment variables from .env file
load_dotenv(override=True)


# Define a type-safe context class
@dataclass
class AppContext:
    async_client: httpx.AsyncClient  # Replace with your actual resource type


# Create the lifespan context manager
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    # Initialize resources on startup
    async_client = httpx.AsyncClient(
        base_url=os.environ["API_BASE_URL"],
        # headers={"Authorization": f"Bearer {os.environ["BEARER_TOKEN"]}"},
        timeout=None,
    )
    try:
        # Make resources available during operation
        yield AppContext(async_client=async_client)
    finally:
        # Clean up resources on shutdown
        await async_client.aclose()


# Create an MCP server
mcp = AuthFastMCP(
    "MyServer",
    host="0.0.0.0",
    # mount_path="/v1/mcp/",
    sse_path="/v1/mcp/sse",
    message_path="/v1/mcp/messages/",
    port=8050,
    lifespan=app_lifespan,
    timeout_keep_alive=30,  # Keep-alive timeout in seconds
    timeout_graceful_shutdown=10,  # Graceful shutdown timeout
)

stdio_mcp = FastMCP("MyStdioServer", lifespan=app_lifespan)


@mcp.custom_route("/v1/mcp/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "message": "Server is operational"})


# Simple tool
@mcp.tool()
def test_tool(ctx: Context, name: str) -> str:
    """Test tool

    Args:
        name: text argument
    """
    token = ctx.request_context.session.auth_token

    return f"Hello, {name}! Nice to meet you. Token: {token if token else 'Not found'}"


@stdio_mcp.tool()
@mcp.tool()
async def get_active_challenge_list(
    ctx: Context,
    status: Optional[List[int]] = None,
    is_clone: Optional[bool] = None,
    search_type: Optional[str] = None,
    enterprise_id: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    challenge_based_on: Optional[str] = None,
    bearer_token=None,
) -> str:
    """Fetch list of active challenges with pagination and filters.
    An 'active' or 'launched' challenge is a challenge which has been enabled for participation from a challenge pool template. Active challenges can be in progress (status = 1), completed (status = 0), or a draft (status = 99).
    The list is sorted by challenge activation date.
    Tool returns an object with keys total (int), page (int), limit (int), totalPages (int), and challenges (array of challenge objects).

    Args:
        status: Filter by challenge status. Possible values: [1 (ACTIVE / IN PROGRESS), 0 (INACTIVE / COMPLETED), 99 (DRAFT)]
        search_type: Type of active challenge. Possible values: 'all_users', 'enterprise', 'inter_company', 'event', 'private'
        enterprise_id: Filter by enterprise ID
        page: Page number for pagination (starts at 1)
        limit: Number of items per page
        search: Search query string for challenge name, challenge enterprise, name of challenge author, or email of challenge author
        challenge_based_on: Filter by challenge type. Possible values: 'calories_burned', 'content', 'step', 'water_intake', 'workout_minutes'
    """
    if bearer_token is None:
        bearer_token = ctx.request_context.session.auth_token

    query_params = {}
    if status is not None:
        query_params["status"] = status
    if is_clone is not None:
        query_params["is_clone"] = is_clone
    if search_type is not None:
        query_params["search_type"] = search_type
    if enterprise_id is not None:
        query_params["enterprise_id"] = enterprise_id
    if page is not None:
        query_params["page"] = page
    if limit is not None:
        query_params["limit"] = limit
    if search is not None:
        query_params["search"] = search
    if challenge_based_on is not None:
        query_params["challenge_based_on"] = challenge_based_on

    response: httpx.Response = (
        await ctx.request_context.lifespan_context.async_client.get(
            "/v1/challenge/active-challenge/list",
            params=query_params,
            headers={"Authorization": f"Bearer {bearer_token}"},
        )
    )
    if not response.is_success:
        raise Exception(response.text)
    return response.text


@stdio_mcp.tool()
@mcp.tool()
async def get_active_challenge_participants(
    ctx: Context,
    id: str,
    search: Optional[str] = None,
    team_id: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    includes_member_data: bool = False,
    bearer_token=None,
) -> str:
    """Fetch participants of given active challenge id.
    Note: This endpoint does not support server-side sorting. Fetch all items and manually sort them in the LLM code logic if needed.
    Tool returns an object with keys totalRecords (int), page (int), limit (int), and data (array of participant objects).

    Args:
        id: The id of the active challenge for which to fetch participants
        search: Search term for name, email, or team name
        team_id: Team ID to filter participants by (MongoDB ObjectId)
        page: Page number for pagination (starts at 1)
        limit: Number of items per page (default: 10)
        includes_member_data: Whether to include additional member data (true/false)
    """
    if bearer_token is None:
        bearer_token = ctx.request_context.session.auth_token

    query_params = {}
    if search is not None:
        query_params["search"] = search
    if team_id is not None:
        query_params["team_id"] = team_id
    if page is not None:
        query_params["page"] = page
    if limit is not None:
        query_params["limit"] = limit
    if includes_member_data is not None:
        query_params["includes_member_data"] = includes_member_data

    response = await ctx.request_context.lifespan_context.async_client.get(
        "/v1/challenge/active-challenge/" + id + "/participants",
        params=query_params,
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    if not response.is_success:
        raise Exception(response.text)
    return response.text


@stdio_mcp.tool()
@mcp.tool()
async def get_active_challenge_participant_workouts(
    ctx: Context, id: str, user_id: str, from_date: str, to_date: str, bearer_token=None
) -> str:
    """Fetch workouts of particpant with given user_id for active challenge with given challenge_id.
    Tool returns object with the key 'workouts' (array of workout objects).

    Args:
        id: The id of the active challenge
        user_id: The id of the participant for which to fetch workouts
        from_date: Date from which to fetch workout information
        to_date: Date till which to fetch workout information
    """
    if bearer_token is None:
        bearer_token = ctx.request_context.session.auth_token

    response = await ctx.request_context.lifespan_context.async_client.get(
        "/v1/challenge/active-challenge/"
        + id
        + "/participants/"
        + user_id
        + "/workouts"
        + f"?from_date={from_date}&to_date={to_date}",
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    if not response.is_success:
        raise Exception(response.text)
    return response.text


@stdio_mcp.tool()
@mcp.tool()
async def get_active_challenge_teams(
    ctx: Context,
    id: str,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    sort_on: Optional[str] = None,
    bearer_token=None,
) -> str:
    """Fetch teams of given active challenge id (in no particular order).
    Tool returns object with the keys total (int), page (int), limit (int), and data (array of team objects).

    Args:
        id: The id of the active challenge for which to fetch teams
        search: Search term for team name
        page: Page number for pagination (starts at 1)
        limit: Number of items per page (default: 10)
        sort_on: Sort teams based on stats or default sorting. Possible values: 'stats', ''
    """
    if bearer_token is None:
        bearer_token = ctx.request_context.session.auth_token

    query_params = {}
    if search is not None:
        query_params["search"] = search
    if page is not None:
        query_params["page"] = page
    if limit is not None:
        query_params["limit"] = limit
    if sort_on is not None:
        query_params["sort_on"] = sort_on

    response = await ctx.request_context.lifespan_context.async_client.get(
        "/v1/challenge/active-challenge/" + id + "/teams",
        params=query_params,
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    if not response.is_success:
        raise Exception(response.text)
    return response.text


@stdio_mcp.tool()
@mcp.tool()
async def get_challenge_pool_list(
    ctx: Context,
    status: Optional[str] = None,
    search: Optional[str] = None,
    challenge_based_on: Optional[str] = None,
    challenge_type: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    no_of_days: Optional[int] = None,
    is_launch_challenge: Optional[bool] = None,
    bearer_token=None,
) -> str:
    """Fetch list of challenges from the challenge pool with pagination and filters.
     A challenge pool record is like a challenge template. People cannot participate directly from the challenges in the challenge pool, the challenge has to be activated and become an active challenge first.
     The list is sorted by challenge creation date.
     Tool returns an object with keys total (int), page (int), limit (int), totalPages (int), and challenges (array of challenge objects).

    Args:
        status: Filter by challenge status. Possible values: 'active', 'inactive', 'all'
        search: Search term to filter challenges by title. Does not search for author email or name.
        challenge_based_on: Filter by challenge type. Possible values: 'calories_burned', 'content', 'step', 'water_intake', 'workout_minutes'
        challenge_type: Filter by challenge period type. Possible values: 'daily', 'weekly'
        page: Page number for pagination (starts at 1)
        limit: Number of items per page (default: 10)
        no_of_days: Filter by number of days
        is_launch_challenge: Filter challenges that can be launched
    """
    if bearer_token is None:
        bearer_token = ctx.request_context.session.auth_token

    query_params = {}
    if status is not None:
        query_params["status"] = status
    if search is not None:
        query_params["search"] = search
    if challenge_based_on is not None:
        query_params["challenge_based_on"] = challenge_based_on
    if challenge_type is not None:
        query_params["challenge_type"] = challenge_type
    if page is not None:
        query_params["page"] = page
    if limit is not None:
        query_params["limit"] = limit
    if no_of_days is not None:
        query_params["no_of_days"] = no_of_days
    if is_launch_challenge is not None:
        query_params["is_launch_challenge"] = is_launch_challenge

    response: httpx.Response = (
        await ctx.request_context.lifespan_context.async_client.get(
            "/v1/challenge/pool/list",
            params=query_params,
            headers={"Authorization": f"Bearer {bearer_token}"},
        )
    )
    if not response.is_success:
        raise Exception(response.text)
    return response.text


@stdio_mcp.tool()
@mcp.tool()
async def get_challenge_pool_by_id(
    ctx: Context, challenge_id: str, bearer_token=None
) -> str:
    """Fetch details of a specific challenge pool by ID.
    Tool returns object with keys message (string) and challenge (challenge object).

    Args:
        challenge_id: The ID of the challenge pool to fetch
    """
    if bearer_token is None:
        bearer_token = ctx.request_context.session.auth_token

    response = await ctx.request_context.lifespan_context.async_client.get(
        f"/v1/challenge/pool/{challenge_id}",
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    if not response.is_success:
        raise Exception(response.text)
    return response.text


@stdio_mcp.tool()
@mcp.tool()
async def get_active_challenge_by_id(
    ctx: Context, challenge_id: str, bearer_token=None
) -> str:
    """Fetch details of a specific active challenge by ID.
    Tool returns active challenge object.

    Args:
        challenge_id: The ID of the active challenge to fetch
    """
    if bearer_token is None:
        bearer_token = ctx.request_context.session.auth_token

    response = await ctx.request_context.lifespan_context.async_client.get(
        f"/v1/challenge/active-challenge/{challenge_id}",
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    if not response.is_success:
        raise Exception(response.text)
    return response.text


@stdio_mcp.tool()
@mcp.tool()
async def get_active_challenge_stats(
    ctx: Context,
    status: Optional[int] = None,
    type_filter: Optional[str] = None,
    search: Optional[str] = None,
    skip: Optional[int] = 0,
    enterprise_id: Optional[str] = None,
    limit: Optional[int] = 10,
    bearer_token=None,
) -> str:
    """Fetch comprehensive statistics for associated with each active challenge, including number of participants and total participant progress.
    Note: This endpoint does not support server-side sorting. Fetch all items and manually sort them in the LLM code logic if needed.
    Tool returns object with keys totalRecords (int), skip (int), and data (array of challenge stats objects).
    Args:
        status: Challenge status filter. Possible values: 1 (ACTIVE), 0 (INACTIVE), 99 (DRAFT)
        type_filter: Filter by challenge type. Possible values: 'all_users', 'enterprise', 'inter_company', 'event', 'private'
        search: Search query string for challenge name, challenge enterprise, name of challenge author, or email of challenge author
        skip: Number of records to skip for pagination
        enterprise_id: Filter by enterprise ID
        limit: Number of records to return (default: 10)
    """
    if bearer_token is None:
        bearer_token = ctx.request_context.session.auth_token

    query_params = {}
    if status is not None:
        query_params["status"] = status
    if type_filter is not None:
        query_params["type_filter"] = type_filter
    if search is not None:
        query_params["search"] = search
    if skip is not None:
        query_params["skip"] = skip
    if enterprise_id is not None:
        query_params["enterprise_id"] = enterprise_id
    if limit is not None:
        query_params["limit"] = limit

    response = await ctx.request_context.lifespan_context.async_client.get(
        "/v1/challenge/active-challenge/list/stats",
        params=query_params,
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    if not response.is_success:
        raise Exception(response.text)
    return response.text


# Run the server
if __name__ == "__main__":
    try:
        # stdio_mcp.run(transport="stdio")
        mcp.run(transport="sse")  # , mount_path=mcp.settings.mount_path)
    except Exception as e:
        print(f"Server error: {e}")
        raise
    # import asyncio

    # asyncio.run(get_active_challenges())
