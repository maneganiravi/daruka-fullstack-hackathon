import asyncio
import json
import os
import subprocess
import time
import httpx
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9222
BASE_URL = "http://localhost:5173"


async def main():
    user_data = os.path.abspath("chrome_temp_config")
    os.makedirs(user_data, exist_ok=True)
    cmd = ["powershell", "-Command", "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force"]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={user_data}",
        "--headless=new",
        "--window-size=1400,900"
    ])
    time.sleep(2)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"http://127.0.0.1:{CDP_PORT}/json")
            tabs = [t for t in res.json() if t.get("type") == "page"]
            ws_url = tabs[0]["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            msg_id = 0

            async def send_cmd(method, params=None):
                nonlocal msg_id
                msg_id += 1
                cmd = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(cmd))
                while True:
                    resp = json.loads(await ws.recv())
                    if resp.get("id") == msg_id:

                        return resp.get("result", {})

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")

            await send_cmd("Page.navigate", {"url": f"{BASE_URL}/"})
            await asyncio.sleep(2)

            inspect_code = """
            (() => {
                const map = window.__debug_map;
                return {
                    config: window.mapboxgl ? Object.keys(window.mapboxgl.config || {}) : null,
                    mapTransform: !!(map && map._transformRequest),
                    mapStyle: map ? map.getStyle()?.name : null
                };
            })()
            """
            eval_res = await send_cmd("Runtime.evaluate", {"expression": inspect_code, "returnByValue": True})
            print("Inspect mapboxgl:", json.dumps(eval_res.get("result", {}).get("value", {}), indent=2))

    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(main())
