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
ARTIFACT_DIR = r"C:\Users\M.Ravi kumar\.gemini\antigravity-ide\brain\256b716e-d3e4-4ffd-975e-94ed31bca9f0"


async def main():
    user_data = os.path.abspath("chrome_temp_profile")
    os.makedirs(user_data, exist_ok=True)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

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
            await send_cmd("Network.enable")

            # 1. Login
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

            # 2. Go to Dashboard
            print("Capturing Dashboard...")
            await send_cmd("Page.navigate", {"url": "http://localhost:5173/"})
            await asyncio.sleep(5)

            dash_screenshot = await send_cmd("Page.captureScreenshot", {"format": "png"})
            dash_bytes = base64.b64decode(dash_screenshot.get("data", ""))
            dash_path = os.path.join(ARTIFACT_DIR, "dashboard_verified.png")
            with open(dash_path, "wb") as f:
                f.write(dash_bytes)
            print(f"Saved dashboard screenshot to: {dash_path} ({len(dash_bytes)} bytes)")

            # 3. Go to GIS Map Explorer
            print("Capturing Map Explorer...")
            await send_cmd("Page.navigate", {"url": "http://localhost:5173/map"})
            await asyncio.sleep(5)

            map_screenshot = await send_cmd("Page.captureScreenshot", {"format": "png"})
            map_bytes = base64.b64decode(map_screenshot.get("data", ""))
            map_path = os.path.join(ARTIFACT_DIR, "map_explorer_verified.png")
            with open(map_path, "wb") as f:
                f.write(map_bytes)
            print(f"Saved map explorer screenshot to: {map_path} ({len(map_bytes)} bytes)")

            # Test clicking polygon on map explorer
            click_poly = """
            (() => {
                const item = document.querySelector('.glass-card');
                if (item) {
                    item.click();
                    return 'Clicked site item in sidebar';
                }
                return 'No site item found';
            })()
            """
            click_res = await send_cmd("Runtime.evaluate", {"expression": click_poly, "returnByValue": True})
            print(f"Site Click Result: {click_res.get('result', {}).get('value')}")
            await asyncio.sleep(2)

            # Test clicking Draw Site button
            click_draw = """
            (() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const drawBtn = btns.find(b => b.textContent.includes('Draw Site'));
                if (drawBtn) {
                    drawBtn.click();
                    return 'Clicked Draw Site button';
                }
                return 'Draw Site button not found';
            })()
            """
            draw_res = await send_cmd("Runtime.evaluate", {"expression": click_draw, "returnByValue": True})
            print(f"Draw Site Result: {draw_res.get('result', {}).get('value')}")
            await asyncio.sleep(2)

            drawer_screenshot = await send_cmd("Page.captureScreenshot", {"format": "png"})
            drawer_bytes = base64.b64decode(drawer_screenshot.get("data", ""))
            drawer_path = os.path.join(ARTIFACT_DIR, "draw_site_modal_verified.png")
            with open(drawer_path, "wb") as f:
                f.write(drawer_bytes)
            print(f"Saved draw site modal screenshot to: {drawer_path} ({len(drawer_bytes)} bytes)")

    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(main())
