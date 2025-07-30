import os
import json
import tempfile
import csv
from primus_safe_pulsekit import PluginContext, ProgressReporter, HardwareInfo
from primus_safe_pulsekit_pytorch_launcher.launcher import Launcher, shutdown_event  # 替换为你真实模块路径

# 创建临时文件
def create_test_files():
    tmp_dir = tempfile.gettempdir()

    # JSON 文件
    json_path = os.path.join(tmp_dir, "test_result.json")
    with open(json_path, "w") as f:
        json.dump({"accuracy": 0.95, "loss": 0.05}, f)

    # CSV 文件
    csv_path = os.path.join(tmp_dir, "test_result.csv")
    with open(csv_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["epoch", "accuracy"])
        writer.writeheader()
        writer.writerow({"epoch": 1, "accuracy": 0.9})
        writer.writerow({"epoch": 2, "accuracy": 0.93})

    return json_path, csv_path

# 模拟进度输出
class DummyProgressReporter(ProgressReporter):
    def log(self, msg: str):
        print(f"[Progress] {msg}")

def test_launcher():
    json_path, csv_path = create_test_files()
    os.environ["PULSEKIT_PYTORCH_LAUNCHER_RESULT_FILES"] = f"{json_path},{csv_path}"

    # 模拟脚本运行完毕
    shutdown_event.set()

    launcher = Launcher()
    context = PluginContext(hardware_info=HardwareInfo())  # 可根据你的定义初始化
    progress = DummyProgressReporter()

    result = launcher.run(context, progress)
    print("\n=== Parsed Results ===")
    print(result)

if __name__ == "__main__":
    test_launcher()
