import os
from typing import List

from bluer_objects import file, README

from bluer_sbc import NAME, VERSION, ICON, REPO_NAME


image_prefix = "https://github.com/kamangir/blue-bracket/raw/main/images/"
design_prefix = "https://github.com/kamangir/blue-bracket/blob/main/designs/"


def items() -> List[str]:
    return [
        "[![image]({}{})]({}{}.md)".format(
            image_prefix,
            item["image"],
            design_prefix,
            item["name"],
        )
        for item in [
            {
                "image": "blue3-1.jpg",
                "name": "blue3",
            },
            {
                "image": "chenar-grove-1.jpg",
                "name": "chenar-grove",
            },
            {
                "image": "cube-1.jpg",
                "name": "cube",
            },
            {
                "image": "eye_nano-1.jpg",
                "name": "eye_nano",
            },
        ]
    ]


def build():
    return README.build(
        items=items(),
        cols=4,
        path=os.path.join(file.path(__file__), ".."),
        ICON=ICON,
        NAME=NAME,
        VERSION=VERSION,
        REPO_NAME=REPO_NAME,
    )
