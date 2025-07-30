import threading
import asyncio
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, VSplit, Window
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.key_binding import KeyBindings
import os
import signal

class BufferWriter:
    def __init__(self, buffer, loop):
        self.buffer = buffer
        self.loop = loop
        self.text_buffer = []
        self.lock = threading.Lock()

    def write(self, text):
        with self.lock:
            self.text_buffer.append(text)

    def flush(self):
        with self.lock:
            if self.text_buffer:
                text = ''.join(self.text_buffer)
                self.text_buffer = []
                async def _write():
                    self.buffer.cursor_position = len(self.buffer.text)
                    self.buffer.insert_text(text, move_cursor=True)
                asyncio.run_coroutine_threadsafe(_write(), self.loop)

class Muxify:
    def __init__(self, N, flush_interval=0.05):
        self.N = N
        self.flush_interval = flush_interval
        self.buffers = [Buffer() for _ in range(N)]
        self.windows = [Window(content=BufferControl(buffer=b)) for b in self.buffers]
        self.layout = Layout(VSplit(self.windows))
        
        self.loop = asyncio.new_event_loop()
        def run_loop():
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        self.tiles = [BufferWriter(b, self.loop) for b in self.buffers]
        kb = KeyBindings()
        @kb.add("c-z")
        def _(event):
            os.kill(os.getpid(), signal.SIGTSTP)
        @kb.add("c-c")
        def _(event):
            os.kill(os.getpid(), signal.SIGINT)
        self.app = Application(layout=self.layout, full_screen=True, key_bindings=kb)
        async def start_all():
            flusher_task = asyncio.create_task(self.flusher())
            await self.app.run_async()
            flusher_task.cancel()
        asyncio.run_coroutine_threadsafe(start_all(), self.loop)


    async def flusher(self):
        while True:
            for tile in self.tiles:
                tile.flush()
            await asyncio.sleep(self.flush_interval)

    def __getitem__(self, index):
        return self.tiles[index]
