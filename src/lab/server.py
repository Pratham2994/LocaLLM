"""Start and stop llama-server, wait until it is healthy, and parse its startup log."""

import os
import re
import socket
import subprocess
import time
from pathlib import Path

import requests

# e.g. "load_tensors:      Vulkan0 model buffer size =  2603.50 MiB"
#      "llama_kv_cache:    Vulkan0 KV buffer size =   256.00 MiB"
BUFFER_RE = re.compile(r"(\S+)\s+(model|KV|RS|compute|output) buffer size =\s*([\d.]+) MiB")
BUILD_RE = re.compile(r"build (\d+) \(([0-9a-f]+)\)")
FILE_RE = re.compile(r"file size\s*=\s*([\d.]+) GiB \(([\d.]+) BPW\)")


class ServerError(RuntimeError):
    pass


def port_in_use(host: str, port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def parse_log(text: str) -> dict:
    """Pull build number, bits per weight and buffer sizes (MiB per device) from the log.

    The log can hold several model loads (e.g. main model + MTP draft model), and one model
    can have several KV caches (Gemma 4: full-attention + sliding-window). So, per model load:
    model/KV/RS lines add up, while a repeated compute/output line (a re-reserve) replaces the
    earlier one. The loads are then added together.
    """
    buffers: dict[str, dict[str, float]] = {}
    for load in re.split(r"(?=llama_model_loader: loaded meta data)", text):
        per_load: dict[str, dict[str, float]] = {}
        for device, kind, mib in BUFFER_RE.findall(load):
            cell = per_load.setdefault(kind.lower(), {})
            additive = kind.lower() in ("model", "kv", "rs")
            cell[device] = (cell.get(device, 0.0) if additive else 0.0) + float(mib)
        for kind, devices in per_load.items():
            for device, mib in devices.items():
                total = buffers.setdefault(kind, {})
                total[device] = round(total.get(device, 0.0) + mib, 2)
    info: dict = {"buffers_mib": buffers}
    if m := BUILD_RE.search(text):
        info["build"], info["commit"] = int(m[1]), m[2]
    if m := FILE_RE.search(text):
        info["file_gib"], info["bpw"] = float(m[1]), float(m[2])
    return info


def system_available_gib() -> float | None:
    """Physical RAM that Windows can still give to programs (free + standby), in GiB."""
    if os.name != "nt":
        return None
    import ctypes

    class MemoryStatus(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
            (name, ctypes.c_ulonglong) for name in
            ("total_phys", "avail_phys", "total_page", "avail_page", "total_virtual", "avail_virtual", "avail_ext")]

    status = MemoryStatus(length=ctypes.sizeof(MemoryStatus))
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None
    return round(status.avail_phys / 2**30, 2)


def process_memory_gib(handle: int) -> dict:
    """RAM of one process: `working_set` = in physical RAM now (for a model: the weights kept in RAM and the
    part of the mapped file Windows has not trimmed yet); `private` = memory only this process can use
    (it includes what Windows reserves against the GPU memory)."""
    if os.name != "nt":
        return {}
    import ctypes

    class Counters(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("page_faults", ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in
            ("peak_working_set", "working_set", "quota_peak_paged", "quota_paged", "quota_peak_nonpaged",
             "quota_nonpaged", "pagefile", "peak_pagefile", "private")]

    counters = Counters(cb=ctypes.sizeof(Counters))
    get = ctypes.windll.psapi.GetProcessMemoryInfo
    get.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
    if not get(handle, ctypes.byref(counters), counters.cb):
        return {}
    return {"working_set_gib": round(counters.working_set / 2**30, 2),
            "peak_working_set_gib": round(counters.peak_working_set / 2**30, 2),
            "private_gib": round(counters.private / 2**30, 2)}


def gpu_used_mib() -> int | None:
    """GPU memory in use by all programs (model + desktop), from nvidia-smi; None if there is no such tool."""
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=10).stdout
        return int(out.strip().splitlines()[0])
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        return None


def _same_file(a: str, b: Path) -> bool:
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


class LlamaServer:
    """Context manager: start the server, block until /health is OK, stop it on exit."""

    def __init__(self, cmd: list[str], base_url: str, host: str, port: int, model: Path,
                 log_path: Path, health_timeout_s: float):
        self.cmd, self.base_url, self.host, self.port = cmd, base_url, host, port
        self.model, self.log_path, self.health_timeout_s = model, log_path, health_timeout_s
        self.proc: subprocess.Popen | None = None
        self.info: dict = {}

    def memory(self) -> dict:
        """Memory with the model loaded: the server process, what is left for other programs, the GPU."""
        if not self.alive():
            return {}
        return {**process_memory_gib(int(self.proc._handle)),  # type: ignore[union-attr]
                "system_available_gib": system_available_gib(),
                "system_available_before_gib": self.available_before_gib,
                "gpu_used_mib": gpu_used_mib()}

    def __enter__(self) -> "LlamaServer":
        self.available_before_gib = system_available_gib()
        if port_in_use(self.host, self.port):
            raise ServerError(
                f"port {self.port} is already in use. Stop the old llama-server first: "
                "otherwise the harness would measure that server instead of this config."
            )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log = open(self.log_path, "w", encoding="utf-8")
        t0 = time.perf_counter()
        self.proc = subprocess.Popen(self.cmd, stdout=self._log, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL)
        try:
            self._wait_healthy()
            self._check_model()
        except BaseException:
            self.stop()
            raise
        self.info = parse_log(self.log_path.read_text(encoding="utf-8", errors="replace"))
        self.info["load_s"] = round(time.perf_counter() - t0, 2)
        return self

    def __exit__(self, *exc) -> None:
        self.stop()

    def _wait_healthy(self) -> None:
        assert self.proc is not None
        deadline = time.perf_counter() + self.health_timeout_s
        while time.perf_counter() < deadline:
            if self.proc.poll() is not None:
                raise ServerError(f"llama-server exited with code {self.proc.returncode} "
                                  f"while loading; last log lines:\n{self.log_tail()}")
            try:
                if requests.get(f"{self.base_url}/health", timeout=2).status_code == 200:
                    return
            except requests.RequestException:
                pass
            time.sleep(0.25)
        raise ServerError(f"llama-server not healthy after {self.health_timeout_s}s")

    def _check_model(self) -> None:
        props = requests.get(f"{self.base_url}/props", timeout=10).json()
        if not _same_file(props.get("model_path", ""), self.model):
            raise ServerError(f"server reports model {props.get('model_path')!r}, expected {self.model}")

    def log_tail(self, n: int = 15) -> str:
        lines = self.log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n:])

    def alive(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        if getattr(self, "_log", None) and not self._log.closed:
            self._log.close()
