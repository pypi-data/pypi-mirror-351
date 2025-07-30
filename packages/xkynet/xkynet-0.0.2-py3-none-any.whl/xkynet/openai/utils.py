# Copyright (c) 2024, Xurpas AI Lab and contributors
# For license information, please see license.txt

import os
import frappe
from pathlib import Path
from typing import Iterable

from openai import OpenAI, NotFoundError, BadRequestError
from openai.types.beta.assistant import Assistant
from xail_chatbot.xail_chatbot.utils import StatusBar

import logging
logging.basicConfig(
    level = logging.INFO,
    format= "[xail-chatbot] - %(levelname)s: %(message)s"
)
logger = logging.getLogger('chat_context.utils')
logger.setLevel(logging.DEBUG)

def create_assistant(name: str, 
                     description: str = None, 
                     system_context:str=None, 
                     model:str='gpt-4o-mini',
                     temperature:float=0.0,
                     score_threshold:float=0.0,
                     vector_id:str=None,
                     client:OpenAI=None,
                     progress_bar:StatusBar=None,
                    ) -> str:
    """ Creates and adds assistant to OpenAI Client.
    Input
        name: Required | Name of the assistant.
        descripton: Optional | Description of the assistant.
        system_context: Optional | The instructions for the assistant.
        model: Optional | The model to be used. Defaults to gpt-4o-mini.
        temperature: Optional | Sampling temperature to use for the model.
        client: Optional | OpenAI client.
    Returns
        assistant_id: The Assistant ID.
    """
    logger.debug("create assistant called")
    progress_bar.update_total(3)
    progress_bar.log(f"Creating assistant named '{name}'")

    if not description:
        description = "You are an Assistant"

    progress_bar.log(f"Assistant is described as '{description}'")

    try:
        temperature = float(temperature)

    except Exception as e:
        warning = f"[xail-chatbot] Exception:    Assistant Creation Error{e}"
        print(warning)
        frappe.throw(warning)

    client = OpenAI() if client is None else client

    assistant = client.beta.assistants.create(
        model=model,
        name=name,
        description=description,
        instructions=system_context,
        tools= [{"type": "file_search",
                 "file_search": {
                     "ranking_options": {"score_threshold": score_threshold}
                 }}],
        temperature=temperature
    )
    progress_bar.log(f"Assistant created with id {assistant.id}")

    if vector_id is not None and vector_id != "":
        add_vector_to_assistant(assistant_id=assistant.id, vector_id=vector_id, client=client, progress_bar=progress_bar)

    elif vector_id is None or vector_id == "":
        progress_bar.log_message("No Vector Index provided. Skipping Vector Index addition to Assistant")
    
    logger.debug(f"returning assistant_id as {assistant.id} after creation")
    return assistant.id, progress_bar

            
def modify_assistant(assistant_id: str,
                    name: str = None, 
                    description: str = None, 
                    system_context: str = None, 
                    model:str = 'gpt-4o-mini',
                    temperature:float = 0.0,
                    score_threshold:float=0.0,
                    vector_id: str = None,
                    client:OpenAI = None,
                    progress_bar: StatusBar = None
                    ) -> str:
    
    """ Creates and adds assistant to OpenAI Client.
    Input
        assistant_id: Required| Assistant ID.
        name: Optional | Name of the assistant.
        descripton: Optional | Description of the assistant.
        system_context: Optional | The instructions for the assistant.
        model: Optional | The model to be used. Defaults to gpt-4o-mini.
        temperature: Optional | Sampling temperature to use for the model.
        client: Optional | OpenAI client.
    Returns
        assistant_id: The Assistant ID.
    """
    client = client if client is not None else OpenAI()
    logger.debug("modify assistant called")
    if assistant_id is None:
        progress_bar.log_message(f"Assistant does not exist! Creating new assistant")
        assistant_id, progress_bar= create_assistant(name=name, description=description, system_context=system_context,
                         model=model, temperature=temperature, progress_bar=progress_bar)
        logger.debug(f"Returning assistant_id as {assistant_id} after it was created since it was None")
        return assistant_id, progress_bar
    else:
        logger.debug(f"client.beta.assistants.retrieve(assistant_id): {client.beta.assistants.retrieve(assistant_id)}")
        try:
            # Testing if assistant has not been deleted via other means
            _ = client.beta.assistants.retrieve(assistant_id)
        except:
            # if Assistant no longer exists create a new one
            progress_bar.log_message(f"Assistant has been deleted! Creating new assistant")
            assistant_id, progress_bar = create_assistant(name=name, description=description, system_context=system_context,
                             model=model, temperature=temperature, progress_bar=progress_bar)
            logger.debug(f"Returning assistant_id as {assistant_id} after it was created since it does not exist")
            return assistant_id, progress_bar

        logger.debug(f"Assistant was not returned. continuing to modify assistant")

        progress_bar.update_total(4)
        progress_bar.log(f"Modifying assistant '{assistant_id}'")

        client = OpenAI() if client is None else client
        name = "Assistant" if name is None else name
        progress_bar.log_step()

        if not description:
            description = "You are an Assistant"

        progress_bar.log(f"Assistant described as '{description}'")
        
        assistant = client.beta.assistants.update(
            assistant_id,
            name=name,
            description=description,
            model=model,
            tools= [{"type": "file_search",
                    "file_search": {
                        "ranking_options": {"score_threshold": score_threshold}
                    }}],
            temperature=temperature,
            instructions=system_context,
            )
        progress_bar.log("Assistant modified!")

        if vector_id is not None and vector_id != "":
            add_vector_to_assistant(assistant_id=assistant_id, vector_id=vector_id, client=client, progress_bar=progress_bar)

        return assistant_id, progress_bar

def check_assistant_tool_resources(*, 
                    assistant_id: str,
                    vector_id: str,
                    client: OpenAI|None = None, 
                    progress_bar: StatusBar = None):
    client = client or OpenAI()
    progress_bar.update_total()
    progress_bar.log(f"Checking Assistant '{assistant_id}' if {vector_id} was added to tool resources")
    
    assistant = client.beta.assistants.retrieve(assistant_id)
    if len(assistant.tool_resources.file_search.vector_store_ids) == 0 or assistant.tool_resources.file_search.vector_store_ids[0] != vector_id:
        progress_bar = add_vector_to_assistant(assistant_id=assistant_id, vector_id=vector_id, client=client, progress_bar=progress_bar)
    else:
        progress_bar.log_message("Vector already added to Assistant")

    return progress_bar

def add_vector_to_assistant(*, 
                            assistant_id: str,
                            vector_id: str,
                            client: OpenAI|None = None, 
                            progress_bar: StatusBar = None):
    """ Adds Vector Index to Assistant."""
    client = client or OpenAI()

    progress_bar.update_total()
    progress_bar.log(f"Adding Vector Index {vector_id} to Assistant {assistant_id}")

    try:
        _ = client.beta.assistants.update(
                assistant_id = assistant_id,
                tools = [{"type": "file_search"}],
                tool_resources={'file_search': {'vector_store_ids': [vector_id]}}
            )
        
    except BadRequestError as e:
        if e.code == 'expired':
            progress_bar.log_message(f"Error: Vector code {vector_id} has expired. Creating new vector index...")
            frappe.msgprint(f"[xail-chatbot] Error:    Vector code {vector_id} has expired. Creating new vector index...")
        else:
            progress_bar.log_message(f"Error: {e}")
            frappe.msgprint(f"[xail-chatbot] Error:    {e}")
    except Exception as e:
        progress_bar.log_message(f"Unexpected Error: {e.body['message']}")
        frappe.msgprint(f"[xail-chatbot] Unexpected Error:    {e.body['message']}")

    finally:
        return progress_bar

def generate_index(*, 
                   index_file_path: str,
                   vector_name: str = None,
                   client: OpenAI|None = None, 
                   expiry:int = 7,
                   max_chunk_size_token: int = 800,
                   chunk_overlap_token: int = 400,
                   progress_bar: StatusBar = None
                   ) -> str:
    """ Creates Vector Index Storage for File Search
    If given no vector_id, removes all indices found in the OpenAI Cloud Client.
    Input
        vector_name: Optional, str | Name for the vector storage, if not given, use given filename as name
        client: Optional, OpenAI | use this if there is already a running OpenAI Client
    Return
        vector id: The ID of the processed vector storage index file. Used by the AgentAssistant Bot.
    """
    progress_bar.update_total(11)
    progress_bar.log("Generating Indices for Open AI")
    def load_files_from_file(doc_path: str)->list:
            """Processes the text file into a list of paths to be used."""
            progress_bar.log("Loading list of files to use")
            paths = []
            with open(doc_path, 'r') as file:
                first_line = file.readline()
                if not first_line:  # Check if File is Empty
                    frappe.msgprint("The file is empty. It should contain list of paths")
                    progress_bar.log_message("The file is empty. It should contain list of paths")
                
                else:
                    progress_bar.log("Loading Paths...")
                    paths.append(first_line.strip()) # Add the first line to the list if not empty
                    progress_bar.log_message(f"Document to be Indexed: {first_line}")
                    # Iterate through the rest of the lines
                    for line in file:
                        progress_bar.log_message(f"Document to be Indexed: {line}")
                        paths.append(line.strip())  # Process each line
                
                return paths
            
    def get_txt_file(directory_path):
        """Gets the .txt file from given directory path"""
        progress_bar.log("Getting list of files to use")
        try:
            progress_bar.log(f"Loading text file at directory {directory_path}")

            # List all files in the directory
            files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
            # Ensure there is only one .txt file
            if len(files) == 1:
                return os.path.join(directory_path, files[0])
            elif len(files) == 0:
                raise Exception("[xail-chatbot] Error:    No .txt files found in the directory.")
            else:
                return Exception("[xail-chatbot] Error:   More than one .txt file found in the directory.")
            
        except FileNotFoundError as e:
            return FileNotFoundError("[xail-chatbot] Error:    The specified directory does not exist.")
    
    text_file_path = frappe.get_site_path('private', 'files', index_file_path)
    
    progress_bar.log(f"Loading file from {text_file_path}")

    index_file = get_txt_file(text_file_path)
    index_paths = load_files_from_file(index_file)   

    if len(index_paths) == 0:
        progress_bar.log("No files to index. Exiting...")

        return None, progress_bar
    
    def check_uploaded_files(files:list, client):
        """Checks if given file exists in client.
        If existing, removes from index path."""
        progress_bar.log("Checking files in client...")
        client_file_list = client.files.list()
        client_files = {client_file.filename:client_file.id for client_file in client_file_list}
        
        existing_ids = []
        for file in files:
            try:
                updated_file = file.split('/')[-1]
            except:
                updated_file = file

            progress_bar.log_message("Looking at already uploaded files...")
            if updated_file in client_files.keys():
                progress_bar.log_message(f"Removing {file} from uploading since it exists already in client.")
                files.remove(file)
                existing_ids.append(client_files[updated_file])
                
        return files, existing_ids
    
    # Uses given client or if no given creates own
    client = client or OpenAI()

    index_paths, existing_file_ids = check_uploaded_files(index_paths, client)

    progress_bar.log("Creating Vector Stores...")
    vector_store = client.vector_stores.create(
        name=vector_name,
        expires_after={
            "anchor": "last_active_at",
            "days": expiry
        },
        chunking_strategy={
                "type":"static",
                "static": {
                    "max_chunk_size_tokens": int(max_chunk_size_token),
                    "chunk_overlap_tokens": int(chunk_overlap_token)
                }
        }

    )

    progress_bar.log(f"Vector store created with name: {vector_name} and ID: {vector_store.id}")
    if not isinstance(index_paths, list):
        index_paths = [index_paths]
    else:
        index_paths = index_paths

    progress_bar.log(f"Creating file streams to add to vector store.")
    file_streams=[]
    
    if len(index_paths) > 0:
        for path in index_paths:
            file_path = os.path.join(frappe.get_site_path(),path.lstrip("/"))
            file_streams.append(open(file_path,"rb"))
            progress_bar.log_message(f"File stream for {path} created")

        progress_bar.log("Adding file streams to vector store")  
        _file_batch_ = client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=file_streams
        )
    
    if len(existing_file_ids) > 0:
        progress_bar.update_total()
        progress_bar.log("Adding existing files in client to vector_store")
        vector_store_file = client.vector_stores.file_batches.create(
            vector_store_id = vector_store.id,
            file_ids = existing_file_ids
        )

    return vector_store.id, progress_bar


def clear_old_index(vector_id:str|None=None, *, client: OpenAI|None = None, progress_bar: StatusBar=None,**kwargs):
    """ Clears the Vector Store Index found in OpenAI Cloud.
    If given no vector_id, removes all indices found in the OpenAI Cloud Client.
    Input
        vector_id: Optional, String | Used if you want to just clear a specific index
        client: Optional, OpenAI | use this if there is already a running OpenAI Client
    Return
        No Return
    """
    client = client or OpenAI()
    progress_bar.update_total()
    progress_bar.log(f"Deleting vector store: {vector_id}")
    try:
        deleted = client.vector_stores.delete(vector_store_id=vector_id)
        progress_bar.log(f"{vector_id} deleted!")

    except Exception as e:
        message = f"Unable to delete {vector_id}!"
        frappe.msgprint(f"[xail-chatbot] Log:    {message}")
        progress_bar.log_message(message)

    finally:
        return progress_bar


def update_vector_store(vector_id: str,*, name:str=None, expires_after:int=None,client: OpenAI|None = None):
    """Changes the name of the given vector_index"""

    # if the client is not provided, create a new one. Uses the OpenAI key
    client = OpenAI() if client is None else client

    vector_store = client.vector_stores.update(
        vector_store_id=vector_id,
        name=name,
        expires_after={
            'anchor':'last_active_at',
            'days': expires_after
            }
        )

def check_vector_store(vector_id: str, client: OpenAI|None = None):
    """Checks if the given vector_index is expired or active in the OpenAI Cloud"""
    client = OpenAI() if client is None else client

    try:
        vector_store = client.vector_stores.retrieve(vector_store_id=vector_id)
        
        if vector_store.status == 'expired':
            logger.debug(f"Vector Store {vector_id} is expired")
            return False
        else:
            logger.debug(f"Vector Store {vector_id} is active")
            return True
    
    except BadRequestError as e:
        if e.code == 'expired':
            #progress_bar.log_message(f"Error: Vector code {vector_id} has expired. Creating new vector index...")
            frappe.msgprint(f"[xail-chatbot] Error:    Vector code {vector_id} has expired. Creating new vector index...")
            logger.debug(f"Vector Store {vector_id} is expired")
            return False
        else:
            #progress_bar.log_message(f"Error: {e}")
            frappe.msgprint(f"[xail-chatbot] Error:    {e}")
            return False
    
    except NotFoundError as e:
        logger.debug(f"Vector Store {vector_id} does not exist.")
        frappe.msgprint(f"[xail-chatbot] Error:    Vector code {vector_id} does not exist. Creating New Vector Index...")
        return None

    except ValueError as e:
        logger.debug(f"Value error {e}")
        if hasattr == 'code':
            frappe.msgprint(f"[xail-chatbot] ValueError: {e.code}")
        elif hasattr == 'message':
            frappe.msgprint(f"[xail-chatbot] ValueError: {e.message}")
        else:
            frappe.msgprint(f"[xail-chatbot] ValueError: {e}")
        
        return None

    except Exception as e:
        logger.debug(f"Unexpected Error: {e}")
        frappe.msgprint(f"[xail-chatbot] Unexpected Error:    {e}")
        return None
        

