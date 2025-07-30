import functools
import inspect
import time
import threading
import sys

_local = threading.local()

def get_call_stack():
    """Get the current thread's call stack."""
    if not hasattr(_local, 'call_stack'):
        _local.call_stack = []
    return _local.call_stack

def get_current_frame():
    """Get the current frame for tracking."""
    if not hasattr(_local, 'current_frame'):
        _local.current_frame = None
    return _local.current_frame

def set_current_frame(frame):
    """Set the current frame for tracking."""
    _local.current_frame = frame

class LatencyFrame:
    """Represents a single function call in the call hierarchy."""
    def __init__(self, func_name):
        self.name = func_name
        self.start_time = time.time()
        self.end_time = None
        self.duration = None
        self.children = []
        self.parent = None

    def finish(self):
        """Mark the frame as finished and calculate duration."""
        if self.end_time is None:
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time

    def get_self_time(self):
        """Calculate time spent in this function excluding children."""
        if self.duration is None:
            return 0.0
        child_time = sum(child.duration or 0.0 for child in self.children)
        return max(self.duration - child_time, 0.0)

    def to_dict(self, threshold_ms=0):
        if self.duration is None:
            self.finish()

        # Skip if below threshold
        if self.duration * 1000 < threshold_ms:
            return None

        children_dicts = [
            child.to_dict(threshold_ms)
            for child in sorted(self.children, key=lambda x: x.start_time)
        ]
        children_dicts = [c for c in children_dicts if c is not None]

        return {
            "Name": self.name,
            "durationMs": round(self.duration * 1000, 2),
            "selfTimeMs": round(self.get_self_time() * 1000, 2),
            "children": children_dicts
        }

    def format(self, indent=0, threshold_ms=0):
        if self.duration is None:
            self.finish()

        if self.duration * 1000 < threshold_ms:
            return ''

        duration_ms = self.duration * 1000
        self_time_ms = self.get_self_time() * 1000

        result = ' ' * indent + f"{self.name}: {duration_ms:.2f}ms (self: {self_time_ms:.2f}ms)\n"
        sorted_children = sorted(self.children, key=lambda x: x.start_time)
        for child in sorted_children:
            child_str = child.format(indent + 2, threshold_ms)
            if child_str:
                result += child_str
        return result


class TracingProfiler:
    """Profiler that uses sys.setprofile to track all function calls."""
    _active = False

    @classmethod
    def start(cls):
        if cls._active:
            return
        get_call_stack().clear()
        set_current_frame(None)
        cls._active = True
        sys.setprofile(cls._profile_handler)

    @classmethod
    def stop(cls):
        if not cls._active:
            return

        call_stack = get_call_stack()
        for frame in call_stack:
            if frame.duration is None:
                frame.finish()

        current = get_current_frame()
        while current:
            if current.duration is None:
                current.finish()
            current = current.parent

        sys.setprofile(None)
        cls._active = False

    @classmethod
    def _should_track(cls, frame):
        if not frame:
            return False

        code = frame.f_code
        filename = code.co_filename

        if 'site-packages' in filename or filename.startswith(sys.base_prefix):
            return False

        module = inspect.getmodule(frame)
        if module:
            mod_name = module.__name__
            excluded_prefixes = (
                'logging', 'threading', 'time', 'contextlib', 'inspect',
                'functools', 'traceback', 'importlib', 'atexit', 'abc',
                'gunicorn', 'concurrent', 'os', 'select'
            )
            if mod_name.startswith('_') and mod_name != '__main__':
                return False
            elif mod_name.startswith(excluded_prefixes):
                return False

        return True
    
    @classmethod
    def _profile_handler(cls, frame, event, arg):
        if frame.f_globals.get('__name__', '').startswith(__name__):
            return

        if not cls._should_track(frame):
            return

        code = frame.f_code
        func_name = code.co_name

        if 'self' in frame.f_locals:
            instance = frame.f_locals['self']
            class_name = instance.__class__.__name__
            func_name = f"{class_name}.{func_name}"
        elif 'cls' in frame.f_locals:
            cls_obj = frame.f_locals['cls']
            if inspect.isclass(cls_obj):
                class_name = cls_obj.__name__
                func_name = f"{class_name}.{func_name}"

        call_stack = get_call_stack()

        if event == 'call':
            latency_frame = LatencyFrame(func_name)
            current = get_current_frame()
            if current:
                latency_frame.parent = current
                current.children.append(latency_frame)
            else:
                call_stack.append(latency_frame)
            set_current_frame(latency_frame)

        elif event == 'return':
            current = get_current_frame()
            if current and current.name == func_name:
                current.finish()
                set_current_frame(current.parent)

class LatencyWatch:
    """
    Simple latency watching decorator that starts tracing for the decorated function.
    """
    @classmethod
    def watch(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            TracingProfiler.start()
            try:
                return func(*args, **kwargs)
            finally:
                TracingProfiler.stop()
        return wrapper

    @classmethod
    def get_last_report(cls, as_dict=False, threshold_ms=0):
        call_stack = get_call_stack()
        if not call_stack:
            return "No calls recorded yet." if not as_dict else {}
        root = call_stack[0]  # Get the root frame
        return root.to_dict(threshold_ms) if as_dict else root.format(threshold_ms=threshold_ms)

    @classmethod
    def reset(cls):
        get_call_stack().clear()
        set_current_frame(None)