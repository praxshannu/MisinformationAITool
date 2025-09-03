# This script fetches the current weather for a given city using the python-weather library.
#
# To use this script, you need to install the library first:
# pip install python-weather

import python_weather
import asyncio
import platform

async def get_weather(city):
  """
  Fetches and prints the current weather for a given city.
  """
  async with python_weather.Client(format=python_weather.IMPERIAL) as client:
    try:
      weather = await client.get(city)
      print(f"Current weather in {city}:")
      print(f"  Temperature: {weather.current.temperature}°F")
      print(f"  Description: {weather.current.description}")
      print(f"  Wind speed: {weather.current.wind_speed} mph")
    except Exception as e:
      print(f"Could not fetch weather for {city}. Error: {e}")

if __name__ == "__main__":
  # Fix for asyncio on Windows
  if platform.system() == "Windows":
      asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
      
  city = input("Enter a city name: ")
  if city:
    asyncio.run(get_weather(city))
  else:
    print("Please enter a city name.")
