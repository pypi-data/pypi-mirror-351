import os
import sys
import time
import inspect
import logging
import asyncio
import threading
import importlib
import functools

from .sigils import Resolver
from .structs import Results


class Gateway(Resolver):
    _builtin_cache = None
    _thread_local = threading.local()

    def __init__(self, *, verbose=False, name="gw", _debug=False, **kwargs):

        self._cache = {}
        self._async_threads = []
        self._debug = _debug
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.name = name
        self.logger = logging.getLogger(name)
        if not verbose:
            self.verbose =  lambda *_, **__: None
        elif verbose is True:
            self.verbose =  lambda *args, **kwargs: self.info(*args, **kwargs)

        # Thread-local context/results
        if not hasattr(Gateway._thread_local, "context"):
            Gateway._thread_local.context = {}
        if not hasattr(Gateway._thread_local, "results"):
            Gateway._thread_local.results = Results()

        # Inject initial context if provided
        Gateway._thread_local.context.update(kwargs)

        # Aliases for convenience
        self.context = Gateway._thread_local.context
        self.results = Gateway._thread_local.results

        # Resolver setup
        super().__init__([
            ('results', self.results),
            ('context', self.context),
            ('env', os.environ),
        ])

        # Cache builtins once
        if Gateway._builtin_cache is None:
            builtins_module = importlib.import_module("gway.builtins")
            Gateway._builtin_cache = {
                name: obj for name, obj in inspect.getmembers(builtins_module)
                if inspect.isfunction(obj)
                and not name.startswith("_")
                and inspect.getmodule(obj) == builtins_module
            }

        self._builtin_functions = Gateway._builtin_cache.copy()

    def success(self, message):
        print(message)
        self.info(message)

    def _wrap_callable(self, func_name, func_obj):
        @functools.wraps(func_obj)
        def wrapped(*args, **kwargs):
            try:
                self.debug(f"Call <{func_name}>: {args=} {kwargs=}")
                sig = inspect.signature(func_obj)
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
                # self.debug(f"Context before argument injection: {self.context}")

                for param in sig.parameters.values():
                    if param.name not in bound_args.arguments and param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                        default_value = param.default
                        if isinstance(default_value, str) and default_value.startswith("[") and default_value.endswith("]"):
                            resolved = self.resolve(default_value)
                            bound_args.arguments[param.name] = resolved

                # Use explicit kwargs provided to override existing context
                for key, value in bound_args.arguments.items():
                    if isinstance(value, str):
                        resolved = self.resolve(value)
                        bound_args.arguments[key] = resolved
                    self.context[key] = bound_args.arguments[key]

                # Prepare args and kwargs for function call
                args_to_pass = []
                kwargs_to_pass = {}
                for param in sig.parameters.values():
                    # self.debug(f"Preparing {param=}")
                    if param.kind == param.VAR_POSITIONAL:
                        bound_val = bound_args.arguments.get(param.name, ())
                        # self.debug(f"Kind == VAR_POSITIONAL {bound_val=} -> extend args")
                        args_to_pass.extend(bound_val)
                    elif param.kind == param.VAR_KEYWORD:
                        bound_val = bound_args.arguments.get(param.name, {})
                        # self.debug(f"Kind == VAR_KEYWORD {bound_val=} -> extend kwargs")
                        kwargs_to_pass.update(bound_val)
                    elif param.name in bound_args.arguments:
                        bound_val = bound_args.arguments[param.name]
                        if param.default == bound_val:
                            found_val = self.find_value(param.name)
                            # self.debug(f"Checking override: {bound_val=} == {param.default=} => {found_val=}")
                            if found_val is not None and found_val != bound_val:
                                self.info(f"Injected {param.name}={found_val} overrides default {bound_val=}")
                                bound_val = found_val
                        else:
                            self.debug(f"Value for {param.name} differs from default "
                                       f"({param.default=}); using provided {bound_val=}")
                        kwargs_to_pass[param.name] = bound_val
                    else:
                        self.debug(f"No preparation procedure matched for {param.name}")

                # Handle coroutine function
                if inspect.iscoroutinefunction(func_obj):
                    thread = threading.Thread(
                        target=self._run_coroutine,
                        args=(func_name, func_obj, args_to_pass, kwargs_to_pass),
                        daemon=True
                    )
                    self._async_threads.append(thread)
                    thread.start()
                    return f"[async task started for {func_name}]"

                # Call synchronous function
                result = func_obj(*args_to_pass, **kwargs_to_pass)

                # Handle coroutine result from sync function
                if inspect.iscoroutine(result):
                    thread = threading.Thread(
                        target=self._run_coroutine,
                        args=(func_name, result),
                        daemon=True
                    )
                    self._async_threads.append(thread)
                    thread.start()
                    return f"[async coroutine started for {func_name}]"

                # Store result

                if result is not None:
                    sk = func_name.split("_")[-1] if "_" in func_name else func_name
                    lk = func_name.split("_", 1)[-1] if "_" in func_name else func_name
                    self.info(f"Stored {result=} into {sk=} {lk=} ")
                    self.results.insert(sk, result)
                    if lk != sk:
                        self.results.insert(lk, result)
                    if isinstance(result, dict):
                        self.context.update(result)
                else:
                    self.debug("Result is None, skip storing.")

                return result

            except Exception as e:
                self.error(f"Error in '{func_name}': {e}")
                raise

        return wrapped
        
    def _run_coroutine(self, func_name, coro_or_func, args=None, kwargs=None):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Determine if it's already a coroutine object
            if asyncio.iscoroutine(coro_or_func):
                result = loop.run_until_complete(coro_or_func)
            else:
                result = loop.run_until_complete(coro_or_func(*(args or ()), **(kwargs or {})))

            self.results.insert(func_name, result)
            if isinstance(result, dict):
                self.context.update(result)
        except Exception as e:
            self.error(f"Async error in {func_name}: {e}")
            self.exception(e)
        finally:
            loop.close()

    def until(self, *, lock_file=None, lock_url=None, lock_pypi=False):
        from .watchers import watch_file, watch_url, watch_pypi_package
        def shutdown(reason):
            self.warning(f"{reason} triggered async shutdown.")
            os._exit(1)

        watchers = [
            (lock_file, watch_file, "Lock file"),
            (lock_url, watch_url, "Lock url"),
            (lock_pypi if lock_pypi is not False else None, watch_pypi_package, "PyPI package")
        ]
        for target, watcher, reason in watchers:
            if target:
                self.info(f"Setup watcher for {reason}")
                if target is True and lock_pypi:
                    target = "gway"
                watcher(target, on_change=lambda r=reason: shutdown(r))
        try:
            while any(thread.is_alive() for thread in self._async_threads):
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.critical("KeyboardInterrupt received. Exiting immediately.")
            os._exit(1)

    def __getattr__(self, name):
        # Delegate standard logger methods to self.logger
        if hasattr(self.logger, name) and callable(getattr(self.logger, name)):
            return getattr(self.logger, name)

        # Builtin function?
        if name in self._builtin_functions:
            func = self._wrap_callable(name, self._builtin_functions[name])
            setattr(self, name, func)
            return func

        # Cached project?
        if name in self._cache: return self._cache[name]

        # Attempt dynamic project loading via load_project
        try:
            project_obj = self.load_project(project_name=name)
            return project_obj
        except Exception as e:
            raise AttributeError(f"Project or builtin '{name}' not found: {e}")

    def load_project(self, project_name: str, *, root: str = "projects"):
        # Replace hyphens with underscores in module names
        project_name = project_name.replace("-", "_")
        project_path = gw.resource(root, *project_name.split("."))
        self.debug(f"Load {project_name=} under {root=} -> {project_path}")

        # Determine if it's a package or module
        if os.path.isdir(project_path) and os.path.isfile(os.path.join(project_path, "__init__.py")):
            # It's a package
            project_file = os.path.join(project_path, "__init__.py")
            module_name = project_name.replace(".", "_")
        else:
            # It's a single module
            project_file = str(project_path) + ".py"
            if not os.path.isfile(project_file):
                raise FileNotFoundError(f"Project file or package not found: {project_file}")
            module_name = project_name.replace(".", "_")

        # Load spec
        spec = importlib.util.spec_from_file_location(module_name, project_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for {project_name!r} from {project_file}")

        project_module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = project_module  # so relative imports work

        # === NEW: wrap exec_module to catch ImportError and log it ===
        try:
            spec.loader.exec_module(project_module)
        except Exception as e:
            self.error(f"Failed to import project '{project_name}' from {project_file}: {e}", exc_info=True)
            # re-raise so caller sees it
            raise

        # Collect all public functions
        project_functions = {
            name: obj
            for name, obj in inspect.getmembers(project_module, inspect.isfunction)
            if not name.startswith("_")
        }

        # Wrap them up on a fresh namespace object
        project_obj = type(project_name, (), {})()
        for func_name, func_obj in project_functions.items():
            wrapped = self._wrap_callable(f"{project_name}.{func_name}", func_obj)
            setattr(project_obj, func_name, wrapped)

        # Cache and return
        self._cache[project_name] = project_obj
        return project_obj
    
    def log(self, *args, **kwargs):
        if self._debug:
            self.debug(*args, **kwargs)
            return "debug"
        self.info(*args, **kwargs)
        return "info"
    

# This line allows using "from gway import gw" everywhere else
gw = Gateway()
