# -*- coding: utf-8 -*-

import os
import openai
import uuid
from sklearn.metrics.pairwise import cosine_similarity
import time

def main(openaiorganization = "org-PSlM10cRMQXx9N1Ogi3l7ino", openaiapikey = "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" , text = "Apples are red", query= "Are apples green", context = "you are an apple", num_results = 7, chunk_size = 150):
    # Function to retry OpenAI requests
    def retry_openai_request(fn, max_retries=5):
        for attempt in range(max_retries):
            try:
                return fn()
            except Exception as e:
                if attempt < max_retries - 1:  # i.e. if it's not the final attempt
                    print(f"Retrying request... (Attempt {attempt + 2})")
                    time.sleep(1)  # Wait for a second before making the next call
                    continue
                else:
                    raise e

    # Function to split text into chunks
    def split_text_into_chunks(text, chunk_size):
        words = text.split()
        return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

    # Function to create an embedding for a text chunk
    def create_embedding(chunk):
        def make_request():
            return openai.Embedding.create(
                input=chunk,
                model="text-embedding-ada-002"
            )
        response = retry_openai_request(make_request)
        return response["data"][0]["embedding"]

    # Function to create an embedding for a query
    def create_query_embedding(query):
        def make_request():
            return openai.Embedding.create(
                input=query,
                model="text-embedding-ada-002"
            )
        response = retry_openai_request(make_request)
        return response["data"][0]["embedding"]


    # Set up OpenAI credentials
    openai.organization = openaiorganization
    openai.api_key = openaiapikey

    # Initialize text
    print("Initializing text...")
    text = text

    # Split text into chunks
    print("Splitting text into chunks...")
    text_chunks = split_text_into_chunks(text, chunk_size)

    # Create embeddings for text chunks
    print("Creating embeddings...")
    embeddings = [(uuid.uuid4().hex, create_embedding(chunk), {"text": chunk}) for chunk in text_chunks]

    # Print message indicating that embeddings have been created
    print("Embeddings created.")

    # Define query
    query = query

    # Create embedding for query
    print("Creating query embedding...")
    query_embedding = create_query_embedding(query)

    # Set number of results to return
    num_results = num_results

    # Compute cosine similarity between query embedding and text chunk embeddings
    results = [(cosine_similarity([query_embedding], [embedding])[0][0], id, meta) for id, embedding, meta in embeddings]

    # Sort results by similarity score
    print("Sorting results...")
    results.sort(reverse=True)

    # Print top results
    print("Top results:")
    for score, id, meta in results[:num_results]:
        print(f"Text chunk: {meta['text']}")
        print(f"Similarity score: {score}")
        print()

    # Generate answer using the GPT3.5 turbo model
    print("Generating answer using the GPT3.5 turbo model...")
    context = " ".join([meta['text'] for _, _, meta in results[:num_results]])

    # Set up prompt for chat completion request
    prompt = f"""
    Context: {context}
    Question: {query}
    """

    # Function to create chat completion request
    def create_chat_completion():
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=1,
        )

    # Send chat completion request and print response
    response = retry_openai_request(create_chat_completion)
    print("Question:", query)
    print("Answer:")
    print(response['choices'][0]['message']['content'].strip())

if __name__ == '__main__':
    main()