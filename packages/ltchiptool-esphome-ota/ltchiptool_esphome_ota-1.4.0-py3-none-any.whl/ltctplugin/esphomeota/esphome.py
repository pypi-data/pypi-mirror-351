# Copyright (c) Kuba Szczodrzyński 2022-08-06.

import gzip
import hashlib
import os
from enum import IntEnum
from io import BytesIO
from logging import debug, info
from os import stat
from random import random
from socket import (
    AF_INET,
    IPPROTO_TCP,
    SO_SNDBUF,
    SOCK_STREAM,
    SOL_SOCKET,
    TCP_NODELAY,
    gethostbyname,
    socket,
)
from typing import IO, Tuple, Union

from _socket import gaierror
from ltchiptool.util.intbin import inttobe32
from ltchiptool.util.logging import verbose
from ltchiptool.util.misc import sizeof
from ltchiptool.util.streams import ClickProgressCallback

OTA_MAGIC = b"\x6c\x26\xf7\x5c\x45"
UPLOAD_BLOCK_SIZE = 8192
UPLOAD_BUFFER_SIZE = UPLOAD_BLOCK_SIZE * 8


def tohex(data: bytes) -> str:
    out = []
    for i in range(len(data)):
        out.append(data[i : i + 1].hex())
    return " ".join(out)


class OTACode(IntEnum):
    RESP_OK = 0
    RESP_REQUEST_AUTH = 1
    RESP_HEADER_OK = 0x40
    RESP_AUTH_OK = 0x41
    RESP_UPDATE_PREPARE_OK = 0x42
    RESP_BIN_MD5_OK = 0x43
    RESP_RECEIVE_OK = 0x44
    RESP_UPDATE_END_OK = 0x45
    RESP_SUPPORTS_COMPRESSION = 0x46
    RESP_CHUNK_OK = 0x47

    ERROR_MAGIC = 0x80
    ERROR_UPDATE_PREPARE = 0x81
    ERROR_AUTH_INVALID = 0x82
    ERROR_WRITING_FLASH = 0x83
    ERROR_UPDATE_END = 0x84
    ERROR_INVALID_BOOTSTRAPPING = 0x85
    ERROR_WRONG_CURRENT_FLASH_CONFIG = 0x86
    ERROR_WRONG_NEW_FLASH_CONFIG = 0x87
    ERROR_ESP8266_NOT_ENOUGH_SPACE = 0x88
    ERROR_ESP32_NOT_ENOUGH_SPACE = 0x89
    ERROR_NO_UPDATE_PARTITION = 0x8A
    ERROR_MD5_MISMATCH = 0x8B
    ERROR_UNKNOWN = 0xFF

    VERSION_1_0 = 1
    VERSION_2_0 = 2
    FEATURE_SUPPORTS_COMPRESSION = 0x01


class ESPHomeUploader:
    sock: socket | None = None
    callback: ClickProgressCallback = None

    def __init__(
        self,
        file: IO[bytes],
        host: str,
        port: int,
        password: str = None,
        callback: ClickProgressCallback = None,
    ):
        self.file = file
        self.file_size = stat(file.name).st_size
        self.host = host
        self.port = port
        self.password = password
        self.callback = callback or ClickProgressCallback()

    def resolve_host(self):
        self.callback.on_message(f"Resolving {self.host}...")
        parts = self.host.split(".")
        if all(map(lambda x: x.isnumeric(), parts)):
            if not all(map(lambda x: int(x) in range(0, 255), parts)):
                raise ValueError(f"Invalid IP address: {self.host}")
            return

        try:
            ip_addr = gethostbyname(self.host)
        except gaierror as e:
            raise RuntimeError(f"Couldn't resolve hostname {self.host} - {e}")

        info(f"Resolved {self.host} to {ip_addr}")
        self.host = ip_addr

    def connect(self):
        self.callback.on_message(f"Connecting to {self.host}:{self.port}...")
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(10.0)

        try:
            self.sock.connect((self.host, self.port))
        except OSError as e:
            self.sock.close()
            self.sock = None
            raise RuntimeError(f"Couldn't connect to {self.host}:{self.port} - {e}")

        self.sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)

    def send(self, data: Union[bytes, int, str]):
        if isinstance(data, int):
            data = bytes([data])
        if isinstance(data, str):
            data = data.encode()
        verbose(f"<-- TX: {tohex(data)[0:100]}")
        self.sock.sendall(data)

    def receive(self, *codes: OTACode, size: int = 0) -> Tuple[OTACode, bytes]:
        response = None
        if codes:
            data = self.sock.recv(1)
            response = OTACode(data[0])
            verbose(f"--> RX: {response.name}")
            if response not in codes:
                raise ValueError(f"Received {response.name} instead of {codes}")
        if size == 0:
            return response, b""
        data = self.sock.recv(size)
        verbose(f"--> RX: {tohex(data)}")
        return response, data

    def upload(self):
        self.resolve_host()
        self.connect()

        self.send(OTA_MAGIC)
        _, ver = self.receive(OTACode.RESP_OK, size=1)
        ota_version = ver[0]
        if ota_version not in (OTACode.VERSION_1_0, OTACode.VERSION_2_0):
            raise ValueError("Invalid OTA version")
        info("Connected to ESPHome")

        self.send(OTACode.FEATURE_SUPPORTS_COMPRESSION)
        features, _ = self.receive(
            OTACode.RESP_HEADER_OK,
            OTACode.RESP_SUPPORTS_COMPRESSION,
        )
        if features == OTACode.RESP_SUPPORTS_COMPRESSION:
            file_data = self.file.read()
            compressed_data = gzip.compress(file_data, compresslevel=9)
            self.file_size = len(compressed_data)
            info(f"Compressed data to {sizeof(self.file_size)}")
            self.file = BytesIO(compressed_data)

        auth, _ = self.receive(
            OTACode.RESP_AUTH_OK,
            OTACode.RESP_REQUEST_AUTH,
        )
        if auth == OTACode.RESP_REQUEST_AUTH:
            if not self.password:
                raise ValueError("OTA password required, but not specified")

            _, nonce_raw = self.receive(size=32)
            nonce = nonce_raw.decode()
            cnonce = hashlib.md5(str(random()).encode()).hexdigest()
            debug(f"Auth nonce={nonce}, cnonce={cnonce}")
            self.send(cnonce)

            md5 = hashlib.md5()
            md5.update(self.password.encode("utf-8"))
            md5.update(nonce.encode())
            md5.update(cnonce.encode())
            digest = md5.hexdigest()
            debug(f"Auth result={digest}")
            self.send(digest)

            auth, _ = self.receive(
                OTACode.RESP_AUTH_OK,
                OTACode.ERROR_AUTH_INVALID,
            )
        if auth == OTACode.ERROR_AUTH_INVALID:
            raise ValueError("Couldn't authenticate: incorrect OTA password")

        self.send(inttobe32(self.file_size))
        self.receive(OTACode.RESP_UPDATE_PREPARE_OK)

        md5 = hashlib.md5()
        md5.update(self.file.read())
        self.file.seek(0, os.SEEK_SET)
        digest = md5.hexdigest()
        debug(f"MD5 of upload is {digest}")
        self.send(digest)
        self.receive(OTACode.RESP_BIN_MD5_OK)

        self.sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 0)
        self.sock.setsockopt(SOL_SOCKET, SO_SNDBUF, UPLOAD_BUFFER_SIZE)
        self.sock.settimeout(20.0)

        self.callback.on_message("Uploading firmware file")
        self.callback.on_total(self.file_size)

        if ota_version < OTACode.VERSION_2_0:
            # allow receiving error codes during writing
            self.sock.setblocking(False)

        while True:
            data = self.file.read(UPLOAD_BLOCK_SIZE)
            if not data:
                break
            if ota_version >= OTACode.VERSION_2_0:
                self.send(data)
                self.receive(OTACode.RESP_CHUNK_OK)
            else:
                while True:
                    try:
                        data = self.sock.recv(1)
                        code = OTACode(data[0])
                        self.close()
                        raise RuntimeError(
                            f"Uploading failed: {code.name} ({code.value})"
                        )
                    except BlockingIOError:
                        pass

                    try:
                        self.send(data)
                        break
                    except BlockingIOError:
                        pass
            # sub loop breaks after successfully sending the current chunk
            self.callback.on_update(len(data))
        # main loop breaks after successfully sending the last chunk
        self.sock.setblocking(True)

        self.callback.on_message("Waiting for response...")
        self.sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        self.receive(OTACode.RESP_RECEIVE_OK)
        self.receive(OTACode.RESP_UPDATE_END_OK)
        self.send(OTACode.RESP_OK)
        self.callback.on_message("Finished")

    def close(self):
        if self.sock:
            self.sock.close()
