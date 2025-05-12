import platform
import winreg
import psutil


# 获取操作系统信息
def get_os_info():
    return platform.system(), platform.release()


# 获取windows系统信息
def get_windows_version_info():
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")

        # 获取 DisplayVersion
        try:
            display_version, _ = winreg.QueryValueEx(registry_key, "DisplayVersion")
        except FileNotFoundError:
            display_version = "N/A"

        # 获取 ReleaseId
        try:
            release_id, _ = winreg.QueryValueEx(registry_key, "ReleaseId")
        except FileNotFoundError:
            release_id = "N/A"

        # 获取 CurrentBuild
        current_build, _ = winreg.QueryValueEx(registry_key, "CurrentBuild")

        winreg.CloseKey(registry_key)

        return {
            "显示版本": display_version,
            "ID": release_id,
            "构建版本号": current_build
        }
    except Exception as e:
        return f"Error retrieving Windows version info: {e}"


# 获取系统资源状态
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    memory_info = psutil.virtual_memory()
    return memory_info.percent


# 获取CPU核心(包括超线程)
def get_cpu_core_count():
    cpu_cores = psutil.cpu_count(logical=False)  # 获取核心(物理)
    cpu_cores_more = psutil.cpu_count(logical=True)  # 获取全部核心(物理+超线程)
    return cpu_cores, cpu_cores_more


# 获取虚拟内存使用率
def get_virtual_memory_usage():
    virtual_mem = psutil.virtual_memory()
    return virtual_mem.percent


# 获取系统进程信息
def get_running_process_count():
    # 获取当前正在运行的进程的PID
    process_ids = psutil.pids()
    return len(process_ids)


# 获取系统总内存
def get_mem_info():
    mem_info = psutil.virtual_memory().total  # 获取总内存
    return mem_info / (1024 ** 3)  # 转换为 GB
