""" A set of classes used to manage the game state and display of components on screen.

Classes:
    Layer
    LayerManager
"""

from pygame import Surface, SRCALPHA, event
from source.core.component import Component


class Layer:
    """
    A layer is used to manage a group of component, to form a single "game state" or display of a scene.
    """
    def __init__(self, transparent: bool, width: int, height: int) -> None:
        """
        :param transparent: If the layer should be see-through.
        :param width: the width of the render area of the layer.
        :param height: the height of the render area of the layer.
        """
        self.transparent = transparent
        self.width = width
        self.height = height

        if transparent:
            self.surface = Surface((width, height), SRCALPHA)
            self.surface.fill((0, 0, 0, 0))
        else:
            self.surface = Surface((width, height))
            self.surface.fill((0, 0, 0))

        self.components: dict[str, Component] = {}

    def add_component(self, name: str, component: Component) -> None:
        """ Adds a component on the layer.

        :param name: The name used to reference the added component.
        :param component: The component to add.
        """
        self.components[name] = component

    def get_component(self, name: str) -> Component:
        """ Get a component present in the layer.

        :param name: The name of the component.
        """
        return self.components[name]

    def remove_component(self, name: str) -> None:
        """ Removes a component from the layer.

        :param name: The name of the component.
        """
        self.components.pop(name)

    def update(self, events: list[event.Event]) -> None:
        """ Updates the components of the layer.

        :param events: The list of events lastly pulled.
        """
        for name in self.components:
            self.components[name].update(events)

    def render(self, surface: Surface) -> None:
        """ Renders the components to a surface.

        :param surface: The surface on which every component will be rendered.
        """
        if self.transparent:
            self.surface.fill((0, 0, 0, 0))
        else:
            self.surface.fill((0, 0, 0))

        for name in self.components:
            self.components[name].render(self.surface)

        surface.blit(self.surface, (0, 0))


class LayerManager:
    """
    A layer manager is used to keep track of the different layers, update and render them in some order of priority.
    """
    def __init__(self) -> None:
        self.layers: dict[str, Layer] = {}
        self.order: list[str] = []

    def add_layer(self, name: str, layer: Layer) -> None:
        """ Adds a layer to the stack.

        :param name: The name used to reference the layer which will be added.
        :param layer: The layer that will be added.
        """
        self.layers[name] = layer
        self.order.append(name)

    def get_layer(self, name: str) -> Layer:
        """ Get a layer from the stack.

        :param name: The name of the desired layer.
        """
        return self.layers[name]

    def remove_layer(self, name: str) -> None:
        """ Removes a layer from the stack.

        :param name: The name of the layer to remove.
        """
        self.layers.pop(name)
        self.order.remove(name)

    def set_focus(self, name: str) -> None:
        """ Change the which layer is currently in focus (at the top of the stack).

        :param name: The name of the layer to set the focus to.
        """
        self.order.remove(name)
        self.order.insert(0, name)

    def get_focus(self) -> str:
        """ Get the name of the layer currently in focus (at the top of the stack).

        :return: The name of the top-level layer.
        """
        return self.order[0]

    def update(self, events: list[event.Event]) -> None:
        """ Updates the layer in focus.

        :param events: The list of events lastly pulled.
        """
        self.layers[self.order[0]].update(events)

    def render(self, surface: Surface) -> None:
        """ Renders the layer in focus, and if it is transparent, each layer under it until a non-transparent layer is
        found or there are no more layers to render.

        :param surface: The surface to which the layers will be rendered.
        """
        to_render: list[str] = []
        for name in self.order:
            to_render.insert(0, name)
            if not self.layers[name].transparent:
                break

        for name in to_render:
            self.layers[name].render(surface)
