import os
import json
import tempfile
import csv
import time
import threading
from primus_safe_pulsekit_pytorch_launcher.launcher import main  # 替换成你的主模块文件名

def create_benchmark_script(json_path, csv_path, script_path):
    with open(script_path, "w") as f:
        f.write(f"""\
import json
import csv
import time

# 模拟计算过程
time.sleep(1)

# 写 JSON 结果
with open("{json_path}", "w") as jf:
    json.dump({{"final_accuracy": 0.98}}, jf)

# 写 CSV 结果
with open("{csv_path}", "w", newline='') as cf:
    writer = csv.DictWriter(cf, fieldnames=["step", "accuracy"])
    writer.writeheader()
    writer.writerow({{"step": 1, "accuracy": 0.9}})
    writer.writerow({{"step": 2, "accuracy": 0.95}})
print("Benchmark finished.")
""")

def test_main_as_master():
    # 准备路径
    tmp_dir = tempfile.gettempdir()
    json_path = os.path.join(tmp_dir, "result.json")
    csv_path = os.path.join(tmp_dir, "result.csv")
    script_path = os.path.join(tmp_dir, "benchmark_script.py")

    create_benchmark_script(json_path, csv_path, script_path)

    # 设置 master 所需的环境变量
    os.environ["RANK"] = "0"
    os.environ["PULSEKIT_PYTORCH_LAUNCHER_SCRIPT"] = script_path
    os.environ["PULSEKIT_PYTORCH_LAUNCHER_RESULT_FILES"] = f"{json_path},{csv_path}"

    # 启动主函数，运行服务+benchmark
    def run_main():
        main()

    thread = threading.Thread(target=run_main)
    thread.start()

    # 等待 benchmark 运行结束
    print("[Test] Waiting for main to complete...")
    thread.join()
    print("[Test] Main completed.")

    # 打印结果文件内容作为验证
    with open(json_path) as jf:
        print("\n[Result JSON]:", json.load(jf))

    with open(csv_path) as cf:
        reader = csv.DictReader(cf)
        print("\n[Result CSV]:", list(reader))

if __name__ == "__main__":
    test_main_as_master()
