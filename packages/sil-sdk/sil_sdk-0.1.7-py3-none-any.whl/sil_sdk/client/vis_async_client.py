import asyncio
import json
import websockets

class VISAsyncClient:
    def __init__(self, server_uri="ws://localhost:4201"):
        self.server_uri = server_uri
        self.websocket = None
        self.response_queue = None
        self.module_results = {}

    async def connect(self):
        self.websocket = await websockets.connect(self.server_uri)
        self.response_queue = asyncio.Queue()
        asyncio.create_task(self._listen())

    async def _listen(self):
        async for message in self.websocket:
            data = json.loads(message)
            module = data.get("module")
            if module:
                self.module_results[module] = data
            await self.response_queue.put(data)

    async def load_module(self, module: str):
        await self.websocket.send(json.dumps({"command": f"{module}_load"}))
        return await self.response_queue.get()

    async def run_module(self, module, *, prompt=None, bbox=None, mask=None, image=None):
        cmd = {"command": f"{module}_run"}
        if prompt: cmd["prompt"] = prompt
        if bbox: cmd["bbox"] = bbox
        if mask: cmd["mask"] = mask
        if image: cmd["image"] = image

        await self.websocket.send(json.dumps(cmd))
        first_resp = await self.response_queue.get()
        if first_resp.get("status") == "error":
            return first_resp
        return await self.response_queue.get()

    async def stop_module(self, module: str):
        await self.websocket.send(json.dumps({"command": f"{module}_stop"}))
        return await self.response_queue.get()

    async def close(self):
        await self.websocket.close()
