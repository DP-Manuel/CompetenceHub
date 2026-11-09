"""Native CurrentUser DPAPI for the isolated synthetic recovery probe only.

No keystore/credential files, UI, key generation or operator backup entry point.
Ciphertext is user/machine-bound: NOT an independent portable recovery strategy.
"""
import ctypes
from ctypes import wintypes
import os
import sys


class ProtectionError(RuntimeError):
    pass


class Blob(ctypes.Structure):
    _fields_=[('length',wintypes.DWORD),('data',ctypes.POINTER(ctypes.c_ubyte))]


def transform(payload: bytes, *, decrypt=False) -> bytes:
    if os.name!='nt' or not payload or len(payload)>64*1024*1024:
        raise ProtectionError('Synthetic DPAPI input unavailable or exceeds bound')
    crypt=ctypes.WinDLL('crypt32',use_last_error=True)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.LocalFree.argtypes=[ctypes.c_void_p];kernel.LocalFree.restype=ctypes.c_void_p
    source=ctypes.create_string_buffer(payload)
    incoming=Blob(len(payload),ctypes.cast(source,ctypes.POINTER(ctypes.c_ubyte)))
    outgoing=Blob()
    # UI_FORBIDDEN=1, never LOCAL_MACHINE=4. No external entropy/password.
    if decrypt:
        operation=crypt.CryptUnprotectData
        operation.argtypes=[ctypes.POINTER(Blob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)]
        args=(ctypes.byref(incoming),None,None,None,None,1,ctypes.byref(outgoing))
    else:
        operation=crypt.CryptProtectData
        operation.argtypes=[ctypes.POINTER(Blob),wintypes.LPCWSTR,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)]
        args=(ctypes.byref(incoming),None,None,None,None,1,ctypes.byref(outgoing))
    operation.restype=wintypes.BOOL
    if not operation(*args): raise ProtectionError('Synthetic DPAPI verification failed')
    try:return ctypes.string_at(outgoing.data,outgoing.length)
    finally:
        ctypes.memset(outgoing.data,0,outgoing.length)
        kernel.LocalFree(ctypes.cast(outgoing.data,ctypes.c_void_p))


if __name__=='__main__':
    if sys.argv[1:]!=['--synthetic-decrypt-stdin']:
        raise SystemExit(2)
    try:
        sys.stdout.buffer.write(transform(sys.stdin.buffer.read(64*1024*1024+1),decrypt=True))
    except ProtectionError:
        raise SystemExit(1) from None
