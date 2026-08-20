"""types-fix-types-not-cast: cast() performs no runtime check and checkers accept it silently."""

from typing import cast

number = cast(int, "definitely not an int")  # EXPECT-CLEAN: cast is an unchecked assertion
