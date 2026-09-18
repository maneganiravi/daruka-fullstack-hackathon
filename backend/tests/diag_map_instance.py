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
            
            await send_cmd("Page.enable")
            await send_cmd("Runtime.enable")
            await send_cmd("Network.enable")
            
            # Setup session
            await send_cmd("Page.navigate", {"url": "http://localhost:5173/login"})
            await asyncio.sleep(2)
            
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
            await send_cmd("Page.navigate", {"url": "http://localhost:5173/"})
            await asyncio.sleep(4)
            
            # Deep Mapbox instance inspection
            inspect_js = """
            (() => {
                try {
                    const map = window.__debug_map;
                    if (!map) return { hasMapInstance: false };
                    
                    const style = map.getStyle ? map.getStyle() : null;
                    const layers = style ? (style.layers || []) : [];
                    const sources = style ? (style.sources || {}) : {};
                    
                    return {
                        hasMapInstance: true,
                        isStyleLoaded: map.isStyleLoaded(),
                        areTilesLoaded: map.areTilesLoaded(),
                        loaded: map.loaded(),
                        center: map.getCenter(),
                        zoom: map.getZoom(),
                        bounds: map.getBounds(),
                        styleName: style ? style.name : null,
                        sourcesKeys: Object.keys(sources),
                        layersIds: layers.map(l => ({ id: l.id, type: l.type, source: l.source })),
                    };
                } catch (e) {
                    return { error: e.message, stack: e.stack };
                }
            })()
            """
            map_data = await send_cmd("Runtime.evaluate", {"expression": inspect_js, "returnByValue": True})
            print(f"MAP INSTANCE INSPECTION:\n{json.dumps(map_data.get('result', {}).get('value', {}), indent=2)}")
            
    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(main())
