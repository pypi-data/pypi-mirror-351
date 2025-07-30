import os
import frappe

from typing import Iterable
from openai import OpenAI, NotFoundError

from xursparks.error.main import GenericXursparksException
from .callbacks import XAILEventHandler


class AgentAssistant:
    def __init__(self, 
                    file_path: None|Iterable[str] = None, # used for vector store
                    file_names: None|Iterable[str] = None, # used for vector store
                    vector_id: None|str = None, 
                    client: OpenAI|None = None, 
                    assistant_id: None|str = None, 
                    thread_id: str|None = None,
                    system_context: str|None = None,
                    model: str|None = 'gpt-4o',
                    name: str|None = None,
                    description: str|None = "",
                    temperature: int = 0, # used for vector store
                    max_chunk_size_token: int = 800, # used for vector store
                    chunk_overlap_token: int = 400, # used for vector store
                    streaming: bool = True,
                    callback_handler: list|None = None,
                    **kwargs
                ):
        """Interface for the OpenAI Assistant.
            Designed to match usage of previous version using llama-index and langchain"""
    
        print("[xail-chatbot] Log:    Initializing Assistant...")
        self.file_path = file_path # used for vector store
        self.file_names = file_names # used for vector store
        self.assistant_id = assistant_id
        self.thread_id = thread_id
        self.system_context = system_context
        self.name = name
        self.description = description
        self.temperature = temperature # used for vector store
        self.model = model
        self.client = client or OpenAI()
        self.max_chunk_size_token = max_chunk_size_token # used for vector store
        self.chunk_overlap_token = chunk_overlap_token # used for vector store
        self.streaming = streaming
        self.callback_handler = callback_handler[0] if isinstance(callback_handler, list) else callback_handler
        self.assistant_id = assistant_id
        print("HELLO!")
        if self.file_path is not None and vector_id is None or not vector_id:
            print("[xail-chatbot] Warning:    Vector ID is not provided. Creating new Indices from files")
            self.vector_store = self._create_vector_storage_()
             
        elif vector_id is not None:
            print("[xail-chatbot] Log:    Loading index from provided vector ID")
            self.vector_id = vector_id

        else:
            raise GenericXursparksException("[xail-chatbot] Error:    Vector ID nor File Path is provided. Please provide either one")

        self.assistant = self.create_assistant()
        if self.vector_id is not None:
            if self.vector_id not in self.assistant.tool_resources.file_search.vector_store_ids:
                print(f"[xail-chatbot] Log:    Adding {self.vector_id} to the Assistant '{self.assistant_id}'")
                self.assistant = self.update_assistant(self.assistant.id, vector_store_id=self.vector_id)
            else:
                print(f"[xail-chatbot] Log:    Vector ID '{vector_id}' already added to assistant")
        
        print(f"[xail-chatbot] Log:    Assistant '{self.assistant_id}' Initialized!")

    def create_assistant(self, 
                        model: str="gpt-4o",
                        system_context: str|None = None, 
                        name:str|None=None,
                        description:str|None=None, 
                        temperature: int = 0
                        ):
        
        """Creates OpenAI Assistant"""
        def _make_assistant_(self, model, name, description, system_context, temperature):
            print(f"[xail-chatbot] Log:    Creating a new Assistant")
            return self.client.beta.assistants.create(
                model=model,
                name=name,
                description=description,
                instructions=system_context,
                tools=[{"type": "file_search"}],
                temperature=temperature,
            )


        model = self.model or model
        system_context = self.system_context or system_context
        description = self.description or description
        name = self.name or name
        temperature = self.temperature or temperature
        
        if self.assistant_id is not None:
            try:
                print(f"[xail-chatbot] Log:    Retrieving Assistant '{self.assistant_id}'")
                assistant = self.client.beta.assistants.retrieve(self.assistant_id)
                print(f"[xail-chatbot] Log:    Assistant '{assistant.id}' retrieved")
            except:
                print(f"[xail-chatbot] Log:    Retrieving Assistant '{self.assistant_id}' failed. :(")
                assistant = _make_assistant_(self, model, name, description, system_context, temperature)

        else:
            assistant = _make_assistant_(self, model, name, description, system_context, temperature)

        self.assistant_id= assistant.id
        return assistant

    def update_assistant(self, assistant_id: str|None = None, vector_store_id: str|None = None):
        """Adds the vector store to an assistant"""
        assistant_id = assistant_id or self.assistant_id


        if hasattr(self, 'vector_id'):
            if self.vector_id is not None:
                vector_store_id = self.vector_id
        elif vector_store_id is None:
            _ = self._create_vector_storage_()

        assistant = self.client.beta.assistants.update(
            assistant_id = assistant_id,
            tool_resources={'file_search': {'vector_store_ids': [vector_store_id]}}
        )

        return assistant
    
    def _create_message_(self,message:str,*,client:OpenAI|None=None, thread_id:str|None=None):
        """Creates message and thread to be used by assistant"""
        client = client or self.client

        if thread_id is None:
            thread = client.beta.threads.create()
            self.thread_id = thread.id
        
        thread_id = self.thread_id if thread_id is None else thread_id

        message = client.beta.threads.messages.create(
            thread_id= thread_id,
            role="user",
            content=message
        )
        return message
    
    def invoke(self, message:str|dict, *, 
               client: OpenAI|None = None, 
               thread_id:str|None=None, 
               assistant_id:str|None=None, 
               instructions:str|None=None,
               **kwargs):
        """ Method used to call the Assistant and get its reply.
        Designed to be backwards compatible with the old version
        Input
            client: Optional|The OpenAI Client
            thread_id: Optional|Thread ID to be used. If None, creates a new thread.
            assistant_id: Optional| If empty, will use the given assistant ID during initialization
            instructions: Optional| Additional instructions to the chatbot for the message
        Output
            Response by the Assistant to the question asked
        Usage Samples
            For New Conversation:
                agent = AgentAssistant(...)
                print(agent.invoke("This is my Sample Question"))
            For Continuing Conversation:
                print(agent.invoke("This is my additional Sample Question", thread_id=agent.thread_id))
        """
        client = self.client or client
        thread_id = self.thread_id if thread_id is None else thread_id

        if assistant_id is None and self.assistant_id is None:
             assistant_id = self.create_assistant()
        else:
             assistant_id = self.assistant_id if assistant_id is None else assistant_id

        user_messages = self._create_message_(message, thread_id=thread_id, client=client)


        if not self.streaming:
            run = client.beta.threads.runs.create_and_poll(
                thread_id = self.thread_id,
                assistant_id = assistant_id,
                instructions=instructions
            )

            messages = client.beta.threads.messages.list(
                thread_id=self.thread_id
            )

            agent_reply = messages.data[0].content[0].text.value
            return agent_reply
         
        elif self.streaming:
            if self.callback_handler is None:
                 raise GenericXursparksException('[xail_chatbot] Log:    Event Handler needed for Streaming Events. Please pass an EventHandler in the parameter "callback_handler"')

            with client.beta.threads.runs.stream(
                    thread_id=self.thread_id,
                    assistant_id=assistant_id,
                    instructions=instructions,
                    event_handler=self.callback_handler,
                ) as stream:
                    print("[xail_chatbot] Log:    Ongoing streaming")
                    stream.until_done()
                    return stream.message


    def _create_vector_storage_(self,name:str=None, file_path:str=None):
        """Creates Vector Store"""

        file_path = file_path or self.file_path

        name = "File" if name is None else name
        vector_store = self.client.beta.vector_stores.create(
            name=name,
            expires_after={
                "anchor": "last_active_at",
                "days": 7
            },
            chunking_strategy={
                "type":"static",
                "static": {
                    "max_chunk_size_tokens": self.max_chunk_size_token,
                    "chunk_overlap_tokens": self.chunk_overlap_token
                }
            }

        )

        if file_path is not type(list):
            file_paths = [file_path]
        else:
            file_paths = file_path

        print("[xail_chatbot] Log:    Creating Index..")
        file_streams=[]
        for path in file_paths:
            file_path = os.path.join(frappe.get_site_path(),path.lstrip("/"))
            file_streams.append(open(file_path,"rb"))
            print(f"[xail-chatbot] Log:    File stream for {path} created")

        _file_batch_ = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )

        self.vector_id = vector_store.id
        
        return vector_store

    def _add_file_to_vector_storage(self, file_paths):
        """Loads files from file path and adds to vector storage"""
        file_streams = [open(path, "rb") for path in file_paths]
        _file_batch_ = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id = self.vector_id, files=file_streams
        )

    def create_vector_indices(self, file_paths:str, name: str = None, vector_id: str = None, client: OpenAI = None,**kwargs) -> str:
        """ Creates and updates the vector index to be used.

        Parameters:
        file_paths: Required, path or path-like object, Path to file containing list of document paths.
        name: Optional, str, name of the vector storage.
        vector_id: Optional, str, id of the vector_id.

        Returns:
        vector_id
        
        """   

        def _load_files_(doc_path: str)->list:
            """Processes the text file into a list of paths to be used."""
            paths = []
            with open(doc_path, 'r') as file:
                first_line = file.readline()
                if not first_line:  # Check if File is Empty
                    raise("[xail_chatbot] Error:    The file is empty. It should contain list of paths")
                else:
                    print("[xail_chatbot] Log:    Loading Paths...")
                    paths.append(first_line.strip()) # Add the first line to the list if not empty
                    
                    # Iterate through the rest of the lines
                    for line in file:
                        paths.append(line.strip())  # Process each line
                
                return paths

        file_paths = _load_files_(file_paths)

        client = OpenAI() if client is None else client

         
        if vector_id is not None:
            try:
                # If vector store found, delete the vector storage and then generate again
                vector_store = client.beta.vector_stores.delete(vector_store_id=vector_id)

            except NotFoundError:
                raise GenericXursparksException(f"[xail_chatbot] Error:    Vector Store with ID '{vector_id}' does not exist!")

        self._create_vector_storage_(name, file_path=file_paths)
         
        return self.vector_id

class NLPAgent:

    def __init__(self,
            model: str,
            llm_ver: str,
            temperature: float,
            embed_batch_size: int,
            streaming: bool,
            verbose: bool, 
            max_chunk_size_token = 800,
            chunk_overlap_token = 400,
            callback_handler = None,
            vector_id:str = None,
            file_path:str = None,
            metadata_name:str = None,
            metadata_desc:list[str] = None,
            system_context:str = None,
            assistant_id: str = None,
            **kwargs):

            self.model = model
            self.llm_ver = llm_ver
            self.temperature = temperature
            self.embed_batch_size = embed_batch_size
            self.streaming = streaming
            self.verbose = verbose
            self.max_chunk_size_token = max_chunk_size_token
            self.chunk_overlap_token = chunk_overlap_token
            self.callback_handler = callback_handler
            self.vector_id = vector_id
            self.file_path = file_path
            self.metadata_name = metadata_name
            self.metadata_desc = metadata_desc
            self.system_context =system_context
            self.assistant_id = assistant_id
            self.__dict__.update(kwargs) #if any kwargs are passed during the initialization, will pass during agent creation

            if self.metadata_name is None or self.metadata_name.strip() == '':
                self.metadata_name = "xurpas_faq"
            if self.metadata_desc is None or self.metadata_desc.strip() == '':
                self.metadata_desc = "Provides information about Xurpas. Use a detailed plain text question as input to the tool."
            if self.system_context is None or self.system_context.strip() == '':
                raise GenericXursparksException("[xail_chatbot] Error:    Must Provide System Context")
            
    def get_agent(self, **kwargs):
        agent = AgentAssistant(
            file_path = self.file_path,
            system_context = self.system_context,
            vector_id = self.vector_id,
            model = self.llm_ver,
            name = self.metadata_name,
            description = self.metadata_desc,
            temperature = self.temperature,
            max_chunk_size_token = self.max_chunk_size_token,
            chunk_overlap_token = self.chunk_overlap_token,
            assistant_id=self.assistant_id,
            streaming = self.streaming,
            callback_handler = self.callback_handler,
            **kwargs
        )

        return agent
