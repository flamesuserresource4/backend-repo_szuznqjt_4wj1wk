import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None  # [{"role": "user|assistant", "content": "..."}]


class ChatResponse(BaseModel):
    reply: str
    suggestions: List[str] = []


def generate_reply(msg: str) -> ChatResponse:
    """Simple, deterministic Norwegian helper tuned for Nex Rail AS topics.
    This avoids external APIs and responds to common intents.
    """
    text = (msg or "").strip().lower()

    # Greetings
    if any(w in text for w in ["hei", "hallo", "heisann", "god dag"]):
        return ChatResponse(
            reply=(
                "Hei! Hva kan vi hjelpe deg med i dag? Vi tilbyr nybygg, vedlikehold, sikkerhet og beredskap innen jernbane."
            ),
            suggestions=[
                "Fortell meg om nybygg",
                "Hvordan fungerer vedlikehold?",
                "Hva innebærer sikkerhet?",
                "Har dere beredskap 24/7?",
            ],
        )

    # Services
    if "nybygg" in text or "ny bygg" in text:
        return ChatResponse(
            reply=(
                "Nybygg: Vi prosjekterer og bygger nye jernbaneanlegg og spor. Vi håndterer planlegging, logistikk, bygging og kvalitetssikring, med fokus på sikker fremdrift og levering til avtalt tid."
            ),
            suggestions=["Kan jeg få et tilbud?", "Hvilke regioner dekker dere?"],
        )

    if "vedlikehold" in text:
        return ChatResponse(
            reply=(
                "Vedlikehold: Vi utfører forebyggende og korrektivt vedlikehold på spor. Arbeidet tilpasses trafikk og sikkerhetskrav, med dokumentasjon etter ferdigstillelse."
            ),
            suggestions=["Kan dere nattarbeid?", "Hva er responstiden deres?"],
        )

    if "sikkerhet" in text or "sha" in text:
        return ChatResponse(
            reply=(
                "Sikkerhet: Vi følger strenge prosedyrer, risikovurderer oppdrag og bruker sertifisert personell. HMS og kvalitet står alltid først."
            ),
            suggestions=["Hvilke sertifiseringer har dere?", "Hvordan planlegger dere sikker jobbanalyse?"],
        )

    if "beredskap" in text or "uhell" in text or "akutt" in text:
        return ChatResponse(
            reply=(
                "Beredskap: Vi tilbyr døgnkontinuerlig beredskap for uforutsette hendelser, med rask mobilisering av mannskap og utstyr for å sikre og gjenåpne strekninger."
            ),
            suggestions=["Hvordan kontakter jeg beredskap?", "Dekker dere hele Norge?"],
        )

    # KL/signal clarification
    if "kl" in text or "kontaktledning" in text or "signal" in text:
        return ChatResponse(
            reply=(
                "Vi fokuserer på nybygg, vedlikehold, sikkerhet og beredskap. KL- og signalarbeid inngår ikke i vårt tilbud per nå."
            ),
            suggestions=["Fortell om nybygg", "Hva med vedlikehold?"],
        )

    # Quotes and contact
    if any(w in text for w in ["tilbud", "befaring", "kontakt", "e-post", "telefon"]):
        return ChatResponse(
            reply=(
                "For tilbud eller befaring: Send oss en melding via kontaktskjemaet nedenfor, så svarer vi raskt. Legg gjerne ved kort beskrivelse av oppdraget og ønsket tidsramme."
            ),
            suggestions=["Hvor raskt kan dere starte?", "Hvilke områder dekker dere?"],
        )

    # Coverage
    if any(w in text for w in ["område", "region", "hvor", "dekker"]):
        return ChatResponse(
            reply=(
                "Vi leverer oppdrag over hele Norge. Mobil gjennomføring med mannskap og utstyr etter behov."
            ),
            suggestions=["Kan dere nattarbeid?", "Gi meg et tilbud"],
        )

    # Fallback
    return ChatResponse(
        reply=(
            "Jeg forstår. Kan du beskrive behovet litt nærmere? Vi kan hjelpe med nybygg, vedlikehold, sikkerhet og beredskap innen jernbane."
        ),
        suggestions=[
            "Fortell om nybygg",
            "Hvordan fungerer vedlikehold?",
            "Hva innebærer sikkerhet?",
            "Har dere beredskap 24/7?",
        ],
    )


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    return generate_reply(req.message)


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        # Try to import database module
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"

            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
