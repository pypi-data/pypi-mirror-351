# ⏱️ LatencyWatch

[![PyPI version](https://badge.fury.io/py/latencywatch.svg)](https://pypi.org/project/latencywatch/0.1.0)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**LatencyWatch** is a lightweight Python profiler for tracing nested function call latencies using `sys.setprofile`. It tracks execution time for every function call — including self-time (excluding children) — and presents a hierarchical report of where time was spent.


---

## 🚀 Installation

Install the package directly from PyPI:

```sh
pip install latencywatch
```
---


🔍 Features

✅ No instrumentation needed — just a decorator!

📊 Provides nested, readable latency reports

🧵 Thread-local storage for thread-safe profiling

🧠 Automatically excludes common library/internal calls

⚡ Useful for tracing performance bottlenecks in Python applications

---
🧪 Basic Usage

```python
from latencywatch import LatencyWatch

@LatencyWatch.watch
def sample_workload():
    def inner():
        time.sleep(0.05)
    inner()
    time.sleep(0.1)

sample_workload()

print(LatencyWatch.get_last_report(threshold_ms=1))

```

Output (formatted):


```python

sample_workload: 151.12ms (self: 100.94ms)
  inner: 50.18ms (self: 50.18ms)

```
---

🧰 API Reference
@LatencyWatch.watch
Decorator to trace an entire function call.

LatencyWatch.get_last_report(threshold_ms=0, as_dict=False)
Returns the last recorded profiling report.

threshold_ms: Minimum duration (in ms) to include in report

as_dict: If True, returns structured dict instead of string

LatencyWatch.reset()
Clears previously recorded profiling data.

---

📦 Example Use Cases
Performance profiling for backend APIs

Detecting latency bottlenecks in nested function calls

Analyzing self-time vs child-time in recursive or complex call stacks


---
📁 Project Structure

```
latencywatch/
├── latencywatch/
│   ├── __init__.py
│   └── profiler.py
├── tests/
├── README.md
├── setup.py
├── pyproject.toml
├── LICENSE


```
---

📜 License

### This project is licensed under the MIT License.

---
