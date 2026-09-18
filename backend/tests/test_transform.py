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


async def test_transform():
    user_data = os.path.abspath("chrome_temp_transform_test")
    os.makedirs(user_data, exist_ok=True)
    ps_cmd = [
        "powershell", "-Command",
        "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force"
    ]
    subprocess.run(ps_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
            await send_cmd("Network.enable")

            await send_cmd("Page.navigate", {"url": f"{BASE_URL}/login"})
            await asyncio.sleep(1)

            # Test creating Mapbox with transformRequest
            eval_script = """
            (async () => {
                const mapDiv = document.createElement('div');
                mapDiv.id = 'test-map-container';
                mapDiv.style.width = '600px';
                mapDiv.style.height = '400px';
                document.body.appendChild(mapDiv);

                const map = new window.mapboxgl.Map({
                    container: 'test-map-container',
                    style: {
                        version: 8,
                        sources: {
                            'esri': {
                                type: 'raster',
                                tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
                                tileSize: 256
                            }
                        },
                        layers: [
                            {
                                id: 'esri-layer',
                                type: 'raster',
                                source: 'esri'
                            }
                        ]
                    },
                    center: [78.96, 20.59],
                    zoom: 4,
                    transformRequest: (url, resourceType) => {
                        if (url.includes('api.mapbox.com/map-sessions') || url.includes('events.mapbox.com')) {
                            return { url: 'data:application/json;base64,e30=' };
                        }
                        return { url };
                    }
                });

                return new Promise((resolve) => {
                    map.on('render', () => {
                        resolve({ rendered: true, isLoaded: map.loaded(), isStyleLoaded: map.isStyleLoaded() });
                    });
                    setTimeout(() => {
                        resolve({ rendered: false, isLoaded: map.loaded(), isStyleLoaded: map.isStyleLoaded() });
                    }, 3000);
                });
            })()
            """
            eval_res = await send_cmd("Runtime.evaluate", {"expression": eval_script, "awaitPromise": True, "returnByValue": True})
            print("TransformRequest Mapbox Test:", json.dumps(eval_res.get("result", {}).get("value", {}), indent=2))

    finally:
        proc.kill()


if __name__ == "__main__":
    asyncio.run(test_transform())
