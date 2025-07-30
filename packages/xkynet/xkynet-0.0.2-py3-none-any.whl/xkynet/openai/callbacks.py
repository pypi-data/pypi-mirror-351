import os
import re
from typing_extensions import override

from openai import AssistantEventHandler



class XAILEventHandler(AssistantEventHandler):
    def __init__(self, session, **kwargs):
        print("[xail_chatbot] Log:    Streaming: Initializing Callback")
        self.session = session
        super().__init__()
        print("[xail_chatbot] Log:    Streaming: Callback initialized!")

    def process_text(self, text):
        # Replace **text** with <b>text</b>
        converted_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return converted_text
                
    @override
    def on_text_created(self, text) -> None:
        # Send each letter as it is created
        print("[xail_chatbot] Log:    Streaming: Text Created", flush=True)

    @override
    def on_text_delta(self, data, snapshot) -> None:
        text = self.process_text(data.value)


