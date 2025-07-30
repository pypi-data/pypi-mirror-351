from graphrag.callbacks.query_callbacks import QueryCallbacks

class StreamingHandler(QueryCallbacks):
    def __init__(self, session):
        print("GraphRag Streamer Callback Initialized ")
        self.session = session
        super().__init__()
    
