import os, shutil, subprocess
#import pprint #used for debugging

from functools import singledispatch
from pathlib import Path

from graphrag.config.load_config import load_config

import pandas as pd

def create_input_folder(directory: str):
    os.makedirs(f'{directory}/input', exist_ok=True)
    print(f'Folder {directory} created')

def copy_file(file_path, output_dir):
    shutil.copy(file_path, output_dir)
    print(f'Copied {file_path} to {output_dir}!')

def copy_files(file_paths, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for file_path in file_paths:
        copy_file(file_path, output_dir)

def delete_env_file(folder):
    env_file_path = os.path.join(folder, '.env')
    if os.path.exists(env_file_path):
        os.remove(env_file_path)
        print(f'Deleted {env_file_path}')
    else:
        print(f'No .env file found in {folder}')


def load_graphrag_config(chatbot_name='ragtest'):
    chatbot_path = Path(chatbot_name)
    if not chatbot_path.exists():
        raise FileNotFoundError(f"The folder {chatbot_name} does not exist in the current directory.")
    conf = load_config(root_dir=chatbot_path)
    return conf

def update_conf(conf, llm_model_version):
    conf['models']['default_chat_model']['model'] = llm_model_version
    conf['models']['default_chat_model']['encoding_model'] = 'cl100k_base'
    conf['models']['default_embedding_model']['api_key'] = '${OPENAI_API_KEY}'
    conf['vector_store']['default_vector_store']['db_uri'] = 'output/lancedb'

    if "deepseek" in llm_model_version:
        conf['models']['default_chat_model'].update({
            'api_key': '${DEEPSEEK_API_KEY}',
            'api_base': 'https://api.deepseek.com'
        })
    else:
        conf['models']['default_chat_model'].update({
            'api_key': '${OPENAI_API_KEY}',
        })
        conf['models']['default_chat_model'].pop('api_base', None)
    
    return conf


@singledispatch
def load_output(directory, **kwargs):
    raise TypeError(f"Unsupported type: {type(directory)}. Expected Path-like Object or dictionary of Path-like Object.")

@load_output.register
def load_output_str(directory:os.PathLike)->dict[pd.DataFrame]:
    print(f"Loading output from {directory}")
    data = {
        'conf': load_config(root_dir=Path(directory)),
        'entities': pd.read_parquet(f"{directory}/output/entities.parquet"),
        'communities': pd.read_parquet(f"{directory}/output/communities.parquet"),
        'community_reports': pd.read_parquet(f"{directory}/output/community_reports.parquet"),
        'text_units': pd.read_parquet(f"{directory}/output/text_units.parquet"),
        'relationships': pd.read_parquet(f"{directory}/output/relationships.parquet"),
        'documents': pd.read_parquet(f"{directory}/output/documents.parquet")
    }
    return data

@load_output.register
def load_output_dict(directory:dict)->dict[pd.DataFrame]:
    print(f"Loading output from dictionary")
    data = {}
    for key, value in directory.items():
        if key == 'conf':
            data['conf'] = load_config(root_dir=Path(value))
        else:
            data[key] = pd.read_parquet(value)
        
    return data


