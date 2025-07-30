# https://nilaoda.github.io/N_m3u8DL-CLI/Advanced.html

from pathlib import Path
import subprocess
import os
import shutil

CURRENT_DIR = Path(__file__).parent
PACKAGE_DIR = CURRENT_DIR.parent

TOOL_PATH = PACKAGE_DIR / "bin/N_m3u8DL-CLI_v3.0.2.exe"
LOG_DIR = PACKAGE_DIR / "bin/Logs"

def b_download_m3u8(url, output_path, maxThreads=32, minThreads=16, retryCount=15, timeOut=10, enableDelAfterDone=True):
    output_dir = Path(output_path).parent
    os.makedirs(output_dir, exist_ok=True)

    output_filename = Path(output_path).name
    output_name, output_ext = os.path.splitext(output_filename)


    command = [
        str(TOOL_PATH),
        url,
        '--workDir', str(output_dir),
        '--saveName', str(output_name),
        '--maxThreads', str(maxThreads),
        '--minThreads', str(minThreads),
        '--retryCount', str(retryCount),
        '--timeOut', str(timeOut),
    ]
    if enableDelAfterDone:
        command.append('--enableDelAfterDone')


    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )
    for line in proc.stdout:
        line = line.strip() # 去掉\n
        if line != '': # 去掉空行
            print(line)

    proc.stdout.close() # 关闭管道
    proc.wait() # 等待进程结束

    # 删除Log文件夹
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR)



if __name__ == '__main__':
    b_download_m3u8('https://www.example.com/playlist.m3u8', 'output/playlist.mp4')
    b_download_m3u8(url, 'output/playlist.mp4')