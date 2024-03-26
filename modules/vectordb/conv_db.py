import chromadb
import pandas as pd
import dataclasses
import os
import logging

log = logging.getLogger(__name__)


class ConvDB():
    def __init__(self, database_path) -> None:
        self.client = chromadb.Client()
        self.db = self.client.get_or_create_collection('conversation_db')
        self.database_path = database_path
        
    def load(self):
        df = pd.read_csv(self.database_path)
        
        metadata = df[['role', 'name', 'time']].to_dict('records')
        documents = df['text'].tolist()
        ids = df['uuid4'].tolist()
        
        self.db.add(documents=documents, metadatas=metadata, ids=ids)
        
    def save(self):
        if os.path.exists(self.database_path):
            original_df = pd.read_csv(self.database_path)
            
        data = self.db.get()
        ids = data['ids']
        metadatas = data['metadatas']
        documents = data['documents']
        
        df = pd.DataFrame()
        df['uuid4'] = ids
        df['text'] = documents
        df['role'] = [m['role'] for m in metadatas]
        df['name'] = [m['name'] for m in metadatas]
        df['time'] = [m['time'] for m in metadatas]
        
        """
        # Combine the original df with the new df
        if os.path.exists(self.database_path):
            original_df = pd.read_csv(self.database_path)
            df = pd.concat([original_df, df])
        """
        df.to_csv(self.database_path, index=False)
    
    def add(self, metadata:dict):
        data = metadata.copy()
        document = data['text']
        uuid4 = data['uuid4']
        data.pop('text')
        data.pop('uuid4')
        self.db.add(documents=[document], metadatas=[data], ids=[uuid4])
        self.save()
        
    def query(self, query_text:str) -> list:
        THRESHOLD = 2
        results = self.db.query(query_texts=[query_text], n_results=2)
        closest_conversations = []
        confidence = results['distances'][0]
        for i, c in enumerate(confidence):
            if c < THRESHOLD:
                closest_conversations.append(results['documents'][0][i])
        
        return closest_conversations
