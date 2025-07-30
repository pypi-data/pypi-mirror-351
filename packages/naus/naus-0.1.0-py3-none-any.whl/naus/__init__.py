import threading
import dataclasses
from dataclasses import dataclass
import struct
from copy import deepcopy

import zmq
import numpy as np
import cv2 as cv
from cv2.typing import MatLike


@dataclass(frozen=True)
class Telemetry:
    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    roll: float


class AUV:
    _auv_id: int
    _ctx: zmq.Context
    _image_socket: zmq.Socket
    _thrust_socket: zmq.Socket
    _telemetry_socket: zmq.Socket

    _image_bottom: MatLike | None
    _image_front: MatLike | None
    _images_lock: threading.Lock
    _images_ready: threading.Event

    _telemetry: Telemetry
    _telemetry_lock: threading.Lock
    _telemetry_ready: threading.Event

    def __init__(self, auv_id: int):
        assert 0 <= auv_id <= 255

        self._auv_id = auv_id

        self._ctx = zmq.Context()

        self._image_front = None
        self._image_bottom = None
        self._images_lock = threading.Lock()
        self._images_ready = threading.Event()

        self._telemetry = None  # type: ignore
        self._telemetry_lock = threading.Lock()
        self._telemetry_ready = threading.Event()

        self._image_socket = self._ctx.socket(zmq.SUB)
        self._image_socket.connect("tcp://localhost:5555")
        self._image_socket.subscribe(bytes([self._auv_id]))

        self._thrust_socket = self._ctx.socket(zmq.PUSH)
        self._thrust_socket.connect("tcp://localhost:5556")

        self._telemetry_socket = self._ctx.socket(zmq.SUB)
        self._telemetry_socket.connect("tcp://localhost:5557")
        self._telemetry_socket.subscribe(bytes([self._auv_id]))

        threading.Thread(target=self._images_listener, daemon=True).start()
        threading.Thread(target=self._telemetry_listener, daemon=True).start()

    def _images_listener(self):
        while True:
            _auv_id, msg_front, msg_bottom = self._image_socket.recv_multipart(0)

            data_front, data_bottom = (
                np.frombuffer(msg_front, np.uint8),
                np.frombuffer(msg_bottom, np.uint8),
            )

            with self._images_lock:
                self._img_front = cv.imdecode(data_front, cv.IMREAD_COLOR)
                self._img_bottom = cv.imdecode(data_bottom, cv.IMREAD_COLOR)
            self._images_ready.set()

    def _telemetry_listener(self):
        while True:
            _auv_id, raw = self._telemetry_socket.recv_multipart(0)

            x: float
            y: float
            z: float
            yaw: float
            pitch: float
            roll: float
            x, y, z, yaw, pitch, roll = struct.unpack("<ffffff", raw)

            with self._telemetry_lock:
                self._telemetry = Telemetry(x, y, z, yaw, pitch, roll)
            self._telemetry_ready.set()

    def get_images(self) -> tuple[MatLike, MatLike]:
        self._images_ready.wait()
        with self._images_lock:
            return (deepcopy(self._img_front), deepcopy(self._img_bottom))

    def get_telemetry(self) -> Telemetry:
        self._telemetry_ready.wait()
        with self._telemetry_lock:
            return dataclasses.replace(self._telemetry)

    def set_motor_powers(
        self,
        *,
        left: int | None = None,
        right: int | None = None,
        side: int | None = None,
        vertical: int | None = None,
    ) -> None:
        assert (left is None) or (-100 <= left <= 100)
        assert (right is None) or (-100 <= right <= 100)
        assert (side is None) or (-100 <= side <= 100)
        assert (vertical is None) or (-100 <= vertical <= 100)

        self._thrust_socket.send(
            struct.pack(
                "Bbbbb",
                self._auv_id,
                left if left is not None else -127,
                right if right is not None else -127,
                side if side is not None else -127,
                vertical if vertical is not None else -127,
            )
        )
