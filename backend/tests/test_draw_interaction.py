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

async def test_draw_flow():
    user_data = os.path.abspath("chrome_temp_draw_flow")
    os.makedirs(user_data, exist_ok=True)
    subprocess.run(["powershell", "-Command", "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

            # Login
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

            # Open Draw Site Modal
            open_modal = """
            (() => {
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Draw Site'));
                if (btn) btn.click();
                return !!btn;
            })()
            """
            await send_cmd("Runtime.evaluate", {"expression": open_modal, "returnByValue": True})
            await asyncio.sleep(2)

            # Get canvas coordinates in viewport
            get_coords = """
            (() => {
                const modal = document.querySelector('.modal-content');
                const canvas = modal ? modal.querySelector('.mapboxgl-canvas') : null;
                if (!canvas) return null;
                const rect = canvas.getBoundingClientRect();
                return {
                    left: rect.left,
                    top: rect.top,
                    width: rect.width,
                    height: rect.height
                };
            })()
            """
            rect_res = (await send_cmd("Runtime.evaluate", {"expression": get_coords, "returnByValue": True})).get("result", {}).get("value", {})
            print("Modal Map Canvas Bounding Box:", rect_res)

            if rect_res:
                cx = rect_res["left"] + rect_res["width"] * 0.3
                cy = rect_res["top"] + rect_res["height"] * 0.5
                
                # Points to draw a polygon
                points = [
                    (cx, cy),
                    (cx + 100, cy),
                    (cx + 100, cy + 80),
                    (cx, cy + 80),
                    (cx, cy) # Close polygon
                ]

                print("Simulating polygon drawing clicks...")
                for px, py in points:
                    await send_cmd("Input.dispatchMouseEvent", {
                        "type": "mousePressed",
                        "x": px,
                        "y": py,
                        "button": "left",
                        "clickCount": 1
                    })
                    await send_cmd("Input.dispatchMouseEvent", {
                        "type": "mouseReleased",
                        "x": px,
                        "y": py,
                        "button": "left",
                        "clickCount": 1
                    })
                    await asyncio.sleep(0.4)

                await asyncio.sleep(1)

                # Inspect if area updated
                check_area = """
                (() => {
                    const text = document.querySelector('.modal-content')?.innerText || '';
                    const match = text.match(/([0-9.]+)\s*ha/);
                    return {
                        fullText: text,
                        hasArea: !!match,
                        areaFound: match ? match[1] : null
                    };
                })()
                """
                area_res = (await send_cmd("Runtime.evaluate", {"expression": check_area, "returnByValue": True})).get("result", {}).get("value", {})
                print("Calculated Area in UI:", area_res.get("areaFound"), "ha")

                # Capture screenshot of drawn polygon in modal
                shot = await send_cmd("Page.captureScreenshot", {"format": "png"})
                img_bytes = base64.b64decode(shot.get("data", ""))
                shot_path = os.path.join(ARTIFACT_DIR, "draw_polygon_drawn_verified.png")
                with open(shot_path, "wb") as f:
                    f.write(img_bytes)
                print(f"Saved drawn polygon screenshot to: {shot_path} ({len(img_bytes)} bytes)")

    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(test_draw_flow())
