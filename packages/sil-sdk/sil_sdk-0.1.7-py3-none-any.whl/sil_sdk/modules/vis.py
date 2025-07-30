import asyncio
from threading import Thread
from sil_sdk.client.vis_async_client import VISAsyncClient

MODULES_WITHOUT_LOAD = {}  # All modules now require loading

MODULE_ALIAS = {
    "hum_pose": "hum_pose_detection",
    "hand_pose": "hand_pose_detection",
    "gdino": "gdino_inference",
    "llava": "llava_inference" 
}

class VISModule:
    def __init__(self, server_uri="ws://localhost:50004", start_server=False):
        self.loop = asyncio.new_event_loop()
        Thread(target=self._start_loop, daemon=True).start()
        self.client = VISAsyncClient(server_uri)
        self._run(self.client.connect())

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _run(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result()

    def load(self, modules):
        if isinstance(modules, str):
            modules = [modules]
        for m in modules:
            if m not in MODULES_WITHOUT_LOAD:
                self._run(self.client.load_module(m))

    def run(self, module, *, prompt=None, bbox=None, mask=None, image=None):
        self._run(self.client.run_module(module, prompt=prompt, bbox=bbox, mask=mask, image=image))

    def stop_module(self, module):
        self._run(self.client.stop_module(module))

    def get_result(self, module):
        actual = MODULE_ALIAS.get(module, module)
        return self.client.module_results.get(actual)
    

    def close(self):
        self._run(self.client.close())
        self.loop.call_soon_threadsafe(self.loop.stop)