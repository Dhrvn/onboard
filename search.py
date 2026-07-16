# search.py
# This is the "brain" of our RAG system.
# It takes a question and finds the most relevant 
# paragraphs from all 9 docs.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# ============================================================
# WHAT IS TF-IDF?
# TF-IDF = Term Frequency - Inverse Document Frequency
# It's a way to turn text into numbers so we can 
# mathematically compare how similar two pieces of text are.
#
# Simple version: if your question contains "SAP" and a 
# chunk also contains "SAP" a lot, it scores high.
# Common words like "the" and "is" are ignored automatically.
#
# WHAT IS COSINE SIMILARITY?
# Once text is converted to numbers (vectors), cosine 
# similarity measures the angle between them.
# Score of 1.0 = identical meaning
# Score of 0.0 = completely unrelated
# ============================================================

def load_and_chunk_docs(docs_folder="docs", chunk_size=400):
    """
    Reads all docs and splits them into chunks.
    
    chunk_size = roughly how many words per chunk.
    400 words is a good balance — specific enough to be 
    relevant, large enough to have full context.
    """
    chunks = []  # List of text chunks
    chunk_sources = []  # Which doc each chunk came from
    
    for filename in sorted(os.listdir(docs_folder)):
        if not filename.endswith(".md"):
            continue
            
        filepath = os.path.join(docs_folder, filename)
        with open(filepath, "r") as f:
            content = f.read()
        
        # Split by double newline (paragraph breaks)
        # This keeps related sentences together
        paragraphs = content.split("\n\n")
        
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph keeps us under chunk_size
            # words, add it to the current chunk
            if len((current_chunk + " " + paragraph).split()) < chunk_size:
                current_chunk += " " + paragraph
            else:
                # Current chunk is full — save it and start new one
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    chunk_sources.append(filename)
                current_chunk = paragraph
        
        # Don't forget the last chunk of each doc
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
            chunk_sources.append(filename)
    
    print(f"✅ Split {len(os.listdir(docs_folder))} docs into {len(chunks)} searchable chunks")
    return chunks, chunk_sources


def find_relevant_chunks(question, chunks, chunk_sources, top_k=5):
    """
    Given a question, finds the top_k most relevant chunks.
    
    top_k=5 means we return the 5 most relevant paragraphs.
    These are what gets sent to Claude — not the whole docs.
    """
    if not chunks:
        return [], []
    
    # Combine question with all chunks for vectorization
    # The vectorizer needs to see all text at once to build
    # its vocabulary
    all_text = [question] + chunks
    
    # Convert all text to TF-IDF vectors (numbers)
    vectorizer = TfidfVectorizer(
        stop_words="english",  # ignore "the", "is", "and" etc
        ngram_range=(1, 2)     # consider single words AND pairs
                               # e.g. "AWS access" as one concept
    )
    tfidf_matrix = vectorizer.fit_transform(all_text)
    
    # question vector is the first row
    # chunk vectors are all the other rows
    question_vector = tfidf_matrix[0]
    chunk_vectors = tfidf_matrix[1:]
    
    # Calculate similarity between question and every chunk
    similarities = cosine_similarity(question_vector, chunk_vectors)[0]
    
    # Get indices of top_k highest scoring chunks
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    # Return the actual text and source filenames
    relevant_chunks = [chunks[i] for i in top_indices]
    relevant_sources = [chunk_sources[i] for i in top_indices]
    
    return relevant_chunks, relevant_sources


def build_smart_context(question, chunks, chunk_sources, top_k=5):
    """
    Builds the context string to send to Claude.
    Only includes the most relevant chunks, not all docs.
    """
    relevant_chunks, relevant_sources = find_relevant_chunks(
        question, chunks, chunk_sources, top_k
    )
    
    context = "RELEVANT SECTIONS FROM NEXUS LABS KNOWLEDGE BASE:\n\n"
    
    for i, (chunk, source) in enumerate(zip(relevant_chunks, relevant_sources)):
        context += f"[Source: {source}]\n{chunk}\n\n---\n\n"
    
    return context


# ============================================================
# TEST — run this file directly to see chunking in action
# python3.11 search.py
# ============================================================
if __name__ == "__main__":
    chunks, sources = load_and_chunk_docs()
    
    print(f"\nTotal chunks: {len(chunks)}")
    print(f"\nExample chunk from {sources[0]}:")
    print("-" * 40)
    print(chunks[0][:500])
    print("-" * 40)
    
    # Test a search
    test_question = "How does SAP data get ingested?"
    relevant, rel_sources = find_relevant_chunks(
        test_question, chunks, sources, top_k=3
    )
    
    print(f"\nTop 3 chunks for: '{test_question}'")
    for i, (chunk, source) in enumerate(zip(relevant, rel_sources)):
        print(f"\n#{i+1} from {source}:")
        print(chunk[:300] + "...")