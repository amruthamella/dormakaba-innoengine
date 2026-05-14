from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from services.gemini_service import generate_response

app = FastAPI(title="Dormakaba Innovation Blueprint Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BlueprintRequest(BaseModel):
    product: str

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


def build_subphase_prompt(product: str, horizon: str, subphase: str) -> str:

    subphase_details = {
        "0-6 months": {
            "urgency": "IMMEDIATE — must be executable with existing team and budget RIGHT NOW",
            "focus": "Bug fixes, UX improvements, firmware updates, quick integrations, competitive response to recent launches",
            "example_incremental": "Fix the 3-second BLE connection delay reported by 40% of users in app store reviews",
            "example_radical": "Kill the PIN pad entirely — ship a software update making smartphone the only entry method",
            "example_ready": "White-label Allegion Engage mobile credential SDK — faster than building from scratch",
            "example_ootb": "Adopt Tile community find-my-device network model for lost key fob recovery"
        },
        "6-24 months": {
            "urgency": "SHORT-TERM — requires some development but must ship within 2 years",
            "focus": "New hardware features, platform integrations, new market verticals, pricing model experiments",
            "example_incremental": "Add Matter protocol support so the lock works with Apple Home, Google Home, and Alexa natively",
            "example_radical": "Launch access-as-a-service — monthly subscription replaces one-time hardware sale",
            "example_ready": "Integrate HID Global Seos mobile credential platform — already accepted in 100+ countries",
            "example_ootb": "Apply hotel minibar auto-replenishment model — lock auto-orders its own battery replacements via IoT"
        },
        "1-2 years": {
            "urgency": "NEAR-TERM — significant development needed, clear technology path exists",
            "focus": "Platform strategy, API ecosystem, emerging tech adoption from adjacent industries",
            "example_incremental": "Launch dormakaba developer API with 50 pre-built building management system connectors",
            "example_radical": "Replace all credentials with continuous behavioral biometrics — gait, typing pattern, location history",
            "example_ready": "License SALTO SVN offline encrypted node technology for areas with no WiFi coverage",
            "example_ootb": "Apply Spotify Wrapped model — annual access pattern report for building security managers"
        },
        "2-5 years": {
            "urgency": "MID-TERM — technology bets requiring R&D investment now to ship in this window",
            "focus": "AI/ML integration, smart building ecosystem, sustainability, new credential paradigms",
            "example_incremental": "AI anomaly detection that flags unusual access patterns and auto-triggers security alerts",
            "example_radical": "Zero-credential building — ambient AI identifies occupants via computer vision, no device needed",
            "example_ready": "Apply Tesla OTA update model — monetize firmware improvements as premium subscription features",
            "example_ootb": "Borrow Amazon Sidewalk mesh concept — locks form their own city-wide encrypted security mesh"
        },
        "5-10 years": {
            "urgency": "LONG-TERM — paradigm bets, emerging science, blue-sky R&D",
            "focus": "Post-credential security, AI-native access, quantum-safe encryption, ambient intelligence",
            "example_incremental": "Locks that self-heal micro-mechanical failures using shape-memory alloy actuators",
            "example_radical": "Access control without physical locks — AI-managed directed acoustic barriers replace doors",
            "example_ready": "Apply autonomous vehicle sensor fusion (lidar + radar + vision) to replace credential checks",
            "example_ootb": "Structural cryptography — building materials carry access permissions in molecular structure"
        }
    }

    d = subphase_details.get(subphase, subphase_details["0-6 months"])

    return f"""You are a senior innovation strategist at dormakaba, a global access control and security company.
Key competitors: ASSA ABLOY, Allegion (Schlage), HID Global, SALTO Systems, Bosch Security.

Product: "{product}"
Horizon: {horizon} | Sub-phase: {subphase}
Urgency: {d['urgency']}
Strategic focus: {d['focus']}

CRITICAL RULES:
1. Write REAL, SPECIFIC content about "{product}" for the EXACT timeframe "{subphase}"
2. NEVER write placeholder text like "Specific idea title" or "2 sentences on what it is"
3. NEVER copy instruction text into the output fields
4. Ideas for "{subphase}" must be realistic for THAT specific timeframe — not too early, not too late
5. Style guide (do not copy, use as inspiration):
   - Incremental style: "{d['example_incremental']}"
   - Ready-made style: "{d['example_ready']}"
   - Out-of-the-box style: "{d['example_ootb']}"

Return ONLY a valid raw JSON object. No markdown. No code fences. No explanation.

{{
  "subphase": "{subphase}",
  "potential_problems": [
    "Real specific barrier #1 blocking {product} innovation at {subphase} — name the actual constraint with context",
    "Real specific barrier #2 — regulatory, supply chain, channel partner resistance, or technology gap",
    "Real specific barrier #3 — internal capability, certification timeline, or market adoption challenge"
  ],
  "incremental": {{
    "title": "Concrete improvement title for {product} in {subphase} timeframe",
    "description": "What this improvement is and how it works technically. What specific pain point it solves for {product} customers.",
    "rationale": "Why {subphase} is the right window — reference a real market signal, competitor move, or technology readiness",
    "impact": "Specific measurable outcome with numbers where realistic",
    "source": "Based on: a real market trend, user complaint category, or named competitor product"
  }},
  "radical": {{
    "title": "Bold disruptive idea for {product} viable at {subphase}",
    "description": "What category assumption this breaks. What the transformed experience or business model looks like for {product}.",
    "rationale": "What technology shift or market condition makes this radical move viable specifically at {subphase}",
    "impact": "Market disruption potential or revenue model transformation",
    "source": "Based on: specific technology trend, research finding, or competitor signal"
  }},
  "ready_made": {{
    "title": "Existing solution to adopt for {product} within {subphase}",
    "description": "What existing technology from which specific company or industry. Exactly how it applies to {product} and what it enables.",
    "rationale": "Why adopting beats building in this {subphase} window — existing infrastructure or IP available",
    "impact": "Time-to-market advantage and specific business benefit",
    "source": "Based on: the specific company, product, or standard being adopted"
  }},
  "out_of_the_box": {{
    "title": "Cross-industry idea for {product} at {subphase}",
    "description": "Which company or industry this is inspired by and their successful model. How that exact model applies to {product} in a non-obvious way.",
    "rationale": "What the two domains share that makes this cross-industry transfer viable at {subphase}",
    "impact": "Transformational business impact if successfully executed",
    "source": "Based on: the specific company, market model, or technology pattern"
  }}
}}"""


def parse_json_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
        raise ValueError("Could not parse JSON from AI response")


def error_subphase(subphase: str, error: str) -> dict:
    return {
        "subphase": subphase,
        "potential_problems": [
            f"Error generating ideas: {error}",
            "Please retry — may be a temporary API issue",
            "Check your OpenRouter API key has sufficient credits"
        ],
        "incremental":    {"title": "Error — Retry", "description": str(error), "rationale": "", "impact": "", "source": ""},
        "radical":        {"title": "Error — Retry", "description": str(error), "rationale": "", "impact": "", "source": ""},
        "ready_made":     {"title": "Error — Retry", "description": str(error), "rationale": "", "impact": "", "source": ""},
        "out_of_the_box": {"title": "Error — Retry", "description": str(error), "rationale": "", "impact": "", "source": ""}
    }


@app.post("/api/blueprint")
def create_blueprint(request: BlueprintRequest):
    product = request.product.strip()

    if not product or len(product) < 2:
        raise HTTPException(status_code=400, detail="Product name too short")

    blueprint = {
        "product": product,
        "domain": "Access Control & Security",
        "executive_summary": f"Innovation blueprint for {product} — specific ideas across NOW (0-6m, 6-24m), NEXT (1-2yr, 2-5yr), and FUTURE (5-10yr) horizons."
    }

    # ── NOW: two clickable sub-phases ───────────────────────────────
    now_subphases = []
    for subphase in ["0-6 months", "6-24 months"]:
        try:
            raw = generate_response(build_subphase_prompt(product, "NOW", subphase))
            now_subphases.append(parse_json_response(raw))
        except Exception as e:
            print(f"Error NOW {subphase}: {e}")
            now_subphases.append(error_subphase(subphase, str(e)))

    blueprint["now"] = {
        "sub_phases": ["0-6 months", "6-24 months"],
        "subphase_data": now_subphases
    }

    # ── NEXT: two clickable sub-phases ──────────────────────────────
    next_subphases = []
    for subphase in ["1-2 years", "2-5 years"]:
        try:
            raw = generate_response(build_subphase_prompt(product, "NEXT", subphase))
            next_subphases.append(parse_json_response(raw))
        except Exception as e:
            print(f"Error NEXT {subphase}: {e}")
            next_subphases.append(error_subphase(subphase, str(e)))

    blueprint["next"] = {
        "sub_phases": ["1-2 years", "2-5 years"],
        "subphase_data": next_subphases
    }

    # ── FUTURE: one sub-phase ───────────────────────────────────────
    try:
        raw = generate_response(build_subphase_prompt(product, "FUTURE", "5-10 years"))
        blueprint["future"] = {
            "sub_phases": ["5-10 years"],
            "subphase_data": [parse_json_response(raw)]
        }
    except Exception as e:
        print(f"Error FUTURE: {e}")
        blueprint["future"] = {
            "sub_phases": ["5-10 years"],
            "subphase_data": [error_subphase("5-10 years", str(e))]
        }

    return {"success": True, "blueprint": blueprint}
