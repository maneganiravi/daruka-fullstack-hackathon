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
    print("Starting Chrome...")
    user_data = os.path.abspath("chrome_temp_profile")
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
                while True:
                    resp = json.loads(await ws.recv())
                    if resp.get("id") == msg_id:
                        return resp.get("result", {})

            await send_cmd("Console.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("Network.enable")
            await send_cmd("Page.enable")

            network_entries = []
            console_entries = []

            async def listener():
                try:
                    while True:
                        raw = await ws.recv()
                        ev = json.loads(raw)
                        method = ev.get("method")
                        params = ev.get("params", {})
                        if method == "Runtime.consoleAPICalled":
                            text = " ".join([
                                str(arg.get("value", arg.get("description", "")))
                                for arg in params.get("args", [])
                            ])
                            console_entries.append(f"[{params.get('type')}] {text}")
                            print(f"[CONSOLE] [{params.get('type')}] {text}")
                        elif method == "Runtime.exceptionThrown":
                            details = params.get("exceptionDetails", {})
                            exc_desc = details.get('exception', {}).get('description')
                            print(f"[EXCEPTION] {details.get('text')} - {exc_desc}")

                        elif method == "Network.responseReceived":
                            resp = params.get("response", {})
                            url = resp.get("url", "")
                            status = resp.get("status")
                            network_entries.append((status, url))
                            if any(k in url for k in ["tile", "mapbox", "carto", "arcgis", "api"]):
                                print(f"[NET {status}] {url[:90]}")
                except Exception:
                    pass

            listen_task = asyncio.create_task(listener())

            # Navigate to login page
            await send_cmd("Page.navigate", {"url": "http://localhost:5173/login"})
            await asyncio.sleep(2)

            # Set localStorage auth token and reload directly to dashboard
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
            token_res = await send_cmd("Runtime.evaluate", {"expression": auth_setup, "awaitPromise": True})
            print(f"Token Setup: {token_res}")

            # Navigate to dashboard
            print("\nNavigating to Dashboard (http://localhost:5173/)...")
            await send_cmd("Page.navigate", {"url": "http://localhost:5173/"})
            await asyncio.sleep(6)

            # Inspect Map
            inspect_js = """
            (() => {
                const mapEl = document.querySelector('.mapboxgl-map');
                const canvas = document.querySelector('.mapboxgl-canvas');
                const sources = window.__mapbox_debug_sources || [];
                return {
                    url: window.location.href,
                    hasMap: Boolean(mapEl),
                    mapStyle: mapEl ? window.getComputedStyle(mapEl).display : null,
                    mapWidth: mapEl ? mapEl.clientWidth : 0,
                    mapHeight: mapEl ? mapEl.clientHeight : 0,
                    hasCanvas: Boolean(canvas),
                    canvasWidth: canvas ? canvas.width : 0,
                    canvasHeight: canvas ? canvas.height : 0,
                    canvasStyleWidth: canvas ? canvas.style.width : '',
                    canvasStyleHeight: canvas ? canvas.style.height : '',
                };
            })()
            """
            dash_res = await send_cmd("Runtime.evaluate", {"expression": inspect_js, "returnByValue": True})
            print(f"\nDASHBOARD MAP INSPECTION:\n{json.dumps(dash_res.get('result', {}).get('value', {}), indent=2)}")

            # Navigate to Map Explorer
            print("\nNavigating to Map Explorer (http://localhost:5173/map)...")
            await send_cmd("Page.navigate", {"url": "http://localhost:5173/map"})
            await asyncio.sleep(6)

            map_res = await send_cmd("Runtime.evaluate", {"expression": inspect_js, "returnByValue": True})
            print(f"\nMAP EXPLORER INSPECTION:\n{json.dumps(map_res.get('result', {}).get('value', {}), indent=2)}")

            listen_task.cancel()

    finally:
        proc.kill()


if __name__ == "__main__":
    asyncio.run(main())
