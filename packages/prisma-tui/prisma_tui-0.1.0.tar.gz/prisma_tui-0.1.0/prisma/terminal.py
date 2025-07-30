import prisma

# //////////////////////////////////////////////////////////////////////////////
class Terminal:
    def __init__(self):
        self.h: int = 0
        self.w: int = 0
        self.key: int = -1
        self.root: prisma.Section
        self.graphics: prisma.Graphics

        self._no_delay: bool = False
        self._nap_ms: int = 0
        self._wait = lambda: None
        self._running: bool = False


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def run(self, fps: int = 0) -> None:
        self.set_fps(fps)
        try:
            prisma._BACKEND._start()
            self._on_start()
            while self._running:
                self._on_resize()
                self._on_update()
            self._on_end()
        finally:
            prisma._BACKEND._end()

    # --------------------------------------------------------------------------
    def stop(self) -> None:
        self._running = False

    # --------------------------------------------------------------------------
    def fetch_key(self) -> int:
        self.key = prisma._BACKEND._get_key()
        return self.key

    # --------------------------------------------------------------------------
    def exhaust_keys(self) -> None:
        """
        Attention: calling to fetch_key()->prisma._BACKEND._get_key() internally rellies on stdscr.getch(),
        so this method will block the terminal when fps=0 (i.e. outside no-delay mode).
        """
        while self.fetch_key() != -1:
            pass


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_fps(self, fps: int) -> None:
        if not fps:
            self._no_delay = False
            self._nap_ms = 0
            self._wait = lambda: None
        else:
            self._no_delay = True
            self._nap_ms = int(1000 / fps)
            self._wait = lambda: prisma._BACKEND.sleep(self._nap_ms)

    # --------------------------------------------------------------------------
    def get_size(self) -> tuple[int, int]:
        return self.h, self.w

    # --------------------------------------------------------------------------
    def resize_terminal(self, h: int, w: int) -> None:
        print(f"\x1b[8;{h};{w}t")

    # --------------------------------------------------------------------------
    def draw_text(self, *args, **kws) -> None:
        self.root.draw_text(*args, **kws)

    # --------------------------------------------------------------------------
    def draw_layer(self, *args, **kws) -> None:
        self.root.draw_layer(*args, **kws)

    # --------------------------------------------------------------------------
    def draw_border(self, *args, **kwds) -> None:
        self.root.draw_border(*args, **kwds)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def on_start(self) -> None:
        return # overridden by user

    # --------------------------------------------------------------------------
    def on_resize(self) -> None:
        return # overridden by user

    # --------------------------------------------------------------------------
    def on_update(self) -> None:
        return # overridden by user

    # --------------------------------------------------------------------------
    def on_end(self) -> None:
        return # overridden by user

    # --------------------------------------------------------------------------
    def should_stop(self) -> bool:
        return False # overridden by user


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _on_start(self) -> None:
        self.root = prisma.Section()
        self.graphics = prisma.Graphics()
        prisma._BACKEND.set_nodelay(self._no_delay)

        self._running = True
        self.on_start()

    # --------------------------------------------------------------------------
    def _on_resize(self) -> None:
        h,w = prisma._BACKEND.get_size(update = True)

        if (self.h == h) and (self.w == w): return

        self.h = h; self.w = w
        self.root.update_size()
        prisma._BACKEND._resize(self.h, self.w)
        self.on_resize()

    # --------------------------------------------------------------------------
    def _on_update(self) -> None:
        self.root.clear()
        self.on_update()
        self._render()

        self.key = prisma._BACKEND._get_key()
        if self.should_stop(): self.stop()
        self._wait()

    # --------------------------------------------------------------------------
    def _on_end(self) -> None:
        self.on_end()


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _render(self) -> None:
        master_layer = prisma.Layer(self.h, self.w)
        self.root.aggregate_layers(master_layer)

        idx = 0
        for chars,attr in master_layer.yield_render_data():
            y,x = divmod(idx, self.w)
            prisma._BACKEND.write_text(y, x, chars, attr)
            idx += len(chars)

        prisma._BACKEND._refresh()


# //////////////////////////////////////////////////////////////////////////////
