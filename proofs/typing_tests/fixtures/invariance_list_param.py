"""types-sequence-over-list-params: a list[Subtype] must be rejected where list[Base] is expected."""


class Widget:
    pass


class Button(Widget):
    pass


def render_all(widgets: list[Widget]) -> None:
    del widgets


buttons: list[Button] = [Button()]
render_all(buttons)  # EXPECT-ERROR: list is invariant
