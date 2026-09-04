"""Minimal Windows Restart Manager adapter used by LockPeek."""

from __future__ import annotations

import ctypes
import os
from ctypes import POINTER, Structure, byref, c_void_p, wintypes
from pathlib import Path

from .core import Holder

ERROR_MORE_DATA = 234
ERROR_SUCCESS = 0
SESSION_KEY_CHARS = 32


class _RmUniqueProcess(Structure):
    _fields_ = [
        ("dwProcessId", wintypes.DWORD),
        ("ProcessStartTime", wintypes.FILETIME),
    ]


class _RmProcessInfo(Structure):
    _fields_ = [
        ("Process", _RmUniqueProcess),
        ("strAppName", wintypes.WCHAR * 256),
        ("strServiceShortName", wintypes.WCHAR * 64),
        ("ApplicationType", wintypes.DWORD),
        ("AppStatus", wintypes.DWORD),
        ("TSSessionId", wintypes.DWORD),
        ("bRestartable", wintypes.BOOL),
    ]


def _raise_api_error(function: str, code: int) -> None:
    if code == ERROR_SUCCESS:
        return
    raise OSError(code, f"{function} returned Windows error {code}")


def find_holders(path: Path) -> list[Holder]:
    """Ask Windows Restart Manager which registered apps use ``path``."""

    if os.name != "nt":
        raise OSError("Restart Manager is available only on Windows")

    dll = ctypes.WinDLL("rstrtmgr.dll")

    start_session = dll.RmStartSession
    start_session.argtypes = [
        POINTER(wintypes.DWORD),
        wintypes.DWORD,
        wintypes.WCHAR * SESSION_KEY_CHARS,
    ]
    start_session.restype = wintypes.DWORD

    end_session = dll.RmEndSession
    end_session.argtypes = [wintypes.DWORD]
    end_session.restype = wintypes.DWORD

    register_resources = dll.RmRegisterResources
    register_resources.argtypes = [
        wintypes.DWORD,
        wintypes.UINT,
        POINTER(wintypes.LPCWSTR),
        wintypes.UINT,
        c_void_p,
        wintypes.UINT,
        POINTER(wintypes.LPCWSTR),
    ]
    register_resources.restype = wintypes.DWORD

    get_list = dll.RmGetList
    get_list.argtypes = [
        wintypes.DWORD,
        POINTER(wintypes.UINT),
        POINTER(wintypes.UINT),
        POINTER(_RmProcessInfo),
        POINTER(wintypes.DWORD),
    ]
    get_list.restype = wintypes.DWORD

    session = wintypes.DWORD()
    session_key = (wintypes.WCHAR * SESSION_KEY_CHARS)()
    _raise_api_error("RmStartSession", start_session(byref(session), 0, session_key))

    try:
        filenames = (wintypes.LPCWSTR * 1)(str(path))
        _raise_api_error(
            "RmRegisterResources",
            register_resources(session, 1, filenames, 0, None, 0, None),
        )

        needed = wintypes.UINT()
        count = wintypes.UINT()
        reasons = wintypes.DWORD()
        first = get_list(session, byref(needed), byref(count), None, byref(reasons))
        if first not in {ERROR_SUCCESS, ERROR_MORE_DATA}:
            _raise_api_error("RmGetList", first)
        if needed.value == 0:
            return []

        process_info = (_RmProcessInfo * needed.value)()
        count = wintypes.UINT(needed.value)
        _raise_api_error(
            "RmGetList",
            get_list(
                session,
                byref(needed),
                byref(count),
                process_info,
                byref(reasons),
            ),
        )
        holders: list[Holder] = []
        for index in range(count.value):
            info = process_info[index]
            name = info.strAppName or info.strServiceShortName or "unknown"
            holders.append(
                Holder(
                    pid=int(info.Process.dwProcessId),
                    name=name,
                    source="restart-manager",
                )
            )
        return holders
    finally:
        _raise_api_error("RmEndSession", end_session(session))
