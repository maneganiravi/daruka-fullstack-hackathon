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

async def test_session_mock():
    user_data = os.path.abspath("chrome_temp_mock_session")
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

            # Route to test page
            await send_cmd("Page.navigate", {"url": f"{BASE_URL}/login"})
            await asyncio.sleep(1)
            
            # Setup fetch interceptor for map-sessions and auth login
            setup_script = """
            (async () => {
                const originalFetch = window.fetch;
                window.fetch = async function(...args) {
                    const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
                    if (url.includes('api.mapbox.com/map-sessions')) {
                        return new Response(JSON.stringify({ success: true, session: 'valid' }), {
                            status: 200,
                            headers: { 'Content-Type': 'application/json' }
                        });
                    }
                    return originalFetch.apply(this, args);
                };

                const res = await fetch('http://localhost:8000/api/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: 'admin@darukaa.earth', password: 'AdminPassword123!'})
                });
                const data = await res.json();
                localStorage.setItem('daruka_token', data.access_token);
                localStorage.setItem('daruka_user', JSON.stringify(data.user));
                window.location.href = '/map';
            })()
            """
            await send_cmd("Runtime.evaluate", {"expression": setup_script, "awaitPromise": True})
            await asyncio.sleep(4)

            # Check if map is loaded and tiles are rendering
            eval_map = """
            (() => {
                const map = window.__debug_map;
                if (!map) return { error: 'No debug map' };
                return {
                    isLoaded: map.loaded(),
                    isStyleLoaded: map.isStyleLoaded(),
                    layers: (map.getStyle()?.layers || []).map(l => l.id),
                    sources: Object.keys(map.getStyle()?.sources || {})
                };
            })()
            """
            eval_res = await send_cmd("Runtime.evaluate", {"expression": eval_map, "returnByValue": True})
            print("Map after mock session:", json.dumps(eval_res.get("result", {}).get("value", {}), indent=2))

    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(test_session_mock())
