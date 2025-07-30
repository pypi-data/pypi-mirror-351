# (c) 2015-2024 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import os
import logging.config
import sys
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("acemd")
except PackageNotFoundError:
    pass


dirname = os.path.dirname(__file__)

try:
    logging.config.fileConfig(
        os.path.join(dirname, "logging.ini"), disable_existing_loggers=False
    )
except Exception:
    print("acemd: Logging setup failed")

from acemd.acemd import acemd, get_acemd_system

_skip_checks = False
if len(sys.argv) > 0 and sys.argv[0].endswith("acemd_register"):
    _skip_checks = True
if (
    len(sys.argv) == 2
    and sys.argv[0].endswith("acemd")
    and sys.argv[1] in ("-h", "--help", "--version", "--license")
):
    _skip_checks = True

if (
    not _skip_checks  # Don't run when the user is executing acemd_register or acemd --help/license/version
    and not os.getenv("CI")  # Don't run in CI
    and not os.getenv("ACEMD_NONINTERACTIVE")  # Don't run in non-interactive mode
    and not os.getenv("APPTAINER_CONTAINER")  # Don't run in Apptainer
):
    from acemd.versionwarnings import _check_for_updates, _print_news
    from acemd.licensing import (
        _is_registered,
        _check_registration,
        _check_license,
        _print_license_file,
        _send_telemetry,
    )
    import time

    licensed = _check_license()

    if not licensed:
        # Don't send telemetry for licensed users
        _send_telemetry("ACEMD", __version__)

    _check_for_updates()
    _print_news()

    # Check if user has an ACEMD license. If not check if they are registered
    if not licensed and (not _is_registered() or not _check_registration()):
        _print_license_file()
        print(
            "By continuing to use ACEMD you are automatically accepting the above license agreement.\n"
            "For commercial licenses please contact info@acellera.com\n"
            "To remove the above license message for non-commercial purposes please register ACEMD by calling acemd_register from command line.\n"
            "Resuming in 5 seconds..."
        )
        time.sleep(5)
