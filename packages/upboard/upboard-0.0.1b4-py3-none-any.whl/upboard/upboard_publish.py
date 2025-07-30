#! python
# -*- coding: utf-8 -*-

import os
import logging
import argparse
import requests
from   pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%m%d %H:%M:%S'
)
logger = logging.getLogger('upboard.publish')

def upload_file(url, file_path, password=None):
    """
    上传单个文件到服务器
    :param url: 目标URL
    :param file_path: 文件路径
    :param password: 认证密码
    :return: 是否成功
    """
    try:
        filename = os.path.basename(file_path)
        if not url.endswith(filename):
            url = url.rstrip('/') + '/' + filename

        headers = {"Authorization": password} if password else None

        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            response = requests.put(url, headers=headers, files=files)
            
            if response.status_code == 201:
                logger.debug(f"Response: {response.text.strip()}")
                return True
            else:
                logger.error(f"Failed for {filename} (Status: {response.status_code})")
                logger.error(f"Error: {response.text.strip()}")
                return False

    except Exception as e:
        logger.error(f"Error {filename}: {str(e)}")
        return False

def upload_directory(base_url, dir_path, password=None):
    """
    上传目录中的所有文件（非递归）
    :param base_url: 基础URL
    :param dir_path: 目录路径
    :param password: 认证密码
    :return: 成功上传的文件数
    """
    success_count = 0
    try:
        dir_path = Path(dir_path)
        files = [f for f in dir_path.iterdir() if f.is_file()]
        if not files:
            logger.warning(f"Empty directory: {dir_path}")
            return 0

        for file in files:
            logger.info(f"Uploading: {file}")
            if upload_file(base_url, str(file), password):
                success_count += 1

        return success_count

    except Exception as e:
        logger.error(f"Error processing directory: {str(e)}")
        return success_count

def main():
    parser = argparse.ArgumentParser(
        description="""UpBoard Client - Upload files to upboard server.

Example:
  upboard_publish http://host:port/api/v1/releases/your-project/win32/x64/ ./file_or_directory -p admin
""",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("url", help="Upload base URL (e.g., http://host:port/api/v1/releases/your-project/win32/x64/)")
    parser.add_argument("path", help="Path to the file or directory to upload")
    parser.add_argument("-p", "--password", default="admin", help="Authorization password")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    path = Path(args.path)
    if path.is_file():
        logger.info(f"Uploading: {path}")
        success = upload_file(args.url, str(path), args.password)
        if not success:
            logger.error("Upload failed.")
            os._exit(1)
        logger.info(f"Done.")

    elif path.is_dir():
        success_count = upload_directory(args.url, str(path), args.password)
        if success_count == 0:
            logger.error("Upload failed.")
            os._exit(1)

        else:
            logger.info(f"Uploaded {success_count} files.")

    else:
        logger.error(f"Not a file or directory: {path}")
        os._exit(1)

if __name__ == "__main__":
    main()
