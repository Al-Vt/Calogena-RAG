import os 
import psycopg
from dotenv import load_dotenv 
from fastapi import FastAPI 
from mistralai.client import Mistral 
from pgvector.psycopg import register_vector 
from sentence_transformers import SentenceTransformer


load_dotenv()

conn = psycopg.connect(autocommit=True)
register_vector(conn)

model = SentenceTransformer("intfloat/multilingual-e5-small")

app = FastAPI()

def ask_LLM(question : str) -> str:
    """
    Feature for submitting a request to our AI assistant.
    question : str
    """
    query_embedding = model.encode("query: " + question, normalize_embeddings=True)

    all_informations = conn.execute(
        """
        SELECT d.name, c.starting_page, c.ending_page, c.text
        FROM chunk c 
        JOIN document d ON d.id = c.document_id
        ORDER BY c.embedding <=> %s
        LIMIT 5
        """,
        (query_embedding,),
    ).fetchall()

    context = str(all_informations)

    system_prompt = """Tu es un assistant IA qui utilise les documents publics disponible sur Calogena pour répondre. 
    Répond à cette question en utilisant uniquement les passages fournis. 
    Cite le document et la page. 
    Si les passages ne permettent pas de répondre à la question, dit que tu ne sais pas et n'invente rien."""

    user_prompt = f"""
    passages : {context}
    Question : {question}
    """

    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    chat_response = client.chat.complete(
        model="mistral-medium-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return(chat_response.choices[0].message.content)


@app.get("/ask")
def ask(question: str):
    return ask_LLM(question)