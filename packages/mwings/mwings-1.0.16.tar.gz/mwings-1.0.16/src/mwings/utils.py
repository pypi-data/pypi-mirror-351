# -*- coding:utf-8 -*-
# Written for Python 3.12
# Formatted with Black

# Utils for MWings

import sys
import os
import subprocess
import time
import math
import re
from pathlib import Path
from typing import Callable

import serial  # type: ignore
from serial.tools import list_ports  # type: ignore


def open_on_system(path: Path) -> None:
    """Open the file in the given path on system using default application

    Parameters
    ----------
    path : Path
        pathlib.Path for file
    """

    if sys.platform == "win32":
        os.startfile(path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path])


def ask_user(
    prompt: str,
    regex: str,
    on_error: str,
    ex_verifier: Callable[[str], bool] | None = None,
    max_attempts: int | None = None,
) -> str:
    """Ask user for something in text

    Parameters
    ----------
    prompt : str
        Prompt message
    regex : str
        Regular expression for validate user input
    on_error : str
        Message for invalid input
    ex_verifier : Callable[[str], bool] | None
        Extra verifier in addition to regex
    max_attempts : int | None
        Max count for attempts. None to infinite

    Returns
    -------
    str
        Valid user input
    """

    attempt = 0
    while True:
        if max_attempts and attempt >= max_attempts:
            return ""
        try:
            user_input = input(prompt)
            if (re.search(regex, user_input) is None) or (
                ex_verifier is not None and not ex_verifier(user_input)
            ):
                raise ValueError(on_error)
            break
        except ValueError as e:
            print(e)
        attempt = attempt + 1
    return user_input


def get_ports() -> list[str]:
    """Get port informations

    Returns
    -------
    list[str]
        List of port names
    """

    comports: list[list_ports.ListPortInfo] = list_ports.comports()
    return [port.device for port in comports]


def is_there_some_ports() -> bool:
    """Check if there is some ports exists

    Returns
    -------
    bool
        True if exists
    """

    return bool(len(get_ports()))


def ask_user_for_port() -> str:
    """Ask the user for the port to use

    If there's only one port, auto selects without asking.

    Returns
    -------
    str
        Port name (COM or fd)

    Notes
    -----
        If the console is not available, raise EnvironmentError.
        If there's no ports, raise IOError.
    """
    if not sys.stdin.isatty():
        raise EnvironmentError("There's no console.")

    ports: list[list_ports.ListPortInfo] = list_ports.comports()

    if ports == []:
        raise IOError("There's no serial port.")

    if len(ports) == 1:
        print(f"Auto selected: {ports[0].device}")
        return str(ports[0].device)

    print("Multiple ports detected.")
    for i, port in enumerate(ports):
        if port.manufacturer == "MONOWIRELESS":
            # Print in magenta
            print(f"[{i+1}] {port.device} \033[35m{port.description} (Genuine)\033[00m")
        elif port.manufacturer == "TOCOS":
            # Print in blue
            print(f"[{i+1}] {port.device} \033[34m{port.description} (Legacy)\033[00m")
        else:
            print(f"[{i+1}] {port.device} {port.description}")

    user_input = ask_user(
        f"Select [1-{len(ports)}]: ",
        regex=r"^[0-9]+$",
        ex_verifier=lambda s: int(s) <= len(ports),
        on_error=f"Please answer 1-{len(ports)}.",
    )
    print(f"Selected: {ports[int(user_input) - 1].device}")
    return str(ports[int(user_input) - 1].device)


def millis() -> int:
    """Get current time in milliseconds

    Returns
    -------
    int
        Current epoch in milliseconds
    """

    return round(time.time_ns() / 1000000)


def lrc8(data: bytes) -> int:
    """Calculate 8-bit LRC for given data

    Parameters
    ----------
    data : bytes
        Bytes to calculate

    Returns
    -------
    int
        LRC checksum
    """

    return int(((sum(data) ^ 0xFF) + 1) & 0xFF)


def hex_from(character: int) -> int:
    """Convert to hex from character

    Parameters
    ----------
    character : int
        Integer value of an ASCII character ('0'-'F')

    Returns
    -------
    int
        Binary integer value (0x0-0xF)
    """

    return character - ord("0") if character < ord("A") else character - ord("A") + 0xA


def character_from(hexvalue: int) -> int:
    """Convert to character from hex

    Parameters
    ----------
    hexvalue : int
        Binary integer value (0x0-0xF)

    Returns
    -------
    int
        Integer value of an ASCII character ('0'-'F')
    """

    return ord("0") + hexvalue if hexvalue < 0xA else ord("A") + hexvalue - 0xA


def byte_count_from(character_count: int) -> int:
    """Convert to byte count from character count

    Parameters
    ----------
    character_count : int
        bytes count in ascii format

    Returns
    -------
    int
        bytes count in binary format
    """

    return math.floor(character_count / 2)


def is_initialized(port: serial.Serial) -> bool:
    """Check if the serial port is initialized

    Parameters
    ----------
    port : serial.Serial
        pyserial instance

    Returns
    -------
    bool
        initialized if true
    """

    return bool(port.readable() and port.writable())


def is_readable(port: serial.Serial) -> bool:
    """Check if the serial port is readable

    Parameters
    ----------
    port : serial.Serial
        pyserial instance

    Returns
    -------
    bool
        readable if true
    """

    return bool(port.readable())


def is_writable(port: serial.Serial) -> bool:
    """Check if the serial port is writable

    Parameters
    ----------
    port : serial.Serial
        pyserial instance

    Returns
    -------
    bool
        writable if true
    """

    return bool(port.writable())


def write_binary(port: serial.Serial, data: int | bytes) -> None:
    """Write binary integer value to the serial port

    Parameters
    ----------
    port : serial.Serial
        pyserial instance
    data : int | bytes
        Binary integer value or bytes
    """

    match data:
        case int():
            if not is_writable(port):
                return None
            if not data >= 0:
                return None
            elif data <= 0xFF:
                port.write(data.to_bytes(1))
            elif data <= 0xFFFF:
                port.write(data.to_bytes(2))
            elif data <= 0xFFFFFFFF:
                port.write(data.to_bytes(4))
        case bytes():
            for byte in data:
                write_binary(port, byte)


def write_in_ascii(port: serial.Serial, data: int | bytes) -> None:
    """Write binary in ASCII format to the serial port

    Parameters
    ----------
    port : serial.Serial
        pyserial instance
    data : int
        Binary integer value or bytes
    """

    match data:
        case int():
            if not is_writable(port):
                return None
            if not data >= 0:
                return None
            elif data <= 0xFF:
                port.write(
                    bytes(
                        [character_from((data >> i) & 0x0F) for i in range(4, -1, -4)]
                    )
                )
            elif data <= 0xFFFF:
                port.write(
                    bytes(
                        [character_from((data >> i) & 0x0F) for i in range(12, -1, -4)]
                    )
                )
            elif data <= 0xFFFFFFFF:
                port.write(
                    bytes(
                        [character_from((data >> i) & 0x0F) for i in range(28, -1, -4)]
                    )
                )
        case bytes():
            for byte in data:
                write_in_ascii(port, byte)


def flush_rx_buffer(port: serial.Serial) -> None:
    """Flush serial rx buffer

    Parameters
    ----------
    port : serial.Serial
        pyserial instance
    """

    port.reset_input_buffer()


def flush_tx_buffer(port: serial.Serial) -> None:
    """Flush serial tx buffer

    Parameters
    ----------
    port : serial.Serial
        pyserial instance
    """

    port.reset_output_buffer()


def find_binary(
    port: serial.Serial,
    data: bytes,
    timeout: int,
    with_terminal: bool = False,
    terminal: int = 0,
    debugging: bool = False,
) -> bool:
    """Find binary bytes in serial rx data

    Parameters
    ----------
    port : serial.Serial
        pyserial instance
    data : bytes
        Binary data bytes to find
    timeout : int
        Timeout in seconds
    with_terminal : bool
        Use terminal byte for data input or not
    terminal : int
        Terminal byte for data input
    debugging : bool
        Print debug info if true

    Returns
    -------
    bool
        Found if true
    """

    if not is_initialized(port):
        return False
    if not len(data) > 0:
        return False
    timestamp: int = millis()
    while True:
        if millis() - timestamp > timeout * 1000:
            return False
        if port.in_waiting:
            read_byte = port.read()
            if debugging:
                print(read_byte.decode("utf-8"))
            if int.from_bytes(read_byte) == data[0]:  # compare as int
                break
    for datum in data[1:]:  # omit the first one
        if with_terminal and terminal == datum:
            break
        while True:
            if millis() - timestamp > timeout * 1000:
                return False
            if port.in_waiting:
                read_byte = port.read()
                if debugging:
                    print(read_byte.decode("utf-8"))
                if int.from_bytes(read_byte) == datum:
                    break
                else:
                    # If data is invalid, retry recursively.
                    return find_binary(
                        port,
                        data,
                        timeout * 1000 - millis() + timestamp,
                        with_terminal,
                        terminal,
                        debugging,
                    )
    return True


def find_ascii(
    port: serial.Serial, data: str, timeout: int, debugging: bool = False
) -> bool:
    """Find ASCII-formatted bytes in serial rx data

    Parameters
    ----------
    port : serial.Serial
        pyserial instance
    data : str
        ASCII-formatted bytes to find
    timeout : int
        Timeout in seconds
    debugging : bool
        Print debug info if true

    Returns
    -------
    bool
        Found if true
    """

    return find_binary(port, data.encode("ascii"), timeout, False, 0, debugging)
