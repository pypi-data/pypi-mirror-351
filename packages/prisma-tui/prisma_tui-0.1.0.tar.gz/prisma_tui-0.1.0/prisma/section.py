import prisma

# //////////////////////////////////////////////////////////////////////////////
class Section:
    def __init__(self):
        self._parent: "Section" = None

        self.h: int; self.w: int
        self.y: int; self.x: int
        self.hrel: int|float = 1.0
        self.wrel: int|float = 1.0
        self.yrel: int|float = 0
        self.xrel: int|float = 0
        self._update_dimensions()

        self._children: list["Section"] = []
        self._layers = [prisma.Layer(self.h, self.w)]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_parent(self, parent: "Section") -> None:
        self._parent = parent
        parent._children.append(self)
        self._update_dimensions()

    # --------------------------------------------------------------------------
    def create_child(self,
        hrel: int|float, wrel: int|float,
        yrel: int|float, xrel: int|float
    ) -> "Section":
        child = Section()
        child.hrel = hrel
        child.wrel = wrel
        child.yrel = yrel
        child.xrel = xrel
        child.set_parent(self)
        return child

    # --------------------------------------------------------------------------
    def create_layer(self) -> prisma.Layer:
        layer = prisma.Layer(self.h, self.w)
        self._layers.append(layer)
        return layer

    # --------------------------------------------------------------------------
    def create_mosaic(self, layout: str, divider = '\n') -> dict:
        section_dict = {}
        for char, hwyx in prisma.utils.mosaic(layout, divider).items():
            section = self.create_child(*hwyx)
            section_dict[char] = section
        return section_dict


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def get_size(self) -> tuple[int, int]:
        return self.h, self.w

    # --------------------------------------------------------------------------
    def get_position(self) -> tuple[int, int]:
        return self.y, self.x

    # --------------------------------------------------------------------------
    def get_bottom_layer(self) -> prisma.Layer:
        return self._layers[0]

    # --------------------------------------------------------------------------
    def get_top_layer(self) -> prisma.Layer:
        return self._layers[-1]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def iter_children(self):
        return iter(self._children)

    # --------------------------------------------------------------------------
    def iter_layers(self):
        return iter(self._layers)

    # --------------------------------------------------------------------------
    def clear(self) -> None:
        for layer in self.iter_layers():
            layer.clear()

        for child in self.iter_children():
            child.clear()

    # --------------------------------------------------------------------------
    def aggregate_layers(self, agg_layer: prisma.Layer) -> None:
        for layer in self.iter_layers():
            agg_layer.draw_layer(self.y, self.x, layer)

        for child in self.iter_children():
            child.aggregate_layers(agg_layer)

    # --------------------------------------------------------------------------
    def update_size(self) -> None:
        self._update_dimensions()

        for layer in self.iter_layers():
            layer.set_size(self.h, self.w)

        for child in self.iter_children():
            child.update_size()


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def draw_text(self, *args, **kwds):
        self.get_top_layer().draw_text(*args, **kwds)

    # --------------------------------------------------------------------------
    def draw_layer(self, *args, **kwds):
        self.get_top_layer().draw_layer(*args, **kwds)

    # --------------------------------------------------------------------------
    def draw_border(self, *args, **kwds):
        self.get_top_layer().draw_border(*args, **kwds)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _update_dimensions(self) -> None:
        if self._parent is None: # root section
            self.h, self.w = prisma._BACKEND.get_size()
            self.y, self.x = 0, 0
            return

        h = self.hrel; w = self.wrel
        y = self.yrel; x = self.xrel

        if isinstance(h, float):
            self.h = round(h * self._parent.h)
        elif isinstance(h, int):
            if h < 0: h += self._parent.h
            self.h = min(h, self._parent.h)

        if isinstance(w, float):
            self.w = round(w * self._parent.w)
        elif isinstance(w, int):
            if w < 0: w += self._parent.w
            self.w = min(w, self._parent.w)

        if isinstance(y, float):
            self.y = self._parent.y + round(y * self._parent.h)
        elif isinstance(y, int):
            if y < 0: y += self._parent.h
            self.y = y + self._parent.y

        if isinstance(x, float):
            self.x = self._parent.x + round(x * self._parent.w)
        elif isinstance(x, int):
            if x < 0: x += self._parent.w
            self.x = x + self._parent.x

        y_outbounds = (self.y + self.h) - (self._parent.y + self._parent.h)
        x_outbounds = (self.x + self.w) - (self._parent.x + self._parent.w)

        if y_outbounds > 0: self.y -= y_outbounds
        if x_outbounds > 0: self.x -= x_outbounds


# //////////////////////////////////////////////////////////////////////////////
