"""Guest client — connects to a host and exchanges messages in a background thread."""
import queue
import select
import socket
import threading

from networking.protocol import (PORT, PROTOCOL_VERSION,
                                  MSG_HELLO, MSG_WELCOME, MSG_BYE,
                                  send_msg, recv_msg)


class GuestClient:
    """
    Manages the client (guest) side of a 2-player session.

    Usage
    -----
        client = GuestClient(guest_name)
        ok, err = client.connect(host_ip)   # blocking handshake (short timeout)
        if ok:
            # client.host_player_dict is now populated from welcome message
            client.start_loop()             # start background read/write thread
        # ... later in game loop:
        for (msg_type, data) in client.poll():
            ...
        client.send(msg_type, data)
        client.stop()
    """

    def __init__(self, guest_name: str, guest_player_dict: dict):
        self._name        = guest_name
        self._player_dict = guest_player_dict
        self._sock: socket.socket | None = None
        self._in_q:  queue.Queue = queue.Queue()
        self._out_q: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None
        self._running = False
        self.host_name: str = ""
        self.host_player_dict: dict = {}
        self.connected = False
        self.error: str = ""

    # ── Public API ────────────────────────────────────────────────────────────

    def connect(self, host_ip: str, timeout: float = 15.0):
        """
        Blocking connect + handshake.
        Returns (True, "") on success or (False, error_string) on failure.
        """
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(timeout)
            self._sock.connect((host_ip, PORT))
            send_msg(self._sock, MSG_HELLO, {
                "name":    self._name,
                "version": PROTOCOL_VERSION,
            })
            mtype, data = recv_msg(self._sock)
            if mtype != MSG_WELCOME:
                self._sock.close()
                return False, f"Unexpected response: {mtype}"
            self.host_player_dict = data.get("player_dict", {})
            self.host_name        = data.get("host_name", "Host")
            self._sock.settimeout(None)
            self.connected = True
            return True, ""
        except OSError as exc:
            self.error = str(exc)
            try:
                self._sock.close()
            except OSError:
                pass
            return False, str(exc)

    def start_loop(self) -> None:
        """Start the background send/receive thread (call after connect)."""
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        try:
            if self._sock:
                send_msg(self._sock, MSG_BYE)
                self._sock.close()
        except OSError:
            pass

    def send(self, msg_type: str, data: dict = None) -> None:
        self._out_q.put((msg_type, data or {}))

    def poll(self) -> list:
        msgs = []
        while not self._in_q.empty():
            try:
                msgs.append(self._in_q.get_nowait())
            except queue.Empty:
                break
        return msgs

    # ── Background thread ─────────────────────────────────────────────────────

    def _loop(self) -> None:
        sock = self._sock
        sock.setblocking(False)
        try:
            while self._running:
                # Send outgoing
                while not self._out_q.empty():
                    try:
                        mtype, data = self._out_q.get_nowait()
                        sock.setblocking(True)
                        send_msg(sock, mtype, data)
                        sock.setblocking(False)
                    except (queue.Empty, OSError):
                        break

                # Receive incoming
                rlist, _, _ = select.select([sock], [], [], 0.05)
                if rlist:
                    sock.setblocking(True)
                    mtype, data = recv_msg(sock)
                    sock.setblocking(False)
                    if mtype is None:
                        break
                    if mtype == MSG_BYE:
                        break
                    self._in_q.put((mtype, data))
        except OSError as exc:
            self.error = str(exc)
        finally:
            self.connected = False
            try:
                sock.close()
            except OSError:
                pass
