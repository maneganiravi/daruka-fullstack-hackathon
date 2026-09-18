import asyncio
import json
import os
import subprocess
import time
import httpx
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9222


async def main():
    user_data = os.path.abspath("chrome_temp_profile_diag")
    os.makedirs(user_data, exist_ok=True)

    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={user_data}",
        "--headless=new",
        "--use-gl=angle",
        "--use-angle=swiftshader",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1400,900"
    ])

    time.sleep(2)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"http://127.0.0.1:{CDP_PORT}/json")
            tabs = res.json()
            ws_url = tabs[0]["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            msg_id = 0

            async def send_cmd(method, params=None):
                nonlocal msg_id
                msg_id += 1
                cmd = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(cmd))
                return msg_id

            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("Network.enable")

            # Setup login
            await send_cmd("Page.navigate", {"url": "http://localhost:5173/login"})
            await asyncio.sleep(1)

            auth_setup = """
            (async () => {
                const res = await fetch('http://localhost:8000/api/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: 'admin@darukaa.earth', password: 'AdminPassword123!'})
                });
                const data = await res.json();
                localStorage.setItem('daruka_token', data.access_token);
                localStorage.setItem('daruka_user', JSON.stringify(data.user));
                return data.user.email;
            })()
            """
            await send_cmd("Runtime.evaluate", {"expression": auth_setup, "awaitPromise": True})

            # Navigate to map
            await send_cmd("Page.navigate", {"url": "http://localhost:5173/map"})

            # Listen to messages for 8 seconds
            end_time = time.time() + 8
            while time.time() < end_time:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    msg = json.loads(raw)
                    method = msg.get("method", "")

                    if method == "Runtime.consoleAPICalled":
                        args = [
                            str(a.get("value", a.get("description", "")))
                            for a in msg.get("params", {}).get("args", [])
                        ]
                        print(f"[CONSOLE {msg['params']['type'].upper()}]: {' '.join(args)}")
                    elif method == "Runtime.exceptionThrown":
                        print(f"[EXCEPTION]: {msg.get('params', {}).get('exceptionDetails', {})}")
                    elif method == "Network.responseReceived":
                        url = msg.get("params", {}).get("response", {}).get("url", "")
                        status = msg.get("params", {}).get("response", {}).get("status", "")
                        lower_url = url.lower()
                        keywords = ("arcgis", "mapbox", "carto", "openstreetmap", "tile")
                        if any(kw in lower_url for kw in keywords):
                            print(f"[NET RESPONSE {status}]: {url}")
                    elif method == "Network.loadingFailed":
                        params = msg.get("params", {})
                        print(f"[NET FAILED]: {params.get('errorText')} - reqId {params.get('requestId')}")
                except asyncio.TimeoutError:
                    pass

            # Inspect map canvas in DOM
            eval_map = """
            (() => {
                const canvas = document.querySelector('.mapboxgl-canvas');
                const container = document.querySelector('.mapboxgl-map');
                return {
                    hasCanvas: !!canvas,
                    canvasWidth: canvas ? canvas.width : 0,
                    canvasHeight: canvas ? canvas.height : 0,
                    canvasClientWidth: canvas ? canvas.clientWidth : 0,
                    canvasClientHeight: canvas ? canvas.clientHeight : 0,
                    containerWidth: container ? container.clientWidth : 0,
                    containerHeight: container ? container.clientHeight : 0,
                    canvasDisplay: canvas ? window.getComputedStyle(canvas).display : null,
                    canvasVisibility: canvas ? window.getComputedStyle(canvas).visibility : null,
                    canvasOpacity: canvas ? window.getComputedStyle(canvas).opacity : null,
                };
            })()
            """
            eval_id = await send_cmd("Runtime.evaluate", {"expression": eval_map, "returnByValue": True})
            # Wait for response
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == eval_id:
                    val = resp.get("result", {}).get("result", {}).get("value", {})
                    print("Map canvas DOM check:", json.dumps(val, indent=2))
                    break

    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(main())
