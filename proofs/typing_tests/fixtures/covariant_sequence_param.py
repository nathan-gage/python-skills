"""types-sequence-over-list-params: Sequence[Base] accepts list[Subtype] — covariant read-only view."""

from collections.abc import Sequence


class Widget:
    pass


class Button(Widget):
    pass


def render_all(widgets: Sequence[Widget]) -> None:
    del widgets


buttons: list[Button] = [Button()]
render_all(buttons)  # EXPECT-CLEAN: Sequence is covariant
