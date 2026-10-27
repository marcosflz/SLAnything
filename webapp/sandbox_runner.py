"""Runner aislado para ejecutar ejemplos de Python del alumnado.

Este archivo se ejecuta como un proceso independiente:

    python -I webapp/sandbox_runner.py

No forma parte del proceso web y no importa `webapp`; todo lo que necesita llega
por `stdin` y el resultado se escribe en un archivo indicado por el servidor.

La aislamiento es defensivo, no un sandbox de nivel producción:

* AST: solo se permiten imports de una lista blanca y se bloquean atributos
  peligrosos (`__class__`, `f_globals`, `format`, etc.).
* imports: se precargan los módulos permitidos antes de instalar el hook.
* auditoría: se bloquean apertura de archivos, red, procesos y `ctypes` mientras
  corre el código del usuario.
* recursos: límite de memoria, tiempo, salida y sin persistencia entre runs.

Para un despliegue público, ejecuta este proceso dentro de un contenedor sin
red y con un usuario sin privilegios, o desactiva la ejecución remota.
"""

from __future__ import annotations

import ast
import base64
import io
import json
import os
import sys
import time
from typing import Any

sys.dont_write_bytecode = True

ALLOWED_IMPORTS = {
    "collections",
    "dataclasses",
    "datetime",
    "decimal",
    "enum",
    "fractions",
    "functools",
    "html",
    "itertools",
    "json",
    "math",
    "matplotlib",
    "numpy",
    "operator",
    "pandas",
    "random",
    "re",
    "statistics",
    "string",
    "textwrap",
    "time",
    "typing",
    "unicodedata",
}

FORBIDDEN_NAMES = {
    "__builtins__",
    "__import__",
    "breakpoint",
    "classmethod",
    "compile",
    "delattr",
    "dir",
    "eval",
    "exec",
    "exit",
    "getattr",
    "globals",
    "help",
    "input",
    "locals",
    "memoryview",
    "object",
    "open",
    "property",
    "quit",
    "setattr",
    "staticmethod",
    "super",
    "type",
    "vars",
}

FORBIDDEN_ATTRS = {
    "ag_frame",
    "cr_frame",
    "f_builtins",
    "f_globals",
    "f_locals",
    "format",
    "format_map",
    "func_globals",
    "gi_frame",
    "mro",
    "tb_frame",
}

DENIED_EVENTS = {
    "builtins.breakpoint",
    "builtins.input",
    "ctypes.dlopen",
    "ctypes.dlsym",
    "os.chdir",
    "os.chmod",
    "os.chown",
    "os.exec",
    "os.fork",
    "os.forkpty",
    "os.kill",
    "os.killpg",
    "os.link",
    "os.mkdir",
    "os.putenv",
    "os.remove",
    "os.rename",
    "os.rmdir",
    "os.spawn",
    "os.system",
    "os.truncate",
    "os.unsetenv",
    "os.utime",
    "pty.spawn",
    "resource.setrlimit",
    "shutil.copyfile",
    "shutil.copymode",
    "shutil.copystat",
    "shutil.copytree",
    "shutil.move",
    "shutil.rmtree",
    "socket.__new__",
    "socket.bind",
    "socket.connect",
    "socket.getaddrinfo",
    "socket.gethostbyname",
    "socket.sendto",
    "subprocess.Popen",
    "sys.addaudithook",
    "sys.setprofile",
    "sys.settrace",
    "urllib.Request",
    "webbrowser.open",
    "winreg.CreateKey",
    "winreg.DeleteKey",
    "winreg.SetValue",
}

DENIED_EVENT_PREFIXES = (
    "ctypes.",
    "ftplib.",
    "http.",
    "msvcrt.",
    "socket.",
    "subprocess.",
    "telnetlib.",
    "urllib.",
)

_ALLOW_SERVER_OPEN = False

# Bibliotecas como pandas o matplotlib leen datos de su propio paquete al
# arrancar. Permitimos solo lecturas dentro del entorno de Python y de la caché
# de matplotlib; nunca dentro del repositorio, del HOME real o del sistema.
_READ_ROOTS = tuple(
    os.path.realpath(path)
    for path in {
        sys.prefix,
        os.path.dirname(os.__file__),
        os.environ.get("MPLCONFIGDIR", ""),
    }
    if path
)


def _open_is_allowed(args: tuple[Any, ...]) -> bool:
    if not args:
        return False
    path = args[0]
    mode = args[1] if len(args) > 1 else "r"
    if isinstance(path, int):
        # `os.fdopen` sobre un descriptor ya abierto por una biblioteca de
        # confianza. El código del usuario no puede abrir descriptores nuevos.
        return not (isinstance(mode, str) and any(flag in mode for flag in "wax+"))
    try:
        path = os.fsdecode(path)
    except (TypeError, ValueError):
        return False
    if isinstance(mode, str) and any(flag in mode for flag in "wax+"):
        return False
    try:
        real = os.path.realpath(path)
    except (OSError, ValueError):
        return False
    for root in _READ_ROOTS:
        try:
            if os.path.commonpath([real, root]) == root:
                return True
        except ValueError:
            continue
    return False


class SecurityError(Exception):
    """El código intentó usar una capacidad no permitida."""


class LimitedWriter(io.TextIOBase):
    """TextIO que corta la salida para no llenar la memoria del servidor."""

    def __init__(self, limit: int) -> None:
        super().__init__()
        self._limit = limit
        self._parts: list[str] = []
        self._size = 0
        self.truncated = False

    def write(self, value: str) -> int:
        if not isinstance(value, str):
            value = str(value)
        if self._size >= self._limit:
            self.truncated = True
            return len(value)
        remaining = self._limit - self._size
        if len(value) > remaining:
            value = value[:remaining]
            self.truncated = True
        self._parts.append(value)
        self._size += len(value)
        return len(value)

    def flush(self) -> None:  # pragma: no cover - interfaz de io
        return None

    def getvalue(self) -> str:
        return "".join(self._parts)


def _root_module(name: str) -> str:
    return (name or "").split(".")[0]


def validate_ast(code: str) -> ast.Module:
    """Valida el árbol sintáctico antes de ejecutar una sola línea."""
    tree = ast.parse(code, filename="<tu-código>", mode="exec")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _root_module(alias.name) not in ALLOWED_IMPORTS:
                    raise SecurityError(f"import no permitido: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise SecurityError("no se permiten imports relativos")
            root = _root_module(node.module or "")
            if root not in ALLOWED_IMPORTS:
                raise SecurityError(f"import no permitido: {node.module}")
        elif isinstance(node, ast.Name):
            if node.id in FORBIDDEN_NAMES or node.id.startswith("__"):
                raise SecurityError(f"nombre no permitido: {node.id}")
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("_") or node.attr in FORBIDDEN_ATTRS:
                raise SecurityError(f"atributo no permitido: {node.attr}")
        elif isinstance(node, ast.ClassDef):
            raise SecurityError("no se permiten definiciones de clases")
        elif isinstance(node, (ast.AsyncFunctionDef, ast.Await, ast.AsyncFor, ast.AsyncWith)):
            raise SecurityError("no se permite código asíncrono")
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            raise SecurityError("no se permiten variables globales")
        elif isinstance(node, ast.FunctionDef) and node.name.startswith("__"):
            raise SecurityError("no se permiten métodos especiales")
    return tree


def _preload_modules(tree: ast.Module) -> None:
    """Carga los módulos permitidos antes de activar el hook de auditoría."""
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(_root_module(alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            roots.add(_root_module(node.module or ""))
    if "matplotlib" in roots:
        import warnings

        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot  # noqa: F401

        warnings.filterwarnings(
            "ignore", message="FigureCanvasAgg is non-interactive"
        )
    if "numpy" in roots:
        import numpy  # noqa: F401
    if "pandas" in roots:
        import pandas  # noqa: F401
        import pandas.io.formats.html  # noqa: F401
        import pandas.io.formats.string  # noqa: F401
    for root in roots - {"matplotlib", "numpy", "pandas"}:
        if root in ALLOWED_IMPORTS:
            __import__(root)


def _limit_resources(memory_mb: int, seconds: int) -> None:
    """Aplica límites de memoria y CPU cuando la plataforma lo permite."""
    if os.name == "nt":
        _limit_windows_memory(memory_mb)
        return
    try:
        import resource

        limit = max(128, memory_mb) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        cpu = max(2, seconds)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
    except (ImportError, OSError, ValueError):
        pass


def _limit_windows_memory(memory_mb: int) -> None:
    """Crea un Job Object con límite de memoria para este proceso."""
    try:
        import ctypes
        from ctypes import wintypes
    except ImportError:  # pragma: no cover - plataformas sin ctypes
        return

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        job = kernel32.CreateJobObjectW(None, None)
        if not job:
            return
        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = 0x00000100 | 0x00002000
        info.ProcessMemoryLimit = max(128, memory_mb) * 1024 * 1024
        kernel32.SetInformationJobObject(
            job,
            9,  # JobObjectExtendedLimitInformation
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
        kernel32.AssignProcessToJobObject(job, kernel32.GetCurrentProcess())
        # El handle debe seguir vivo: KILL_ON_JOB_CLOSE termina el proceso.
        globals()["_WINDOWS_JOB_HANDLE"] = job
    except (AttributeError, OSError, ValueError):
        pass


def _install_audit_hook() -> None:
    def hook(event: str, args: tuple[Any, ...]) -> None:
        if event == "open" and _ALLOW_SERVER_OPEN:
            return
        if event == "open" and _open_is_allowed(args):
            return
        if event == "open":
            raise SecurityError(f"apertura bloqueada por seguridad: {args!r}")
        if event in DENIED_EVENTS:
            raise SecurityError(f"operación bloqueada por seguridad: {event}")
        if event.startswith(DENIED_EVENT_PREFIXES):
            raise SecurityError(f"operación bloqueada por seguridad: {event}")

    sys.addaudithook(hook)


def _import_guard(name: str, globals=None, locals=None, fromlist=(), level=0):
    if level:
        raise SecurityError("no se permiten imports relativos")
    root = _root_module(name)
    if root not in ALLOWED_IMPORTS:
        raise SecurityError(f"import no permitido: {name}")
    if fromlist:
        module = sys.modules.get(name) or sys.modules.get(root)
        if module is None:
            raise ImportError(f"módulo no disponible: {name}")
        return module
    module = sys.modules.get(root)
    if module is None:
        raise ImportError(f"módulo no disponible: {root}")
    return module


def _safe_builtins(
    outputs: list[dict[str, Any]],
    images: list[dict[str, Any]],
    data: dict[str, str],
):
    def mostrar(*objetos: Any, **kwargs: Any) -> None:
        for objeto in objetos:
            _render_value(objeto, outputs, images)

    def leer_recurso(nombre: str) -> str:
        """Devuelve un recurso de datos de solo lectura del curso."""
        if nombre not in data:
            disponibles = ", ".join(sorted(data)) or "ninguno"
            raise FileNotFoundError(
                f"Recurso no disponible: {nombre}. Disponibles: {disponibles}"
            )
        return data[nombre]

    allowed = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "chr": chr,
        "dict": dict,
        "display": mostrar,
        "divmod": divmod,
        "enumerate": enumerate,
        "filter": filter,
        "float": float,
        "frozenset": frozenset,
        "int": int,
        "isinstance": isinstance,
        "issubclass": issubclass,
        "leer_recurso": leer_recurso,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "next": next,
        "ord": ord,
        "print": print,
        "range": range,
        "repr": repr,
        "reversed": reversed,
        "round": round,
        "set": set,
        "slice": slice,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
        "Exception": Exception,
        "IndexError": IndexError,
        "KeyError": KeyError,
        "StopIteration": StopIteration,
        "TypeError": TypeError,
        "ValueError": ValueError,
        "ZeroDivisionError": ZeroDivisionError,
        "__import__": _import_guard,
    }
    return allowed


def _is_dataframe(obj: Any) -> bool:
    module = type(obj).__module__
    return module.startswith("pandas") and hasattr(obj, "to_html")


def _table_html(obj: Any) -> str:
    frame = getattr(obj, "data", obj)
    if hasattr(frame, "to_html"):
        return frame.to_html(
            index=False,
            border=0,
            escape=True,
            classes="py-table",
            justify="left",
        )
    return f"<pre>{_escape(str(obj))}</pre>"


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _load_data(data_dir: str | None) -> dict[str, str]:
    """Precarga los recursos de datos antes de activar el hook de auditoría."""
    if not data_dir:
        return {}
    data: dict[str, str] = {}
    path = os.path.join(data_dir, "quijote_fragmento.txt")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data["quijote_fragmento.txt"] = handle.read()
    except OSError:
        pass
    return data


def _render_value(obj: Any, outputs: list[dict[str, Any]], images: list[dict[str, Any]]) -> None:
    if obj is None:
        return
    if _is_dataframe(obj):
        outputs.append({"type": "table", "html": _table_html(obj)})
        return
    module = type(obj).__module__
    if module.startswith("matplotlib") and hasattr(obj, "savefig"):
        _save_figure(obj, images)
        return
    text = repr(obj)
    if len(text) > 8000:
        text = text[:8000] + "…"
    outputs.append({"type": "text", "text": text})


def _save_figure(figure: Any, images: list[dict[str, Any]]) -> None:
    buffer = io.BytesIO()
    try:
        figure.savefig(buffer, format="png", bbox_inches="tight", dpi=120)
        images.append(
            {
                "type": "image",
                "mime": "image/png",
                "data": base64.b64encode(buffer.getvalue()).decode("ascii"),
            }
        )
    except Exception:
        pass


def _capture_figures(images: list[dict[str, Any]]) -> None:
    if "matplotlib.pyplot" not in sys.modules:
        return
    try:
        import matplotlib.pyplot as plt

        for number in plt.get_fignums():
            figure = plt.figure(number)
            _save_figure(figure, images)
        plt.close("all")
    except Exception:
        pass


def _run(code: str, config: dict[str, Any]) -> dict[str, Any]:
    global _ALLOW_SERVER_OPEN

    started = time.monotonic()
    try:
        tree = validate_ast(code)
    except SyntaxError as exc:
        return {
            "ok": False,
            "error": f"SyntaxError: {exc.msg} (línea {exc.lineno})",
            "stdout": "",
            "outputs": [],
        }
    except SecurityError as exc:
        return {"ok": False, "error": str(exc), "stdout": "", "outputs": []}

    _preload_modules(tree)

    stdout = LimitedWriter(int(config.get("max_output", 20_000)))
    stderr = LimitedWriter(int(config.get("max_output", 20_000)))
    outputs: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    builtins = _safe_builtins(outputs, images, _load_data(config.get("data_dir")))
    namespace: dict[str, Any] = {"__name__": "__main__", "__builtins__": builtins}

    _limit_resources(
        int(config.get("memory_mb", 512)),
        int(config.get("timeout_seconds", 10)),
    )
    _install_audit_hook()

    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = stdout, stderr
    error = None
    try:
        body = tree.body
        last_expression = None
        if body and isinstance(body[-1], ast.Expr):
            last_expression = body.pop()
        if body:
            exec(compile(tree, "<tu-código>", "exec"), namespace)  # noqa: S102
        if last_expression is not None:
            value = eval(  # noqa: S307
                compile(ast.Expression(last_expression.value), "<tu-código>", "eval"),
                namespace,
            )
            _render_value(value, outputs, images)
    except SecurityError as exc:
        error = f"SecurityError: {exc}"
    except BaseException as exc:  # noqa: BLE001 - el runner debe capturar todo
        error = f"{type(exc).__name__}: {exc}"
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        _capture_figures(images)

    if stdout.truncated or stderr.truncated:
        notice = "\n[la salida se ha truncado]\n"
        outputs.append({"type": "text", "text": notice.strip()})

    result = {
        "ok": error is None,
        "error": error,
        "stdout": stdout.getvalue(),
        "stderr": stderr.getvalue(),
        "outputs": outputs + images,
        "duration_ms": int((time.monotonic() - started) * 1000),
    }

    return result


def main() -> int:
    payload = json.load(sys.stdin)
    code = payload.get("code", "")
    result_path = payload["result_path"]
    try:
        result = _run(code, payload)
    except BaseException as exc:  # noqa: BLE001 - nunca dejamos el archivo sin escribir
        result = {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "stdout": "",
            "outputs": [],
            "duration_ms": 0,
        }
    try:
        globals()["_ALLOW_SERVER_OPEN"] = True
        with open(result_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
