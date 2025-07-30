import os
import asyncio

import graphrag.api as api

from .utils import load_output

class GraphRagSearcher:
    def __init__(self, context_directory: os.PathLike|dict[os.PathLike], response_type, query, callbacks=None):
        # load the parquet files
        print(f"context directory: {context_directory}")
        self.response_type = response_type
        self.query = query
        self.search_context = load_output(context_directory)
        self.callbacks = callbacks
        print(self.search_context)

    def run_searcher(self, search_context=None, query=None, callbacks=None):
        query = query or self.query
        callbacks = callbacks or self.callbacks
        search_context = search_context or self.search_context

        async def graphrag_search():
            response, context = await api.local_search(
                config=search_context['conf'],
                entities=search_context['entities'],
                communities=search_context['communities'],
                community_reports=search_context['community_reports'],
                text_units=search_context['text_units'],
                relationships=search_context['relationships'],
                covariates=None,  
                community_level=2,
                response_type=self.response_type,
                callbacks=self.callbacks,
                query=self.query,
            )
    
            return response, context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response, context = loop.run_until_complete(graphrag_search())
        loop.close()
        
        return response, context
