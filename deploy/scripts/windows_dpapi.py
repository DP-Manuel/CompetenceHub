"""Bounded Windows CurrentUser DPAPI; no keystore, password, UI or key rotation.

This is machine/user-bound temporary rollback storage, NOT portable recovery.
The CLI is a private binary-pipe worker; never run it with terminal output.
"""
import ctypes
from ctypes import wintypes
import os
import sys

MAX_BYTES = 64 * 1024 * 1024


class ProtectionError(RuntimeError):
    pass


class Blob(ctypes.Structure):
    _fields_ = [('length', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_ubyte))]


def transform(payload: bytes, *, decrypt=False) -> bytes:
    bound = MAX_BYTES if decrypt else MAX_BYTES - 4096
    if os.name != 'nt' or not payload or len(payload) > bound:
        raise ProtectionError('DPAPI_INPUT_BOUND_OR_PLATFORM')
    crypt = ctypes.WinDLL('crypt32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    source = ctypes.create_string_buffer(payload)
    incoming = Blob(len(payload), ctypes.cast(source, ctypes.POINTER(ctypes.c_ubyte)))
    outgoing = Blob()
    # UI_FORBIDDEN=1. Never LOCAL_MACHINE=4; never use existing application keys.
    operation = crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    second = ctypes.c_void_p if decrypt else wintypes.LPCWSTR
    operation.argtypes = [ctypes.POINTER(Blob), second, ctypes.c_void_p, ctypes.c_void_p,
                          ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    operation.restype = wintypes.BOOL
    try:
        if not operation(ctypes.byref(incoming), None, None, None, None, 1, ctypes.byref(outgoing)):
            raise ProtectionError('DPAPI_VERIFICATION_FAILED')
        return ctypes.string_at(outgoing.data, outgoing.length)
    finally:
        ctypes.memset(source, 0, len(payload))
        if outgoing.data:
            ctypes.memset(outgoing.data, 0, outgoing.length)
            kernel.LocalFree(ctypes.cast(outgoing.data, ctypes.c_void_p))


if __name__ == '__main__':
    if sys.argv[1:] != ['--decrypt-stdin'] or sys.stdin.isatty() or sys.stdout.isatty():
        raise SystemExit(2)
    try:
        sys.stdout.buffer.write(transform(sys.stdin.buffer.read(MAX_BYTES + 1), decrypt=True))
    except Exception:
        raise SystemExit(1) from None
