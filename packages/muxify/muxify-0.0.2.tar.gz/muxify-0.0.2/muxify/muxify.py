import asyncio
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, VSplit, Window
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl

class BufferWriter:
    def __init__(self, buffer, loop):
        self.buffer = buffer
        self.loop = loop

    def write(self, text):
        def _write():
            self.buffer.cursor_position = len(self.buffer.text)
            self.buffer.insert_text(text, move_cursor=True)
        self.loop.call_soon_threadsafe(_write)

    def flush(self):
        pass

class Muxify:
    def __init__(self, N):
        self.N = N
        self.buffers = [Buffer() for _ in range(N)]
        self.windows = [Window(content=BufferControl(buffer=b)) for b in self.buffers]
        self.layout = Layout(VSplit(self.windows))
        self.app = Application(layout=self.layout, full_screen=True)
        self.tiles = [BufferWriter(b) for b in self.buffers]
        self.task = asyncio.create_task(self.app.run_async())
    
    def __getitem__(self, index):
        return self.tiles[index]


mux = Muxify(2)

async def update_tiles():
    for i in range(500):
        if i % 5 == 0:
            print(f"Update {i} to tile0", file=mux[0])
        print(f"Update {i} to tile1", file=mux[1])
        await asyncio.sleep(0.1)

async def main():
    await update_tiles()

if __name__ == "__main__":
    asyncio.run(main())
