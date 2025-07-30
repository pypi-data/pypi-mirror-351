import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Dict, Any

from primus_safe_pulsekit import RemotePlugin, PluginContext, ProgressReporter

down_event = threading.Event()
exit_event = threading.Event()

def is_master():
    return int(os.environ.get("RANK", "-1")) == 0

import csv

class Launcher(RemotePlugin):
    def __init__(self, host: str = "0.0.0.0", port: int = 8989):
        super().__init__(host, port)
        self.register_shutdown()

    def register_shutdown(self):
        @self.app.post("/exit")
        def shutdown():
            exit_event.set()
    def install_dependencies(self, context: PluginContext, progress: ProgressReporter):
        pass

    def run(self, context: PluginContext, progress: ProgressReporter) -> str:
        progress.log("[Launcher] Waiting for benchmark script to complete...")
        down_event.wait()
        progress.log("[Launcher] Benchmark complete. Reading results...")

        result_file_json = os.environ.get("PULSEKIT_PYTORCH_LAUNCHER_RESULT_FILES")
        if not result_file_json:
            raise ValueError("No result file paths provided.")

        try:
            path_name_map = json.loads(result_file_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON for PULSEKIT_PYTORCH_LAUNCHER_RESULT_FILES: {e}")

        results = {}
        for path, name in path_name_map.items():
            path = path.strip()
            if not path or not os.path.exists(path):
                results[name] = {"error": f"Path does not exist: {path}"}
                continue

            ext = os.path.splitext(path)[1].lower()
            try:
                if ext == ".json":
                    with open(path, "r") as f:
                        results[name] = json.load(f)
                elif ext == ".csv":
                    with open(path, "r", newline='') as f:
                        reader = csv.DictReader(f)
                        results[name] = list(reader)
                else:
                    results[name] = {"error": f"Unsupported file extension: {ext}"}
            except Exception as e:
                results[name] = {"error": str(e)}

        return json.dumps(results)

    def get_json_result(self, output: str) -> Dict[str, Any]:
        return json.loads(output)

def run_server(launcher: Launcher):
    launcher.serve()

def main():
    benchmark_script = os.environ.get("PULSEKIT_PYTORCH_LAUNCHER_SCRIPT")
    result_file_paths = os.environ.get("PULSEKIT_PYTORCH_LAUNCHER_RESULT_FILES")
    if not benchmark_script or not result_file_paths:
        print("Missing environment variables!")
        sys.exit(1)

    launcher = Launcher()

    if is_master():
        # 启动 run_server
        threading.Thread(target=run_server, args=(launcher,), daemon=True).start()

        # 启动 benchmark 脚本线程
        def run_benchmark():
            print("[Master] Running benchmark script...")
            try:
                p = Path(benchmark_script)
                print(p.absolute())
                subprocess.run(["python3", benchmark_script], check=True, env=os.environ)
            except subprocess.CalledProcessError as e:
                print(f"[Master] Benchmark script failed: {e}")
            finally:
                # 通知挂起的 run 方法继续执行
                down_event.set()

        threading.Thread(target=run_benchmark, daemon=True).start()
        print("[Master] Waiting for /shutdown (script completion)...")
        down_event.wait()
        print("[Master]Execution done")
        exit_event.wait()

    else:
        # 非 master 节点只运行 benchmark 脚本
        subprocess.run(["python3", benchmark_script], check=True, env=os.environ)

