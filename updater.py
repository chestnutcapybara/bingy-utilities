import requests
import zipfile
import os
import shutil
import tempfile
import sys
import subprocess
import time
from logger import logger

GIST_URL = "https://gist.githubusercontent.com/chestnutcapybara/193b05cf99947c5f62e199b74a490a7e/raw/d5e43c6a259377acedcbbc67375de767a1d1b94c/version.json"

APP_DIR = sys.argv[1]
MAIN_EXE = os.path.join(APP_DIR, "main.dist", "main.exe")

print("APP_DIR =", APP_DIR)
print("MAIN_EXE =", MAIN_EXE)
print("MAIN_EXE exists =", os.path.exists(MAIN_EXE))
print("APP_DIR exists =", os.path.exists(APP_DIR))


def get_platform_key():
    return "windows-x64"


def download_file(url, output_path):
    r = requests.get(url, stream=True, timeout=10)
    r.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def main():
    logger.info("Update started")

    data = requests.get(GIST_URL, timeout=5).json()
    info = data["capyutilities"]

    version = info["version"]
    download_url = info["downloads"][get_platform_key()]

    logger.info(f"Updating to {version}")

    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, "update.zip")

    logger.info("Downloading update...")
    download_file(download_url, zip_path)

    extract_dir = os.path.join(tmp_dir, "extracted")

    logger.info("Extracting...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    time.sleep(2)

    logger.info("Replacing files...")

    for item in os.listdir(extract_dir):
        src = os.path.join(extract_dir, item)
        dst = os.path.join(APP_DIR, item)

        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    shutil.rmtree(tmp_dir)

    print("Restarting CapyUtilities...")
    subprocess.Popen([MAIN_EXE])

    print("Update complete!")


if __name__ == "__main__":
    main()