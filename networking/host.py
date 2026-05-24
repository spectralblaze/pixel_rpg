"""Host server — runs in a background thread, accepts one guest."""
import queue
import select
import socket
import subprocess
import sys
import threading

from networking.protocol import (PORT, PROTOCOL_VERSION,
                                  MSG_HELLO, MSG_WELCOME, MSG_BYE,
                                  send_msg, recv_msg)


def _add_firewall_rule() -> None:
    """Best-effort: add a Windows Firewall inbound rule for our TCP port.
    Silent on any error or on non-Windows systems."""
    if sys.platform != "win32":
        return
    try:
        rule_name = f"LegendsCursedRealm_TCP_{PORT}"
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule",
             f"name={rule_name}",
             "protocol=TCP", f"localport={PORT}",
             "action=allow", "dir=in", "enable=yes"],
            capture_output=True, timeout=6,
        )
    except Exception:
        pass


class HostServer:
    """
    Manages the server side of a 2-player session.

    Usage
    -----
        server = HostServer(host_player_dict, host_name)
        server.start()          # opens TCP listener on PORT
        # ... later in game loop:
        for (msg_type, data) in server.poll():
            ...                 # handle incoming messages
        server.send(msg_type, data)   # send to guest
        server.stop()
    """

    def __init__(self, host_player_dict: dict, host_name: str):
        self._host_dict  = host_player_dict
        self._host_name  = host_name
        self._in_q:  queue.Queue = queue.Queue()   # messages FROM guest
        self._out_q: queue.Queue = queue.Queue()   # messages TO   guest
        self._listen_sock: socket.socket | None = None
        self._guest_sock:  socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        self.guest_name: str = ""
        self.connected  = False     # True once handshake done
        self.listening  = False     # True once socket is bound and accept()-ready
        self.error: str = ""

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Open the TCP listener and start the background thread."""
        _add_firewall_rule()   # silently poke Windows Firewall (no-op on non-Windows)
        self._running = True
        self._thread  = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        try:
            if self._guest_sock:
                send_msg(self._guest_sock, MSG_BYE)
                self._guest_sock.close()
        except OSError:
            pass
        try:
            if self._listen_sock:
                self._listen_sock.close()
        except OSError:
            pass

    def send(self, msg_type: str, data: dict = None) -> None:
        """Queue a message to send to the guest (non-blocking)."""
        self._out_q.put((msg_type, data or {}))

    def poll(self) -> list:
        """Drain and return all messages received from the guest since last call."""
        msgs = []
        while not self._in_q.empty():
            try:
                msgs.append(self._in_q.get_nowait())
            except queue.Empty:
                break
        return msgs

    # ── Background thread ─────────────────────────────────────────────────────

    def _run(self) -> None:
        try:
            self._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._listen_sock.bind(("0.0.0.0", PORT))
            self._listen_sock.listen(1)
            self._listen_sock.setblocking(False)
            self.listening = True   # server is ready for incoming connections

            # Wait for one guest to connect
            while self._running and self._guest_sock is None:
                rlist, _, _ = select.select([self._listen_sock], [], [], 0.2)
                if rlist:
                    self._guest_sock, addr = self._listen_sock.accept()
                    self._guest_sock.setblocking(True)
                    self._handshake()

            if not self._running:
                return

            # Main read/write loop
            self._listen_sock.close()
            self._listen_sock = None
            self._loop()

        except OSError as exc:
            self.error = str(exc)
        finally:
            self._running = False

    def _handshake(self) -> None:
        mtype, data = recv_msg(self._guest_sock)
        if mtype != MSG_HELLO:
            self._guest_sock.close()
            self._guest_sock = None
            return
        self.guest_name = data.get("name", "Guest")
        send_msg(self._guest_sock, MSG_WELCOME, {
            "player_dict": self._host_dict,   # give guest a copy of host save
            "host_name":   self._host_name,
            "version":     PROTOCOL_VERSION,
        })
        self.connected = True

    def _loop(self) -> None:
        sock = self._guest_sock
        sock.setblocking(False)
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
                    break   # disconnected
                if mtype == MSG_BYE:
                    break
                self._in_q.put((mtype, data))

        self.connected = False
        try:
            self._guest_sock.close()
        except OSError:
            pass
        self._guest_sock = None
