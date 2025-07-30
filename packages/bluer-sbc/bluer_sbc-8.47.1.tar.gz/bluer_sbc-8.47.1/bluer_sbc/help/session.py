from typing import List

from bluer_options.terminal import show_usage, xtra


def help_session_start(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun,sudo,~upload", mono=mono)

    return show_usage(
        [
            "@sbc",
            "session",
            "start",
            f"[{options}]",
        ],
        "start an @sbc session.",
        mono=mono,
    )


help_functions = {
    "start": help_session_start,
}
