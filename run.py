"""一键运行入口：执行用例 → 生成 Allure 中文报告 → 自动打开。"""
import os
import subprocess
import sys
from common.config import config

ROOT = config.base_dir


def run_tests():
    """执行 pytest 用例，生成 allure-results。"""
    cmd = [sys.executable, "-m", "pytest", "test_cases"]
    print(">>> 执行测试：", " ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


def _find_allure():
    """定位 allure 可执行文件（Windows 下优先找 allure.bat）。"""
    # 1. 常见安装目录
    candidates = [
        os.path.join(os.path.expanduser("~"), "allure", "bin", "allure.bat"),
        os.path.join(os.path.expanduser("~"), "allure", "bin", "allure"),
    ]
    # 2. 从 PATH 里找
    for p in os.environ.get("Path", "").split(os.pathsep):
        candidates.append(os.path.join(p, "allure.bat"))
        candidates.append(os.path.join(p, "allure"))
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def generate_report():
    """生成并打开 Allure 中文报告。"""
    results = config.allure.get("results_dir", "allure-results")
    report = config.allure.get("report_dir", "reports/allure-report")

    allure_exe = _find_allure()
    if not allure_exe:
        print("⚠ 未检测到 Allure CLI，请先安装并加入 PATH：")
        print("  下载地址：https://github.com/allure-framework/allure2/releases")
        print("  已生成 allure-results/，可手动执行 allure generate 查看报告。")
        return

    env = os.environ.copy()
    env["ALLURE_LANGUAGE"] = "zh"  # 中文报告

    gen = [allure_exe, "generate", results, "-o", report, "--clean"]
    print(">>> 生成报告：", " ".join(gen))
    subprocess.run(gen, cwd=ROOT, env=env, check=True)

    print(f"✅ 报告已生成：{os.path.join(ROOT, report)}")
    print(">>> 打开报告预览（Ctrl+C 退出）...")
    try:
        subprocess.run([allure_exe, "open", report], cwd=ROOT, env=env)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    code = run_tests()
    print(f"\n测试执行完毕，退出码：{code}")
    generate_report()
