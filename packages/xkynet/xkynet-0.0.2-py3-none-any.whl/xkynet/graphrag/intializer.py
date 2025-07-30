
import subprocess

from .utils import delete_env_file

def initialize_graphrag(chatbot_dir, GRAPHRAG_PATH):
    try:
        result = subprocess.run([GRAPHRAG_PATH, "init", "--root", chatbot_dir], capture_output=True, text=True, check=True)
        print(result.stdout)
        delete_env_file(chatbot_dir)
    except subprocess.CalledProcessError as e:
        print(e)
        print(f"{chatbot_dir} already initialized")