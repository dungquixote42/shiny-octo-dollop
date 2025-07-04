import os
import sys
from pathlib import Path

import comfy.controlnet
import comfy.utils
import torch
from comfy.comfy_types.node_typing import IO

from .include.config import MAX_RESOLUTION

comfyui_path = Path(
    os.path.join(os.path.dirname(os.path.realpath(__file__)))
).parent.parent.parent
sys.path.insert(0, str(comfyui_path.absolute()))


class ApplyControlNetBig:
    def __init__(self):
        pass

    CATEGORY = "conditioning/controlnet"

    upscale_methods = [
        "disabled",
        "nearest-exact",
        "bilinear",
        "area",
        "bicubic",
        "lanczos",
    ]
    crop_methods = ["disabled", "center"]

    def upscale(self, image: torch.Tensor, upscale_method, width, height, crop):
        if width == 0 and height == 0:
            s = image
        else:
            samples = image.movedim(-1, 1)

            if width == 0:
                width = max(1, round(samples.shape[3] * height / samples.shape[2]))
            elif height == 0:
                height = max(1, round(samples.shape[2] * width / samples.shape[3]))

            s = comfy.utils.common_upscale(samples, width, height, upscale_method, crop)
            s = s.movedim(1, -1)
        return s

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "control_net_union": (IO.CONTROL_NET,),
                "base_image": (IO.IMAGE,),
                "dimension": (
                    IO.INT,
                    {"forceInput": True},
                ),
                "positive": (IO.CONDITIONING,),
                "negative": (IO.CONDITIONING,),
                "control_net": (IO.CONTROL_NET,),
                "image": (IO.IMAGE,),
                "target_width": (
                    IO.INT,
                    {"forceInput": True},
                ),
                "target_height": (
                    IO.INT,
                    {"forceInput": True},
                ),
                "upscale_method": (s.upscale_methods,),
                "crop": (s.crop_methods,),
                "strength": (
                    IO.FLOAT,
                    {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01},
                ),
                "start_percent": (
                    IO.FLOAT,
                    {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
                "end_percent": (
                    IO.FLOAT,
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001},
                ),
            },
            "optional": {
                "vae": (IO.VAE,),
            },
        }

    FUNCTION = "run"

    def run(
        self,
        control_net_union,
        base_image,
        dimension,
        positive,
        negative,
        control_net,
        image: torch.Tensor,
        target_width,
        target_height,
        upscale_method,
        crop,
        strength,
        start_percent,
        end_percent,
        vae=None,
        extra_concat=[],
    ):
        if strength == 0:
            return (positive, negative)
        if upscale_method != "disabled":
            image = self.upscale(
                image, upscale_method, target_width, target_height, crop
            )

        control_hint = image.movedim(-1, 1)
        cnets = {}

        out = []
        for conditioning in [positive, negative]:
            c = []
            for t in conditioning:
                t1: dict = t[1]
                d: dict = t1.copy()

                prev_cnet = d.get("control", None)
                if prev_cnet in cnets:
                    c_net = cnets[prev_cnet]
                else:
                    control_net: comfy.controlnet.ControlNet = control_net
                    c_net = control_net.copy().set_cond_hint(
                        control_hint,
                        strength,
                        (start_percent, end_percent),
                        vae=vae,
                        extra_concat=extra_concat,
                    )
                    c_net.set_previous_controlnet(prev_cnet)
                    cnets[prev_cnet] = c_net

                d["control"] = c_net
                d["control_apply_to_uncond"] = False
                n = [t[0], d]
                c.append(n)
            out.append(c)
        return (
            control_net_union,
            base_image,
            dimension,
            out[0],
            out[1],
            image,
            target_width,
            target_height,
            vae,
        )

    RETURN_TYPES = (
        IO.CONTROL_NET,
        IO.IMAGE,
        IO.INT,
        IO.CONDITIONING,
        IO.CONDITIONING,
        IO.IMAGE,
        IO.INT,
        IO.INT,
        IO.VAE,
    )
    RETURN_NAMES = (
        "control_net_union",
        "base_image",
        "dimension",
        "positive",
        "negative",
        "image",
        "target_width",
        "target_height",
        "vae",
    )


if __name__ == "__main__":
    test = ApplyControlNetBig()
    print("goodbye")
