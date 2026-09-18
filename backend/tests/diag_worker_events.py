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
    user_data = os.path.abspath("chrome_temp_worker_test")
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
            await send_cmd("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True})

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
                window.location.href = '/map';
            })()
            """
            await send_cmd("Runtime.evaluate", {"expression": auth_setup, "awaitPromise": True})
            
            # Listen to ALL events for 6 seconds
            end_time = time.time() + 6
            while time.time() < end_time:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=0.2)
                    msg = json.loads(raw)
                    method = msg.get("method", "")
                    if "console" in method.lower() or "exception" in method.lower():
                        print(f"[{method}]:", msg)
                    elif method == "Network.requestWillBeSent":
                        url = msg.get("params", {}).get("request", {}).get("url", "")
                        if not url.startswith("data:") and not "node_modules" in url and not "src/" in url:
                            print(f"[NET REQ]: {url}")
                    elif method == "Network.loadingFailed":
                        print(f"[NET FAILED]:", msg.get("params"))
                except asyncio.TimeoutError:
                    pass

    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(main())
