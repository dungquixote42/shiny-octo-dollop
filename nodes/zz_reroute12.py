from comfy.comfy_types.node_typing import IO


class ZzReroute12:
    def __init__(self):
        pass

    CATEGORY = "reroute"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                " ": (IO.ANY,),
                "  ": (IO.ANY,),
                "   ": (IO.ANY,),
                "    ": (IO.ANY,),
                "     ": (IO.ANY,),
                "      ": (IO.ANY,),
                "       ": (IO.ANY,),
                "        ": (IO.ANY,),
                "         ": (IO.ANY,),
                "          ": (IO.ANY,),
                "           ": (IO.ANY,),
                "            ": (IO.ANY,),
            },
        }

    FUNCTION = "run"

    def run(
        self, **kwargs,
    ):
        y = ()
        for x in kwargs.values():
            y += (x,)
        return y

    RETURN_TYPES = (
        IO.ANY,
        IO.ANY,
        IO.ANY,
        IO.ANY,
        IO.ANY,
        IO.ANY,
        IO.ANY,
        IO.ANY,
        IO.ANY,
        IO.ANY,
        IO.ANY,
        IO.ANY,
    )
    RETURN_NAMES = (
        " ",
        "  ",
        "   ",
        "    ",
        "     ",
        "      ",
        "       ",
        "        ",
        "         ",
        "          ",
        "           ",
        "            ",
    )
