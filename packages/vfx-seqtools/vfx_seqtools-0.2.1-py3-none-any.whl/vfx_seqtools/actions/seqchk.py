import glob
import logging
import pathlib
from typing import Annotated, Optional

import fileseq
import OpenEXR
import typer
from PIL import Image
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

from vfx_seqtools import common_options
from vfx_seqtools.decorators import attach_hook


def do_action(tupl: tuple) -> bool:
    framefile, is_dryrun, be_verbose, be_strict, logger = tupl
    if is_dryrun:
        logger.info(f"dry-run: CHECK {framefile}")
        return True
    else:
        # Run the command using subprocess or any other method
        if be_verbose:
            logger.info(f"CHECK {framefile}")

        try:
            framepath = pathlib.Path(framefile)
            if framepath.suffix.lower() == ".exr":
                with OpenEXR.File(framefile):
                    # header = infile.header()
                    # print(f"type={header['type']}")
                    # print(f"compression={header['compression']}")

                    # RGB = infile.channels()["RGB"].pixels
                    # height, width = RGB.shape[0:2]
                    # print(f"width={width}, height={height}")
                    # print(f"channels={infile.channels()}")
                    pass
            else:
                Image.open(framefile).verify()
                # print(f"{verify_response} was returned by verify")
                Image.open(framefile)
                # print(f"{im.filename.split('/')[-1]} is a valid image")
                # im.show()
            return True
        except Exception:
            return False


@attach_hook(common_options.logging_options, hook_output_kwarg="logger")
@attach_hook(common_options.dry_run_option, hook_output_kwarg="is_dryrun")
@attach_hook(common_options.verbose_option, hook_output_kwarg="be_verbose")
@attach_hook(common_options.strict_option, hook_output_kwarg="be_strict")
@attach_hook(common_options.version_option, hook_output_kwarg="show_version")
@attach_hook(common_options.sequence_only_option, hook_output_kwarg="only_on_sequences")
def seqchk(
    show_version: bool,
    logger: logging.Logger,
    filepattern: Annotated[
        str,
        typer.Argument(
            help="An optional file pattern to use, use quotes or escape shell wildcards like '?' and '*'."
        ),
    ] = "",
    be_verbose: Optional[bool] = False,
    be_strict: Optional[bool] = False,
    is_dryrun: Optional[bool] = False,
    only_on_sequences: bool = False,
) -> None:
    """
    Check file sequences.

    seqchk - will check all file sequences in the current directory.

    seqchk file.\*.exr - will check all file sequences matching the pattern 'file.*.exr' (escaping shell wildcards).

    seqchk "file.????.exr" - will check all file sequences matching the pattern 'file.????.exr' (quoting shell wildcards).

    """
    if filepattern:
        files = glob.glob(filepattern)
        seqs = fileseq.findSequencesInList(files)
    else:
        seqs = fileseq.findSequencesOnDisk(".")

    for seq in seqs:
        if only_on_sequences and "@" not in str(seq) and "#" not in str(seq):
            continue
        if is_dryrun:
            for framefile in list(seq):
                do_action((framefile, is_dryrun, be_verbose, be_strict, logger))
        else:
            bad_frames = []
            from rich.logging import RichHandler

            logging.basicConfig(
                level=logging.INFO,
                format="%(message)s",
                datefmt="[%X]",
                handlers=[RichHandler(rich_tracebacks=True)],
            )
            logger = logging.getLogger("rich")
            progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                MofNCompleteColumn(),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
            )
            with progress:
                for framefile in progress.track(
                    list(seq), description=f"Checking {str(seq)}..."
                ):
                    check_ok = do_action(
                        (framefile, is_dryrun, be_verbose, be_strict, logger)
                    )
                    if not check_ok:
                        bad_frames.append(framefile)

            if bad_frames:
                if len(bad_frames) == 1:
                    print(f"{str(seq)}: Bad frame: {bad_frames[0]}")
                else:
                    badseqs = fileseq.findSequencesInList(bad_frames)
                    # print(f"Bad sequences: {badseqs}")
                    print(f"{str(seq)}: Bad frames: {badseqs[0].frameSet()}")
