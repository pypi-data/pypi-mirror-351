import httpx
from mcp.server.fastmcp import FastMCP
from teamwork_mcp.manifest_tool_server import FastMCP, get_fast_mcp_server

mcp = get_fast_mcp_server()

@mcp.tool()
async def echo(state: str) -> str:
    """这个工具是一个简单的回声工具，它会返回输入的字符串"""
    return state


@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)


@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{city}")
        return response.text

@mcp.resource("resource://my-resource")
async def get_data() -> str:
    return "Hello, world!"


@mcp.prompt()
def analyze_table(table_name: str):
    schema = "..."
    return [
        {
            "role": "user",
            "content": f"Analyze this schema:\n{schema}"
        }
    ]