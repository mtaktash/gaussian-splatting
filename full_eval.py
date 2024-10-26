#
# Copyright (C) 2023, Inria
# GRAPHDECO research group, https://team.inria.fr/graphdeco
# All rights reserved.
#
# This software is free for non-commercial, research and evaluation use
# under the terms of the LICENSE.md file.
#
# For inquiries contact  george.drettakis@inria.fr
#

import os
import time
from argparse import ArgumentParser

mipnerf360_outdoor_scenes = ["garden"]
mipnerf360_indoor_scenes = ["room"]
scannetpp_scenes = [
    "2e74812d00",
    "0a7cc12c0e",
    "0a76e06478",
    "0cf2e9402d",
    "0e75f3c4d9",
    "1ae9e5d2a6",
    "1b75758486",
    "1c4b893630",
    "4c5c60fa76",
    "4ea827f5a1",
    "6b40d1a939",
    "5748ce6f01",
    "7079b59642",
]
blender_scenes = ["textured_plane_with_cube"]

parser = ArgumentParser(description="Full evaluation script parameters")
parser.add_argument("--skip_training", action="store_true")
parser.add_argument("--skip_rendering", action="store_true")
parser.add_argument("--skip_metrics", action="store_true")
parser.add_argument("--output_path", default="./eval")
args, _ = parser.parse_known_args()

all_scenes = []
all_scenes.extend(mipnerf360_outdoor_scenes)
all_scenes.extend(mipnerf360_indoor_scenes)
all_scenes.extend(scannetpp_scenes)

if not args.skip_training or not args.skip_rendering:
    parser.add_argument("--mipnerf360", "-m360", type=str, required=True)
    parser.add_argument("--scannetpp", "-spp", type=str, required=True)
    parser.add_argument("--blender", "-blen", type=str, required=True)
    args = parser.parse_args()

if not args.skip_training:
    os.makedirs(args.output_path, exist_ok=True)
    common_args = " --quiet --eval --test_iterations -1 --ip 127.0.0.20"

    start_time = time.time()
    for scene in mipnerf360_outdoor_scenes:
        source = args.mipnerf360 + "/" + scene
        os.system(
            "python train.py -s "
            + source
            + " -i images_4 -m "
            + args.output_path
            + "/"
            + scene
            + common_args
        )
    for scene in mipnerf360_indoor_scenes:
        source = args.mipnerf360 + "/" + scene
        os.system(
            "python train.py -s "
            + source
            + " -i images_2 -m "
            + args.output_path
            + "/"
            + scene
            + common_args
        )
    m360_timing = (time.time() - start_time) / 60.0

    start_time = time.time()
    for scene in scannetpp_scenes:
        source = args.scannetpp + "/" + scene
        os.system(
            "python train.py -s "
            + source
            + " -m "
            + args.output_path
            + "/"
            + scene
            + common_args
        )
    scannetpp_timing = (time.time() - start_time) / 60.0

    start_time = time.time()
    for scene in blender_scenes:
        source = args.blender + "/" + scene
        os.system(
            "python train.py -s "
            + source
            + " -m "
            + args.output_path
            + "/"
            + scene
            + common_args
        )
    blender_timing = (time.time() - start_time) / 60.0

with open(os.path.join(args.output_path, "timing.txt"), "w") as file:
    file.write(
        f"m360: {m360_timing} minutes \nscannetpp: {scannetpp_timing} minutes \nblender: {blender_timing} minutes \n"
    )

if not args.skip_rendering:
    all_sources = []
    for scene in mipnerf360_outdoor_scenes:
        all_sources.append(args.mipnerf360 + "/" + scene)
    for scene in mipnerf360_indoor_scenes:
        all_sources.append(args.mipnerf360 + "/" + scene)
    for scene in scannetpp_scenes:
        all_sources.append(args.scannetpp + "/" + scene)
    for scene in blender_scenes:
        all_sources.append(args.blender + "/" + scene)

    common_args = " --quiet --eval --skip_train"
    for scene, source in zip(all_scenes, all_sources):
        os.system(
            "python render.py --iteration 7000 -s "
            + source
            + " -m "
            + args.output_path
            + "/"
            + scene
            + common_args
        )
        os.system(
            "python render.py --iteration 30000 -s "
            + source
            + " -m "
            + args.output_path
            + "/"
            + scene
            + common_args
        )

if not args.skip_metrics:
    scenes_string = ""
    for scene in all_scenes:
        scenes_string += '"' + args.output_path + "/" + scene + '" '

    os.system("python metrics.py -m " + scenes_string)
