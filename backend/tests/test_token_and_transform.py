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


async def test_mapbox_in_browser(token, intercept_sessions=False):
    user_data = os.path.abspath("chrome_temp_test_token")
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

            # Route to test page
            await send_cmd("Page.navigate", {"url": f"{BASE_URL}/login"})
            await asyncio.sleep(1)

            # Login and inject token
            auth_script = f"""
            (async () => {{
                const res = await fetch('http://localhost:8000/api/auth/login', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{email: 'admin@darukaa.earth', password: 'AdminPassword123!'}})
                }});
                const data = await res.json();
                localStorage.setItem('daruka_token', data.access_token);
                localStorage.setItem('daruka_user', JSON.stringify(data.user));
                window.location.href = '/map';
            }})()
            """
            await send_cmd("Runtime.evaluate", {"expression": auth_script, "awaitPromise": True})
            await asyncio.sleep(4)

            # Test evaluate canvas pixel data
            eval_canvas = """
            (() => {
                const canvas = document.querySelector('.mapboxgl-canvas');
                if (!canvas) return { error: 'No canvas' };
                const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
                if (!gl) return { error: 'No WebGL context' };

                const pixels = new Uint8Array(4 * 10 * 10);
                gl.readPixels(100, 100, 10, 10, gl.RGBA, gl.UNSIGNED_BYTE, pixels);

                let nonZero = 0;
                for (let i = 0; i < pixels.length; i += 4) {
                    const r = pixels[i], g = pixels[i+1], b = pixels[i+2], a = pixels[i+3];
                    if (r > 0 || g > 0 || b > 0) nonZero++;
                }
                return {
                    width: canvas.width,
                    height: canvas.height,
                    nonZeroPixels: nonZero,
                    sample: Array.from(pixels.slice(0, 16))
                };
            })()
            """
            res = (await send_cmd("Runtime.evaluate", {"expression": eval_canvas, "returnByValue": True})).get("result", {}).get("value", {})
            print("Canvas Pixel Inspection:", res)

    finally:
        proc.kill()


if __name__ == "__main__":
    asyncio.run(test_mapbox_in_browser(""))
