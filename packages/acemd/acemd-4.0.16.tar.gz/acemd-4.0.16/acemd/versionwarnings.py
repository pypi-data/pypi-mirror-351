# (c) 2015-2024 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import os
import logging
import pathlib

logger = logging.getLogger("acemd")

_REGISTRATION_FILE = os.path.join(pathlib.Path.home(), ".acellera", "acemd.json")


def _read_registration_file():
    import json

    dirname = os.path.dirname(_REGISTRATION_FILE)
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname, exist_ok=True)
        except Exception:
            logger.warning(
                f"Unable to create {dirname} folder. Will not check for new ACEMD versions."
            )
            return None

    try:
        with open(_REGISTRATION_FILE) as fh:
            return json.load(fh)
    except Exception:
        try:
            if os.path.isfile(_REGISTRATION_FILE):
                os.remove(_REGISTRATION_FILE)
        except Exception:
            if os.path.isfile(_REGISTRATION_FILE):
                logger.warning(
                    f"Unable to remove broken {_REGISTRATION_FILE} file. Will not check for new ACEMD versions."
                )
                return None

        try:
            with open(_REGISTRATION_FILE, "w") as fh:
                json.dump({}, fh)
        except Exception:
            logger.warning(
                f"Unable to create {_REGISTRATION_FILE} file. Will not check for new ACEMD versions."
            )
            return None
        return {}


def _get_latest_version():
    import urllib.request
    import json

    version = None
    try:
        url = "https://api.anaconda.org/package/acellera/acemd"
        with urllib.request.urlopen(url) as r:
            version = json.loads(r.read())["latest_version"]
    except Exception:
        return None

    return version


def _check_for_updates():
    from acemd import __version__ as currver
    from natsort import natsorted
    import json
    import time

    info = _read_registration_file()
    if info is None:
        return

    # Check if one day has passed since last version check. If yes, get new version and write to file
    if (
        "latest_version" not in info
        or "last_version_check" not in info
        or time.time() > info["last_version_check"] + 86400
    ):
        latest_version = _get_latest_version()
        if latest_version is not None:
            info["latest_version"] = latest_version
            info["last_version_check"] = time.time()
            try:
                with open(_REGISTRATION_FILE, "w") as f:
                    json.dump(info, f)
            except Exception:
                logger.warning(
                    f"Unable to open {_REGISTRATION_FILE} file for writing. Will not check for new ACEMD versions."
                )
                return

    try:
        with open(_REGISTRATION_FILE, "r") as f:
            latest = json.load(f).get("latest_version", None)
    except Exception:
        logger.warning(
            f"Unable to open {_REGISTRATION_FILE} file for reading. Will not check for new ACEMD versions."
        )
        return

    if latest is None:
        return

    if natsorted((latest, currver))[1] != currver:
        logger.warning(
            f"New ACEMD version ({latest}) is available. You are currently on ({currver}). "
            "We recommend you create a new conda environment with the latest ACEMD version https://software.acellera.com/acemd/install.html "
        )
    else:
        logger.info(f"# You are on the latest ACEMD version ({currver}).")


def _get_news():
    import urllib.request

    news = None
    try:
        url = "https://software.acellera.com/acemd/news"
        with urllib.request.urlopen(url) as r:
            news = r.read()
    except Exception:
        return None

    return news.decode("utf-8")


def _print_news():
    import json
    import time

    info = _read_registration_file()
    if info is None:
        return

    # Check if one day has passed since last news check. If yes, get news and write to file
    if (
        "news" not in info
        or "last_news_check" not in info
        or time.time() > info["last_news_check"] + 86400
    ):
        news = _get_news()
        if news is not None:
            info["news"] = news
            info["last_news_check"] = time.time()
            try:
                with open(_REGISTRATION_FILE, "w") as f:
                    json.dump(info, f)
            except Exception:
                logger.warning(
                    f"Unable to open {_REGISTRATION_FILE} file for writing. Will not check for ACEMD news."
                )
                return

    try:
        with open(_REGISTRATION_FILE, "r") as f:
            news = json.load(f).get("news", None)
    except Exception:
        logger.warning(
            f"Unable to open {_REGISTRATION_FILE} file for reading. Will not check for ACEMD news."
        )
        return

    if news is not None and news != "":
        logger.info(news)
