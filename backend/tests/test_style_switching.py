import asyncio
import base64
import json
import os
import subprocess
import time
import httpx
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9222
BASE_URL = "http://localhost:5173"
ARTIFACT_DIR = r"C:\Users\M.Ravi kumar\.gemini\antigravity-ide\brain\256b716e-d3e4-4ffd-975e-94ed31bca9f0"


async def test_styles():
    user_data = os.path.abspath("chrome_temp_styles")
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

        async with websockets.connect(ws_url, max_size=20 * 1024 * 1024) as ws:
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

            # Login & Navigate to Map Explorer
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
                window.location.href = '/map';
            })()
            """
            await send_cmd("Runtime.evaluate", {"expression": auth_setup, "awaitPromise": True})
            await asyncio.sleep(3)

            # Click Dark Vector style
            print("Switching to Dark Vector style...")
            click_dark = """
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Dark Vector'));
                if (btn) btn.click();
                return !!btn;
            })()
            """
            await send_cmd("Runtime.evaluate", {"expression": click_dark})
            await asyncio.sleep(3)

            # Capture Dark Vector screenshot
            shot = await send_cmd("Page.captureScreenshot", {"format": "png"})
            dark_bytes = base64.b64decode(shot.get("data", ""))
            dark_path = os.path.join(ARTIFACT_DIR, "dark_vector_verified.png")
            with open(dark_path, "wb") as f:
                f.write(dark_bytes)
            print(f"Saved Dark Vector screenshot to: {dark_path} ({len(dark_bytes)} bytes)")

            # Click Terrain style
            print("Switching to Terrain style...")
            click_terrain = """
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Terrain'));
                if (btn) btn.click();
                return !!btn;
            })()
            """
            await send_cmd("Runtime.evaluate", {"expression": click_terrain})
            await asyncio.sleep(3)

            # Capture Terrain screenshot
            shot_t = await send_cmd("Page.captureScreenshot", {"format": "png"})
            t_bytes = base64.b64decode(shot_t.get("data", ""))
            t_path = os.path.join(ARTIFACT_DIR, "terrain_verified.png")
            with open(t_path, "wb") as f:
                f.write(t_bytes)
            print(f"Saved Terrain screenshot to: {t_path} ({len(t_bytes)} bytes)")

    finally:
        proc.kill()


if __name__ == "__main__":
    asyncio.run(test_styles())
