-- enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- One document is one row 
CREATE TABLE IF NOT EXISTS document (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    source TEXT
);

-- One chunk is one row, with page associated and its embedding 
CREATE TABLE IF NOT EXISTS chunk ( 
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES document(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    starting_page INTEGER NOT NULL,
    ending_page INTEGER NOT NULL,
    starting_character INTEGER NOT NULL, 
    ending_character INTEGER NOT NULL, 
    text TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    UNIQUE (document_id, chunk_index)
);

-- one query is one row 
CREATE TABLE IF NOT EXISTS query (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    creation_time TIMESTAMP NOT NULL DEFAULT NOW()
);

-- shared table showing the chunks used per question
CREATE TABLE IF NOT EXISTS chunk_used_by_query (
    query_id INTEGER NOT NULL REFERENCES query(id) ON DELETE CASCADE,
    chunk_id INTEGER NOT NULL REFERENCES chunk(id) ON DELETE CASCADE,
    score REAL NOT NULL,
    PRIMARY KEY (query_id, chunk_id)
);

-- create an index by vector
CREATE INDEX IF NOT EXISTS chunk_embedding_index
    ON chunk USING hnsw (embedding vector_cosine_ops);