from typing import List, Union
import subprocess

def run_command_with_realtime_output(
    command: Union[str, List[str]], 
    working_directory: str = None,
    encoding: str = None
):
    """
    执行命令并实时输出结果
    :param command: 要执行的命令，可以是字符串或列表
    :param working_directory: 命令执行的工作目录，None表示当前目录
    :param encoding: 输出编码，默认None不设置
    """
    from threading import Thread
    try:
        shell = True if isinstance(command, str) else False
        # 启动子进程，实时输出 stdout 和 stderr
        process = subprocess.Popen(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding=encoding,  # 明确指定编码,这种方式可能会导致部分命令输出中文乱码，可以设置环境变量PYTHONIOENCODING控制
            errors='replace',  # 替换无法解码的字符
            cwd=working_directory,
            bufsize=1,  # 行缓冲
            universal_newlines=True
        )

        # 定义一个函数来实时读取并打印输出
        def print_output(stream, prefix=""):
            for line in stream:
                print(prefix + line.strip())

        # 启动两个线程分别读取 stdout 和 stderr
        stdout_thread = Thread(target=print_output, args=(process.stdout,))
        stderr_thread = Thread(target=print_output, args=(process.stderr,))

        stdout_thread.start()
        stderr_thread.start()

        # 等待进程结束
        process.wait()

        # 确保线程完成
        stdout_thread.join()
        stderr_thread.join()

        # 检查返回码
        if process.returncode == 0:
            # print("命令执行成功")
            pass
        else:
            raise RuntimeError(f"命令执行失败，返回码：{process.returncode}")
    except Exception as e:
        raise e


def run_command_and_capture_output(
    command: Union[str, List[str]],
    working_directory: str = None,
    encoding: str = None,
    timeout: int = None
):
    """
    执行命令并捕获输出
    :param command: 要执行的命令，可以是字符串或列表
    :param working_directory: 命令执行的工作目录，None表示当前目录
    :param encoding: 输出编码，默认None不设置
    :param timeout: 超时时间(秒)，None表示不限制
    """
    try:
        shell = True if isinstance(command, str) else False
        # 执行命令并捕获输出
        result = subprocess.run(
            command,
            shell=shell,
            cwd=working_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True,
            encoding=encoding,  # 明确指定编码,这种方式可能会导致部分命令输出中文乱码，可以设置环境变量PYTHONIOENCODING控制
            errors='replace'
        )

        # 打印所有输出（执行完成后）
        if result.stdout:
            print("标准输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)

        # 检查返回码
        if result.returncode == 0:
            # print("命令执行成功")
            pass
        else:
            raise RuntimeError(f"命令执行失败，返回码：{result.returncode}")
    except Exception as e:
        raise e


def run_command_silently(
    command: Union[str, List[str]],
    working_directory: str = None,
    encoding: str = 'utf-8',
    timeout: int = None
):
    """
    静默执行命令，不关心输出
    :param command: 要执行的命令，可以是字符串或列表
    :param working_directory: 命令执行的工作目录，None表示当前目录
    :param encoding: 输出编码，默认utf-8
    :param timeout: 超时时间(秒)，None表示不限制
    """
    shell = True if isinstance(command, str) else False
    try:
        # 执行命令
        result = subprocess.run(
            command,
            shell=shell,
            cwd=working_directory,
            stdout=subprocess.DEVNULL,  # 忽略标准输出
            stderr=subprocess.DEVNULL,  # 忽略标准错误
            timeout=timeout,
            encoding=encoding,  # 明确指定编码,这种方式可能会导致部分命令输出中文乱码，可以设置环境变量PYTHONIOENCODING控制
            errors='replace',  # 替换无法解码的字符
            check=True  # 如果命令失败，会抛出异常
        )
        # print("命令执行成功")
    except subprocess.CalledProcessError as e:
        raise e
    except Exception as e:
        raise e