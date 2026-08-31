"""
HTTP layer over the scansion engine.

The dictionary and the mined suffix table load once at import and stay in
memory — they're ~126k entries, so building them per request would dominate
response time.
"""

from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from scansion import analyze_line, analyze_poem, rhyme_scheme

app = FastAPI(title="Scansion", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PoemIn(BaseModel):
    text: str = Field(..., max_length=20000)


class WordOut(BaseModel):
    text: str
    syllables: int
    stress: str
    certain: bool
    demoted: bool
    alternatives: List[str]


class SubOut(BaseModel):
    foot: int
    expected: str
    actual: str
    kind: str


class LineOut(BaseModel):
    text: str
    pattern: str
    marked: str
    meter: Optional[str]
    confidence: Optional[float]
    words: List[WordOut]
    substitutions: List[SubOut]
    caesura: Optional[int]
    notes: List[str]


def _line_payload(a) -> LineOut:
    return LineOut(
        text=a.text,
        pattern=a.pattern,
        marked=a.marked,
        meter=str(a.meter) if a.meter else None,
        confidence=round(a.meter.confidence, 3) if a.meter else None,
        words=[WordOut(text=w.text, syllables=w.syllables, stress=w.stress,
                       certain=w.certain, demoted=w.demoted,
                       alternatives=w.alternatives) for w in a.words],
        substitutions=[SubOut(foot=s.foot_index, expected=s.expected,
                              actual=s.actual, kind=s.kind) for s in a.substitutions],
        caesura=a.caesura,
        notes=a.performance_notes(),
    )


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/scan/line", response_model=LineOut)
def scan_one(body: PoemIn):
    return _line_payload(analyze_line(body.text))


@app.post("/scan")
def scan(body: PoemIn):
    result = analyze_poem(body.text)
    return {
        "dominant_meter": result["dominant_meter"],
        "meter_counts": result["meter_counts"],
        "rhyme_scheme": result["rhyme_scheme"],
        "line_count": result["line_count"],
        "lines": [_line_payload(a) for a in result["lines"]],
    }


@app.post("/rhyme")
def rhyme(body: PoemIn):
    lines = [ln for ln in body.text.splitlines() if ln.strip()]
    return {"scheme": "".join(rhyme_scheme(lines))}
