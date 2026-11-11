"""仅在 Windows CI 上诊断测试程序所需的系统 DLL 导出，不执行测试程序。"""
import argparse
import ctypes
from pathlib import Path
import struct


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    args = parser.parse_args()
    data = args.executable.read_bytes()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    assert data[pe:pe + 4] == b"PE\0\0"
    sections, optional_size = struct.unpack_from("<H", data, pe + 6)[0], struct.unpack_from("<H", data, pe + 20)[0]
    optional = pe + 24
    assert struct.unpack_from("<H", data, optional)[0] == 0x20B
    table = optional + optional_size

    def offset(rva):
        for i in range(sections):
            virtual_size, address, raw_size, raw = struct.unpack_from("<IIII", data, table + 40 * i + 8)
            if address <= rva < address + max(virtual_size, raw_size):
                return rva - address + raw
        raise ValueError(f"无效 PE 地址：{rva}")

    def string(start):
        return data[start:data.index(b"\0", start)].decode("ascii")

    imports = offset(struct.unpack_from("<I", data, optional + 120)[0])
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetProcAddress.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    kernel.GetProcAddress.restype = ctypes.c_void_p
    missing = []
    while True:
        original, _, _, name, thunk = struct.unpack_from("<IIIII", data, imports)
        if not name:
            break
        dll_name = string(offset(name))
        print("DLL:", dll_name, flush=True)
        try:
            dll = ctypes.WinDLL(dll_name, use_last_error=True)
        except OSError as error:
            missing.append(f"{dll_name}: {error}")
            imports += 20
            continue
        index = offset(original or thunk)
        while True:
            entry = struct.unpack_from("<Q", data, index)[0]
            if not entry:
                break
            if entry & (1 << 63):
                symbol = entry & 0xFFFF
                address = kernel.GetProcAddress(dll._handle, symbol)
            else:
                symbol = string(offset(entry) + 2)
                encoded = ctypes.create_string_buffer(symbol.encode())
                address = kernel.GetProcAddress(dll._handle, ctypes.cast(encoded, ctypes.c_void_p))
            if not address:
                missing.append(f"{dll_name}!{symbol}")
            index += 8
        imports += 20
    for item in missing:
        print("MISSING:", item, flush=True)
    if missing:
        raise SystemExit(1)
    print("全部直接导入符号存在")


if __name__ == "__main__":
    main()
