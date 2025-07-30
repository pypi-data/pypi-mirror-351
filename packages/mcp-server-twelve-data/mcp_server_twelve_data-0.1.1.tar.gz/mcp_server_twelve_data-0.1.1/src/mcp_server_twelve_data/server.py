import logging
from typing import Literal

import httpx
from mcp.server.fastmcp import FastMCP


from .requests.get_cryptocurrencies_params import GetCryptocurrenciesParams
from .requests.get_forex_pairs_params import GetForexPairsParams
from .requests.get_price_params import GetPriceParams
from .requests.get_stocks_params import GetStocksParams
from .requests.get_time_series_params import GetTimeSeriesParams
from .responses.get_cryptocurrencies_response import GetCryptocurrenciesResponse
from .responses.get_forex_pairs_response import GetForexPairsResponse
from .responses.get_price_response import GetPriceResponse
from .responses.get_stock_response import GetStocksResponse
from .responses.get_time_series_response import GetTimeSeriesResponse


def serve(api_base: str, transport: Literal["stdio", "sse", "streamable-http"]) -> None:
    logger = logging.getLogger(__name__)

    server = FastMCP("mcp-twelve-data")

    # @server.tool()
    # def add(a: int, b: int) -> int:
    #    """Add two numbers"""
    #    return a + b

    @server.tool(name="GetTimeSeries", description="Time series tool calling /time_series endpoint")
    async def get_time_series(params: GetTimeSeriesParams) -> GetTimeSeriesResponse:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{api_base}/time_series", params=params.model_dump(exclude_none=True))
            resp.raise_for_status()
            return GetTimeSeriesResponse.model_validate(resp.json())

    @server.tool(name="GetPrice", description="Real-time price tool calling /price endpoint")
    async def get_price(params: GetPriceParams) -> GetPriceResponse:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{api_base}/price", params=params.model_dump(exclude_none=True))
            resp.raise_for_status()
            return GetPriceResponse.model_validate(resp.json())

    @server.tool(name="GetStocks", description="Stocks list tool calling /stocks endpoint")
    async def get_stocks(params: GetStocksParams) -> GetStocksResponse:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{api_base}/stocks", params=params.model_dump(exclude_none=True))
            resp.raise_for_status()
            return GetStocksResponse.model_validate(resp.json())

    @server.tool(name="GetForexPairs", description="Forex pairs list tool calling /forex_pairs endpoint")
    async def get_forex_pairs(params: GetForexPairsParams) -> GetForexPairsResponse:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{api_base}/forex_pairs", params=params.model_dump(exclude_none=True))
            resp.raise_for_status()
            return GetForexPairsResponse.model_validate(resp.json())

    @server.tool(name="GetCryptocurrencies",
                 description="Cryptocurrencies list tool calling /cryptocurrencies endpoint")
    async def get_cryptocurrencies(params: GetCryptocurrenciesParams) -> GetCryptocurrenciesResponse:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{api_base}/cryptocurrencies", params=params.model_dump(exclude_none=True))
            resp.raise_for_status()
            return GetCryptocurrenciesResponse.model_validate(resp.json())

    server.run(transport=transport)
    # server.run(transport="streamable-http")
