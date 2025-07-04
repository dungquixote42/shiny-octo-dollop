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


class ZzippedApplyControlNet:
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
                "control_net": (IO.CONTROL_NET,),
                "image": (IO.IMAGE,),
                "latent_width": (
                    IO.INT,
                    {"default": 1024, "min": 0, "max": MAX_RESOLUTION},
                ),
                "latent_height": (
                    IO.INT,
                    {"default": 1024, "min": 0, "max": MAX_RESOLUTION},
                ),
                "positive": (IO.CONDITIONING,),
                "negative": (IO.CONDITIONING,),
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
                "control_net_union": (IO.CONTROL_NET,),
                "vae": (IO.VAE,),
            },
        }

    FUNCTION = "run"

    def run(
        self,
        control_net,
        image: torch.Tensor,
        latent_width,
        latent_height,
        positive,
        negative,
        upscale_method,
        crop,
        strength,
        start_percent,
        end_percent,
        control_net_union,
        vae=None,
        extra_concat=[],
    ):
        if strength == 0:
            return (positive, negative)
        if upscale_method != "disabled":
            image = self.upscale(
                image, upscale_method, latent_width, latent_height, crop
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
            image,
            latent_width,
            latent_height,
            out[0],
            out[1],
            control_net_union,
            vae,
        )

    RETURN_TYPES = (
        IO.IMAGE,
        IO.INT,
        IO.INT,
        IO.CONDITIONING,
        IO.CONDITIONING,
        IO.CONTROL_NET,
        IO.VAE,
    )
    RETURN_NAMES = (
        "image",
        "latent_width",
        "latent_height",
        "positive",
        "negative",
        "control_net_union",
        "vae",
    )


if __name__ == "__main__":
    test = ZzippedApplyControlNet()
    print("goodbye")
