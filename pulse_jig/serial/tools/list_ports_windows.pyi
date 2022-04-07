import ctypes
from collections.abc import Generator
from ctypes.wintypes import DWORD
from serial.tools import list_ports_common as list_ports_common
from serial.win32 import ULONG_PTR as ULONG_PTR
from typing import Any

def ValidHandle(value, func, arguments): ...

NULL: int
HDEVINFO = ctypes.c_void_p
LPCTSTR = ctypes.c_wchar_p
PCTSTR = ctypes.c_wchar_p
PTSTR = ctypes.c_wchar_p
LPDWORD: Any
PDWORD: Any
LPBYTE = ctypes.c_void_p
PBYTE = ctypes.c_void_p
ACCESS_MASK = DWORD
REGSAM = ACCESS_MASK

class GUID(ctypes.Structure): ...
class SP_DEVINFO_DATA(ctypes.Structure): ...

PSP_DEVINFO_DATA: Any
PSP_DEVICE_INTERFACE_DETAIL_DATA = ctypes.c_void_p
setupapi: Any
SetupDiDestroyDeviceInfoList: Any
SetupDiClassGuidsFromName: Any
SetupDiEnumDeviceInfo: Any
SetupDiGetClassDevs: Any
SetupDiGetDeviceRegistryProperty: Any
SetupDiGetDeviceInstanceId: Any
SetupDiOpenDevRegKey: Any
advapi32: Any
RegCloseKey: Any
RegQueryValueEx: Any
cfgmgr32: Any
CM_Get_Parent: Any
CM_Get_Device_IDW: Any
CM_MapCrToWin32Err: Any
DIGCF_PRESENT: int
DIGCF_DEVICEINTERFACE: int
INVALID_HANDLE_VALUE: int
ERROR_INSUFFICIENT_BUFFER: int
ERROR_NOT_FOUND: int
SPDRP_HARDWAREID: int
SPDRP_FRIENDLYNAME: int
SPDRP_LOCATION_PATHS: int
SPDRP_MFG: int
DICS_FLAG_GLOBAL: int
DIREG_DEV: int
KEY_READ: int
MAX_USB_DEVICE_TREE_TRAVERSAL_DEPTH: int

def get_parent_serial_number(
    child_devinst, child_vid, child_pid, depth: int = ..., last_serial_number: Any | None = ...
): ...
def iterate_comports() -> Generator[Any, None, None]: ...
def comports(include_links: bool = ...): ...
