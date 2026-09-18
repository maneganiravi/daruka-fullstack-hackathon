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
    user_data = os.path.abspath("chrome_temp_diag_mapbox")
    os.makedirs(user_data, exist_ok=True)
    subprocess.run(["powershell", "-Command", "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={user_data}",
        "--headless=new",
        "--use-gl=angle",
        "--use-angle=swiftshader",
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

            # Setup login
            await send_cmd("Page.navigate", {"url": f"{BASE_URL}/login"})
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
                window.location.href = '/';
            })()
            """
            await send_cmd("Runtime.evaluate", {"expression": auth_setup, "awaitPromise": True})
            await asyncio.sleep(4)

            # Debug Mapbox instance state
            debug_script = """
            (() => {
                const map = window.__debug_map;
                if (!map) return { error: "window.__debug_map not found" };
                
                const style = map.getStyle();
                const isLoaded = map.loaded();
                const isStyleLoaded = map.isStyleLoaded();
                const areTilesLoaded = map.areTilesLoaded ? map.areTilesLoaded() : null;
                const center = map.getCenter();
                const zoom = map.getZoom();
                const bounds = map.getBounds();
                const canvas = map.getCanvas();
                const gl = canvas.getContext('webgl') || canvas.getContext('webgl2');
                
                return {
                    isLoaded,
                    isStyleLoaded,
                    areTilesLoaded,
                    center: [center.lng, center.lat],
                    zoom,
                    bounds: bounds ? [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()] : null,
                    styleSources: style ? Object.keys(style.sources || {}) : null,
                    styleLayers: style ? (style.layers || []).map(l => ({ id: l.id, type: l.type, source: l.source, visible: l.layout?.visibility || 'visible' })) : null,
                    canvas: {
                        width: canvas.width,
                        height: canvas.height,
                        clientWidth: canvas.clientWidth,
                        clientHeight: canvas.clientHeight,
                        glRenderer: gl ? gl.getParameter(gl.RENDERER) : null,
                        glVendor: gl ? gl.getParameter(gl.VENDOR) : null,
                    }
                };
            })()
            """
            eval_res = await send_cmd("Runtime.evaluate", {"expression": debug_script, "returnByValue": True})
            map_status = eval_res.get("result", {}).get("value", {})
            print("MAPBOX DEBUG STATE:\n", json.dumps(map_status, indent=2))

            # Check network requests for tiles
            print("\nListening for network requests...")
            end_time = time.time() + 5
            tile_reqs = []
            while time.time() < end_time:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    msg = json.loads(raw)
                    if msg.get("method") == "Network.requestWillBeSent":
                        url = msg.get("params", {}).get("request", {}).get("url", "")
                        if "arcgis" in url or "carto" in url or "tile" in url or "mapbox" in url:
                            tile_reqs.append(url)
                            print(f"[REQ]: {url}")
                    elif msg.get("method") == "Network.responseReceived":
                        url = msg.get("params", {}).get("response", {}).get("url", "")
                        status = msg.get("params", {}).get("response", {}).get("status", "")
                        if "arcgis" in url or "carto" in url or "tile" in url or "mapbox" in url:
                            print(f"[RESP {status}]: {url}")
                except asyncio.TimeoutError:
                    pass

            print(f"Total tile requests observed: {len(tile_reqs)}")

    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(main())
