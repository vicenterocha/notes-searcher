import os
import glob
from pathlib import Path
import frontmatter
import lancedb
import pandas as pd
import pyarrow as pa
from sentence_transformers import SentenceTransformer
import ollama

class NotesSearcher:
    def __init__(self, notes_dir, db_path="data/notes-db"):
        self.notes_dir = Path(notes_dir)
        self.db = lancedb.connect(db_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def find_markdown_files(self):
        """Find all markdown files in the notes directory"""
        return glob.glob(str(self.notes_dir / "**/*.md"), recursive=True)
    
    def process_note(self, filepath):
        """Process a single note file and return its content and metadata"""
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            content = post.content
            metadata = post.metadata
            return {
                "path": str(filepath),
                "content": content,
                "title": metadata.get('title', os.path.basename(filepath)),
                "tags": metadata.get('tags', [])
            }
    
    def create_embedding(self, text):
        """Create an embedding for the given text"""
        return self.model.encode(text)
    
    def index_notes(self):
        """Index all notes in the directory"""
        markdown_files = self.find_markdown_files()
        data = []
        
        for filepath in markdown_files:
            note = self.process_note(filepath)
            embedding = self.create_embedding(note['content'])
            data.append({
                "vector": embedding.tolist(),
                "path": note['path'],
                "content": note['content'],
                "title": note['title'],
                "tags": note['tags']
            })
        
        # Create or recreate the table
        if "notes" in self.db.table_names():
            self.db.drop_table("notes")
        
        self.db.create_table("notes", data=data)
        print(f"Indexed {len(data)} notes")
    
    def search(self, query, k=5):
        """
        Search for notes relevant to the query, then use LLM to synthesize a single response
        from the most relevant notes
        """
        # Get embedding for the query
        query_embedding = self.create_embedding(query)
        
        # Search in LanceDB
        tbl = self.db.open_table("notes")
        results = tbl.search(query_embedding).limit(k).to_list()
        
        # Prepare context from relevant notes
        context = "\n\n---\n\n".join([
            f"Note: {result['title']}\n\nContent: {result['content'][:1500]}"  # Limit each note to 1500 chars
            for result in results
        ])
        
        # Create a comprehensive prompt for the LLM
        prompt = f"""Based on the following query: "{query}"

Here are the most relevant notes I found:

{context}

Please provide a comprehensive answer to the query using ONLY the information from these notes. 
If the notes don't contain relevant information to answer the query, please state that clearly.
Format your response in a clear and concise way, citing specific notes when relevant."""
        
        # Get LLM response
        ollama_client = ollama.Client()
        response = ollama_client.generate(model='mistral', prompt=prompt)
        
        return {
            "answer": response.response,
            "sources": [
                {
                    "title": result["title"],
                    "path": result["path"],
                    "relevance_score": float(result["_distance"])
                }
                for result in results
            ]
        }

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Search through Obsidian notes')
    parser.add_argument('--notes-dir', required=True, help='Directory containing Obsidian notes')
    parser.add_argument('--index', action='store_true', help='Reindex all notes')
    parser.add_argument('--query', help='Search query')
    
    args = parser.parse_args()
    
    searcher = NotesSearcher(args.notes_dir)
    
    if args.index:
        searcher.index_notes()
    
    if args.query:
        result = searcher.search(args.query)
        print("\nAnswer:")
        print("=======")
        print(result["answer"])
        print("\nSources:")
        print("========")
        for source in result["sources"]:
            print(f"\n- {source['title']}")
            print(f"  Path: {source['path']}")
            print(f"  Relevance Score: {source['relevance_score']:.4f}")
