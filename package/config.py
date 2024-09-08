import logging
import os

PORT       = 5010
HOST       = "192.168.5.27"
END_POINT  = "pre_commit"
PASS, FAIL = 0, 1
ROOT       = os.path.abspath(__file__ + '/../../')
INTERNAL   = os.path.abspath(ROOT + "/_internal")
VERSION_F  = os.path.join(INTERNAL,"version.txt")
VERSION    = open(VERSION_F).read().strip() if os.path.exists(VERSION_F) else "0.0.0"
MAX_PROMPT_LEN = 6000
log_directory = os.path.expanduser("~/ouai/log")
os.makedirs(log_directory, exist_ok=True)
log_file_path = os.path.join(log_directory, "check_commit_msg.log")

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file_path),logging.StreamHandler()])
logger = logging.getLogger("check_commit_msg")

