# Calogena RAG

An AI assistant that references public documents available on Calogena, such as the expert opinions of the ASNR, the French Nuclear Safety and Radiation Protection Authority, or the consultation document published by Calogena.

## Organization

* The text is extracted from the PDFs, then cleaned and linked back to its source along with the corresponding pages
* It is then broken down into chunks, which are subsequently converted into vectors that allow the meaning of the text to be linked to the meaning of the questions asked
* This is then stored in a vector database using PostgreSQL and the pgvector extension
* The questions themselves are converted into vectors, enabling semantic search. Up to five chunks whose meaning matches the question are extracted to answer it.
* An LLM, here Mistral’s, draws on these chunks to answer the question. It does not invent anything if the documents do not provide a way to answer the question

## Data engineering details

* The text of each document is linked to the corresponding document and pages based on the first and last characters of the chunk
* The `register_pdf` text extraction function allows you to choose the extraction mode. For example, “layout” works best for the ASNR expert opinion, and “plain” works best for the College's opinion. Each document is processed using its own mode
* Cleaning: removal of extraneous headers and footers, lines split in the middle of a sentence are rejoined, multiple blank lines are removed. The associated functions are `clean_text`, `remove_parasite`, `remove_false_start_consultation`, `delete_footnote`, and `remove_footnote`
* The `boolean_end_page_line` function creates a Boolean column to identify pages whose last line is cut off. The `pdf_reconstruction` function rejoins these sentences
* Pages containing graphs and tables of contents are filtered based on the length of the text on the page. Pages with fewer than 1,000 characters are therefore deleted after being verified

## Chunking et embedding details

* The splitter used is LangChain's `RecursiveCharacterTextSplitter`. It returns the starting position of each chunk, which is then used by the `find_page` function to locate the corresponding page
* Paragraphs are 1,000 characters long with 150 characters of overlap
* The `intfloat/multilingual-e5-small` model is used for embedding. It was chosen because it keeps the data local, meaning it never leaves the user’s computer, and it is also fast, free, and multilingual.
* Its vectors have 384 dimensions

## Vector database details

* pgvector was chosen for vectors, texts, and source documents, all stored in the same database and linked by keys. It is also well-suited to our current volume of chunks. A single SQL query can find nearby chunks and retrieve the source documents
* The tables are: `document`, `chunk`, `query`, with the join table `chunk_used_by_query` linking queries to chunks
* `UNIQUE` was used to prevent duplicates during reloading, and `ON DELETE CASCADE` was used to ensure no chunk exists without a document
* Searches are performed using cosine similarity
* Docker Compose is used to start the database. The credentials must be in a `.env` file

## LLM details

* Mistral was chosen because Calogena aims to develop a sovereign heating solution.
* It responds only to the five chunks that received it. It is programmed to respond with nothing other than “I don't know” if none of the chunks answer the question.

## API details

* FastAPI was used
* There's only one option: ask it a question. It converts the question into a vector, feeds the 5 chunks to Mistral's LLM, and returns the answer
* The sources are cited directly in the LLM's response
* The embedding model and the database connection are loaded only once at startup

## Start the project

* Set up the environment and install the dependencies:

```bash
conda create -n  rag-calogena python=3.11

conda activate rag-calogena 

pip install -r requirements.txt 
```

* Fill in the `.env.example` file with your keys and credentials, and rename it to `.env`
* Start Docker:

```bash
docker compose up -d
```

* PostgreSQL is running on port `55432`
* Adminer is at `http://localhost:8082`
* Run the notebooks in order. This allows you to retrieve the data, since `data/raw` is in the .gitignore file.
* Start API:

```bash
uvicorn api:app --reload
```

* Then open `http://localhost:8000/docs` and try `GET /ask`


