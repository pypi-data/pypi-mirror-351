# (c) 2015-2023 Acellera Ltd www.acellera.com
# All rights reserved
# Distributed under the terms of the HTMD Software License Agreement
# No redistribution in whole or in part

import json
import os
import pathlib
import requests
import uuid
import logging

logger = logging.getLogger("acemd")

_REGISTRATION_FILE = os.path.join(pathlib.Path.home(), ".acellera", "acemd.json")


def _is_registered():
    """Check if the user has registered. Does not check if the registration is still valid"""
    content = _get_registration_content()
    return content.get("code", None) is not None


def _get_registration_content():
    if os.path.exists(_REGISTRATION_FILE):
        with open(_REGISTRATION_FILE) as fh:
            content = json.load(fh)
            return content if content is not None else {}
    else:
        return {}


def _get_telemetry_id():
    content = _get_registration_content()

    if "telemetry_id" not in content:
        content["telemetry_id"] = str(uuid.uuid4())
        with open(_REGISTRATION_FILE, "w") as fh:
            json.dump(content, fh)

    return content["telemetry_id"]


def _print_debug(message):
    if "ACEMD_TELEMETRY_DEBUG" in os.environ:
        print(message)


def _send_telemetry(name: str, version: str) -> None:
    """Send telemetry data to the telemetry server"""
    _print_debug("# Telemetry")

    try:
        url = os.environ.get("ACEMD_TELEMETRY_URL", "https://telemetry.acellera.com")
        _print_debug(f"#   URL: {url}")

        _print_debug(f"#   Config path: {_REGISTRATION_FILE}")

        data = {"name": name, "version": version, "id": _get_telemetry_id()}
        _print_debug(f"#   Data: {data}")

        response = requests.post(url, json=data, timeout=10)
        _print_debug(f"#   Response: {response}")

    except Exception as e:
        _print_debug(f"#   Exception: {e}")

    _print_debug("#")


def _print_license_file():
    """Print the license file to the terminal"""
    from acemd import dirname

    # Find the license file
    path = os.path.join(dirname, "LICENSE")
    if not os.path.exists(path):
        raise RuntimeError("Cannot find the license file!")

    with open(path) as fh:
        print("")
        print(fh.read())
        print("")


def _check_license(_print=False):
    from pathlib import Path
    from acemd import dirname

    envvars = [
        "ACELLERA_LICENCE_SERVER",
        "ACELLERA_LICENSE_SERVER",
        "ACELLERA_LICENCE_FILE",
        "ACELLERA_LICENSE_FILE",
    ]
    user_home = str(Path.home())
    locations = [
        "/opt/acellera/licence.dat",
        "/opt/acellera/license.dat",
        os.path.join(user_home, ".acellera/licence.dat"),
        os.path.join(user_home, ".acellera/license.dat"),
    ]

    if (
        any([envv in os.environ for envv in envvars])
        or any([os.path.exists(ll) for ll in locations])
        or _print
    ):
        import subprocess

        try:
            ret = subprocess.Popen(
                os.path.join(dirname, "share", "license-checker"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            ret.wait()
            if ret.returncode == 0 and not _print:
                return True
            else:  # Only print if license check failed
                print(ret.communicate()[0].decode("utf-8"))
        except Exception:
            pass
    return False


def _check_registration():
    """Check if the registration data is valid and approved"""
    try:
        content = _get_registration_content()
        content["product"] = "acemd"

        # Send the registration data
        url = "https://registration.acellera.com/check"
        res = requests.post(url, content, timeout=10)

        # Check the response
        if res.status_code == 200:
            status = res.json()
            if "approved" in status:
                return True

    except Exception:
        print("Failed to check registration")
        return False

    print(f"Registration is not approved: {res.text}")
    return False


def acemd_register():
    print(
        """
  Welcome to the ACEMD registration!

  By registering ACEMD you are agreeing to the terms and conditions of the ACEMD license.
  Please see https://software.acellera.com/acemd/licence.html for more details.

  If you are using ACEMD for commercial purposes you need to contact info@acellera.com
  for a commercial license.

  We would like to know about you to keep in touch.
  Please provide your full name, institutional email,
  institution name, city, and country.
"""
    )

    def _ask(prompt):
        value = ""
        while value == "":
            value = input(prompt).strip()
        return value

    # Ask a user for data
    data = {}
    data["name"] = _ask("  Full name           : ")
    data["email"] = _ask("  Institutional email : ")
    data["institution"] = _ask("  Institution name    : ")
    data["city"] = _ask("  City                : ")
    data["country"] = _ask("  Country             : ")
    data["product"] = "acemd"

    # Send data to the registration server
    url = "https://registration.acellera.com/register"
    res = requests.post(url, data=data, timeout=10)

    content = _get_registration_content()
    # Check the response
    if res.status_code == 200:
        content.update(res.json())
        with open(_REGISTRATION_FILE, "w") as fh:
            json.dump(content, fh)
        print("\n  Registration completed!\n")
    else:
        print(f"\n  Registration failed: {res.text}\n")
