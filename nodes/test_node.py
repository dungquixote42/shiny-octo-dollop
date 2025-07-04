from .include.keywords import *


class TestNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input0_name": (IMG_T),
                "input1_name": (
                    INT_T,
                    {
                        "default": 0,
                        "min": 0,
                        "max": 4096,
                        "step": 64,
                        "display": NUM_D,
                    },
                ),
                "input2_name": (
                    FLT_T,
                    {
                        "default": 1.0,
                        "min": 0,
                        "max": 10.0,
                        "step": 0.01,
                        "round": 0.001,  # same as step unless specified
                        "display": NUM_D,
                    },
                ),
                "input3_name": (
                    [
                        "enable",
                        "disable",
                    ],
                ),
                "input4_name": (
                    STR_T,
                    {
                        "multiline": False,
                        "default": "Hello World!",  # <"forceInput": True> to diable manual input
                    },
                ),
            }
        }

    def run(
        self,
        input0,
        input1,
        input2,
        input3,
        input4,
    ):
        return 1.0 - input0

    FUNCTION = "run"

    RETURN_TYPES = (IMG_T,)
    RETURN_NAMES = ("output_name",)

    # OUTPUT_NODE = False

    CATEGORY = "shiny-octo-dollop"
