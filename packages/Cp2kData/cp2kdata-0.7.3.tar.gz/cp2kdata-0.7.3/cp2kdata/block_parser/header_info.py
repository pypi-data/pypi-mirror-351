import regex as re
from dataclasses import dataclass
# use monty.re because it can terminate on match
from monty.re import regrep
from cp2kdata.log import get_logger

logger = get_logger(__name__)

@dataclass
class Cp2kInfo:
    version: str = None
    restart: bool = None
    terminated_by_request: bool = None


CP2K_INFO_VERSION_PATTERN = \
    r"""(?xm)
    ^\sCP2K\|\sversion\sstring:\s{10,42}
    CP2K\sversion\s(?P<version>\d{1,4}\.\d)(?:\s\(Development\sVersion\))?$
    """

CP2K_INFO_RESTART_PATTERN = \
    r"""(?xm)
    ^\s\*\s{28}RESTART\sINFORMATION\s{30}\*$
    """

CP2K_INFO_TERMINATED_BY_REQUEST = \
    r"""(?xm)
    ^\s\*{3}\sMD\srun\sterminated\sby\sexternal\srequest\s\*{3}
    """

def parse_cp2k_info(filename) -> Cp2kInfo:

    cp2k_info = regrep(
        filename=filename,
        patterns={
            "version": CP2K_INFO_VERSION_PATTERN,
            "restart": CP2K_INFO_RESTART_PATTERN
            },
        terminate_on_match=True
    )

    num_match_restart = len(cp2k_info['restart'])
    if num_match_restart > 1:
        raise ValueError(f"More than one restart information found in {filename}")
    elif num_match_restart == 1:
        cp2k_restart = True
        logger.debug(f"Found restart information in the output header")

    elif num_match_restart == 0:
        cp2k_restart = False


    tmp_info = regrep(
        filename=filename,
        patterns={
            "terminated_by_request": CP2K_INFO_TERMINATED_BY_REQUEST
            },
        reverse=True,
        terminate_on_match=True
    )

    # parse the termination information
    num_match_terminated_by_request = len(tmp_info['terminated_by_request'])
    if num_match_terminated_by_request > 1:
        raise ValueError(f"More than one termination information found in {filename}")
    elif num_match_terminated_by_request == 1:
        cp2k_terminated_by_request = True
    elif num_match_terminated_by_request == 0:
        cp2k_terminated_by_request = False

    return Cp2kInfo(
        version=cp2k_info["version"][0][0][0],
        restart=cp2k_restart,
        terminated_by_request=cp2k_terminated_by_request
        )

@dataclass
class GlobalInfo:
    run_type: str = None
    print_level: str = None


# PATTERNS
GLOBAL_INFO_RUN_TYPE_PATTERN = \
    r"""(?xm)
    ^\sGLOBAL\|\sRun\stype\s{33,}(?P<run_type>\w+)\n
    """
GLOBAL_INFO_PRINT_LEVEL_PATTERN = \
    r"""(?xm)
    ^\sGLOBAL\|\sGlobal\sprint\slevel\s{42,}(?P<print_level>\w+)\n
    """


def parse_global_info(filename) -> GlobalInfo:
    global_info = {}

    global_info = regrep(
        filename=filename,
        patterns={"run_type": GLOBAL_INFO_RUN_TYPE_PATTERN,
                  "print_level": GLOBAL_INFO_PRINT_LEVEL_PATTERN
                  },
        terminate_on_match=True
    )

    return GlobalInfo(run_type=global_info["run_type"][0][0][0],
                      print_level=global_info["print_level"][0][0][0]
                      )


@dataclass
class DFTInfo:
    ks_type: str = None
    multiplicity: str = None


DFT_INFO_KS_TYPE_PATTERN = \
    r"""(?xm)
    ^\sDFT\|\sSpin\s
    (?:
        restricted\sKohn-Sham\s\(RKS\) | unrestricted\s\(spin-polarized\)\sKohn-Sham
    )
    \scalculation\s+(?P<ks_type>\w{3,4})$
    """

DFT_INFO_MULTIPLICITY_PATTERN = \
    r"""(?xm)
    ^\sDFT\|\sMultiplicity\s{57,}(\d{1,4})$
    """


def parse_dft_info(filename) -> DFTInfo:
    dft_info = {}

    dft_info = regrep(
        filename=filename,
        patterns={
            "ks_type": DFT_INFO_KS_TYPE_PATTERN,
            "multiplicity": DFT_INFO_MULTIPLICITY_PATTERN
        },
        terminate_on_match=True
    )

    if dft_info:
        return DFTInfo(ks_type=dft_info["ks_type"][0][0][0], multiplicity=dft_info["multiplicity"][0][0][0])
    else:
        return None


@dataclass
class MDInfo:
    ensemble_type: str = None


# PATTERNS
MD_INFO_ENSEMBLE_TYPE_PATTERN = \
    r"""(?xm)
    ^\s(?:MD_PAR|MD)\|\sEnsemble\s(?:t|T)ype\s{39,60}(?P<ensemble_type>\w{3,16})
    """


def parse_md_info(filename):
    md_info = {}

    md_info = regrep(
        filename=filename,
        patterns={
            "ensemble_type": MD_INFO_ENSEMBLE_TYPE_PATTERN
        },
        terminate_on_match=True
    )

    return MDInfo(ensemble_type=md_info["ensemble_type"][0][0][0])
