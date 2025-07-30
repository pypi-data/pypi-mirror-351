import logging
import subprocess
from datetime import datetime
from enum import Enum

import httpx
from mcp.server.fastmcp import FastMCP
from PIL import Image as PILImage

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Setup Console logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

# Create an MCP server
mcp = FastMCP("Espresso-MCP")


@mcp.tool()
def list_avds() -> list:
    """List all available Android Virtual Devices (AVDs)"""
    result = subprocess.run(["emulator", "-list-avds"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error listing AVDs: {result.stderr}")
    return result.stdout.splitlines()


@mcp.tool()
def list_emulators() -> list:
    """List all running Android Emulators"""
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error listing emulators: {result.stderr}")
    lines = result.stdout.splitlines()
    print("---lines", lines)
    emulators = [line.split()[0] for line in lines[1:] if "emulator" in line]
    return emulators


@mcp.tool()
def start_emulator(emulator_name: str) -> str:
    """Start an Android Emulator by name"""
    result = subprocess.Popen(
        ["emulator", "-avd", emulator_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return f"Emulator '{emulator_name}' is starting."


@mcp.tool()
def kill_emulator(emulator_name: str) -> str:
    """Kill a specific Android Emulator"""
    result = subprocess.run(
        ["adb", "-s", emulator_name, "emu", "kill"], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error killing emulator '{emulator_name}': {result.stderr}")
    return f"Emulator '{emulator_name}' has been killed."


@mcp.tool()
def dump_ui_hierarchy() -> str:
    """Dump the UI hierarchy of the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "uiautomator", "dump"], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error dumping UI hierarchy: {result.stderr}")

    # The UI hierarchy is dumped to a file on the device /sdcard/window_dump.xml
    # Pull the file to the local machine and read its contents
    pull_result = subprocess.run(
        ["adb", "pull", "/sdcard/window_dump.xml", "window_dump.xml"],
        capture_output=True,
        text=True,
    )
    if pull_result.returncode != 0:
        raise RuntimeError(f"Error pulling UI hierarchy file: {pull_result.stderr}")

    with open("window_dump.xml", encoding="utf-8") as f:
        ui_hierarchy = f.read()
    return ui_hierarchy


@mcp.tool()
def open_uri(uri: str) -> str:
    """Open a URI on the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", uri],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error opening URI '{uri}': {result.stderr}")
    return f"URI '{uri}' has been opened successfully."


@mcp.tool()
def list_apps() -> list:
    """List all installed apps on the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "pm", "list", "packages"], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error listing installed apps: {result.stderr}")
    apps = [line.replace("package:", "").strip() for line in result.stdout.splitlines()]
    return apps


@mcp.tool()
def start_app(package_name: str) -> str:
    """Start an app on the connected Android device"""
    result = subprocess.run(
        [
            "adb",
            "shell",
            "monkey",
            "-p",
            package_name,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error starting app '{package_name}': {result.stderr}")
    return f"App '{package_name}' has been started successfully."


@mcp.tool()
def stop_app(package_name: str) -> str:
    """Stop an app on the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "am", "force-stop", package_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error stopping app '{package_name}': {result.stderr}")
    return f"App '{package_name}' has been stopped successfully."


@mcp.tool()
def install_app(app_path: str) -> str:
    """Install an App APK on the connected Android device"""
    result = subprocess.run(
        ["adb", "install", app_path], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error installing App: {result.stderr}")
    return f"App '{app_path}' has been installed successfully."


@mcp.tool()
def uninstall_app(package_name: str) -> str:
    """Uninstall an app from the connected Android device"""
    result = subprocess.run(
        ["adb", "uninstall", package_name], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error uninstalling app '{package_name}': {result.stderr}")
    return f"App '{package_name}' has been uninstalled successfully."


@mcp.tool()
def clear_app_data(package_name: str) -> str:
    """Clear app data for a specific app on the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "pm", "clear", package_name], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Error clearing app data for '{package_name}': {result.stderr}"
        )
    return f"App data for '{package_name}' has been cleared."


@mcp.tool()
def take_screenshot(output_path: str) -> str:
    """Take a screenshot of the connected Android device"""

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file = f"/sdcard/espresso-mcp_screenshot_{timestamp}.mp4"

    # Capture screenshot on the device
    subprocess.run(["adb", "shell", "screencap", "-p", file], check=True)
    # Pull the screenshot to the local machine
    subprocess.run(["adb", "pull", file, "screenshot.png"], check=True)
    # Remove the screenshot from the device
    subprocess.run(["adb", "shell", "rm", file], check=True)

    # Compress the screenshot to reduce size
    with PILImage.open("screenshot.png") as img:
        width, height = img.size
        new_width = int(width * 0.3)
        new_height = int(height * 0.3)
        resized_img = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
        resized_img.save(output_path, "PNG", quality=85, optimize=True)

    return f"Screenshot saved to '{output_path}'."


@mcp.tool()
def record_screen(output_path: str, duration: int) -> str:
    """Record the screen of the connected Android device for a specified duration"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file = f"/sdcard/espresso-mcp_recording_{timestamp}.mp4"
    result = subprocess.run(
        ["adb", "shell", "screenrecord", file],
        capture_output=True,
        text=True,
        timeout=duration,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error recording screen: {result.stderr}")

    pull_result = subprocess.run(
        ["adb", "pull", file, output_path],
        capture_output=True,
        text=True,
    )
    if pull_result.returncode != 0:
        raise RuntimeError(f"Error pulling recorded file: {pull_result.stderr}")
    return f"Screen recording saved to '{output_path}'."


class Button(Enum):
    HOME = "3"
    BACK = "4"
    MENU = "82"
    POWER = "26"
    VOLUME_UP = "24"
    VOLUME_DOWN = "25"
    CAMERA = "27"
    ENTER = "66"


@mcp.tool()
def press_button(button: Button) -> str:
    """Simulate a button press on the connected Android device using an Enum button"""
    result = subprocess.run(
        ["adb", "shell", "input", "keyevent", button.value],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error pressing button '{button.name}': {result.stderr}")
    return f"Button '{button.name}' has been pressed."


@mcp.tool()
def type_text(text: str) -> str:
    """Type text on the connected Android device"""
    result = subprocess.run(
        ["adb", "shell", "input", "text", text],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error typing text '{text}': {result.stderr}")
    return f"Text '{text}' has been typed successfully."


@mcp.tool()
def tap(x: int, y: int) -> str:
    """Simulate a tap on the connected Android device at the specified coordinates"""
    result = subprocess.run(
        ["adb", "shell", "input", "tap", str(x), str(y)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error performing tap at ({x}, {y}): {result.stderr}")
    return f"Tap performed at coordinates ({x}, {y})."


@mcp.tool()
def swipe(direction: str, duration: int = 500) -> str:
    """Perform a swipe gesture in a specific direction on the connected Android device"""
    directions = {
        "up": (500, 1500, 500, 500),
        "down": (500, 500, 500, 1500),
        "left": (1500, 500, 500, 500),
        "right": (500, 500, 1500, 500),
    }
    if direction not in directions:
        raise ValueError(
            f"Invalid direction '{direction}'. Valid directions are: {list(directions.keys())}"
        )

    start_x, start_y, end_x, end_y = directions[direction]
    result = subprocess.run(
        [
            "adb",
            "shell",
            "input",
            "swipe",
            str(start_x),
            str(start_y),
            str(end_x),
            str(end_y),
            str(duration),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error performing swipe: {result.stderr}")
    return f"Swipe gesture performed in '{direction}' direction over {duration}ms."


@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{city}")
        return response.text


@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"


def main():
    # Start the MCP server
    print("Starting Espresso MCP server...")

    import argparse

    parser = argparse.ArgumentParser(description="Run MCP Server")
    parser.add_argument("--sse", action="store_true", help="Use SSE transport")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=3333, help="Port to listen on")
    args = parser.parse_args()

    transport = "stdio"  # Default transport
    if args.sse:
        transport = "sse"

    # mcp.run()
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
