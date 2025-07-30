import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")

@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters."""
    return weight_kg / (height_m**2)

@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid=5c0a402d6d946b7c61105cd8056cb22d"
        )
        return response.text

def run():
    mcp.run(transport='stdio')
if __name__ == '__main__':
   run()