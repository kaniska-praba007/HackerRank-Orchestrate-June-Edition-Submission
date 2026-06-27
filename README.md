Here's a polished, submission-ready README optimized for a HackerRank review. It keeps the technical depth while making the architecture and engineering decisions immediately visible.

# 🚗💻📦 Multi-Modal Evidence Review System

An AI-powered claim verification system that determines whether submitted image evidence **supports**, **contradicts**, or provides **insufficient information** to evaluate insurance and damage claims involving:

- 🚗 Cars
- 💻 Laptops
- 📦 Packages

The system combines **Gemini 2.5 Flash**, **LangGraph**, and deterministic business rules to perform multimodal reasoning over user conversations and submitted images.

---

## ✨ Key Features

- 🧠 **Multi-Agent Architecture** orchestrated using LangGraph
- 👁️ **Multimodal Reasoning** using Gemini Vision
- 📑 **Structured Claim Understanding** with Pydantic schemas
- 🔍 **Deterministic Evidence Validation** based on business rules
- ⚠️ **Risk Detection** from image quality, inconsistencies, and user history
- 🔄 **Retry + Caching** for resilient and cost-efficient LLM calls
- 📊 **Automated Evaluation Pipeline** with report generation
- 🛡️ **Schema-Safe Outputs** ensuring specification compliance

---

## 🏗️ System Architecture

```text
Claims CSV
     │
     ▼
┌────────────────────┐
│ Claim Parser Agent │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Visual Analyzer    │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Evidence Engine    │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Risk Detector      │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Claim Verifier     │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Output Writer      │
└────────────────────┘
```

The entire workflow is orchestrated as a **LangGraph state machine**, where each node consumes and returns strongly typed Pydantic objects.

---

## 🛠️ Tech Stack

| Layer            | Technology       |
| ---------------- | ---------------- |
| Language         | Python 3.10+     |
| LLM / VLM        | Gemini 2.5 Flash |
| Orchestration    | LangGraph        |
| Framework        | LangChain        |
| Validation       | Pydantic v2      |
| Image Processing | Pillow           |
| CLI              | Click + Rich     |
| Reliability      | Tenacity         |
| Caching          | DiskCache        |
| Logging          | Python Logging   |

---

## 📂 Project Structure

```text
code/
├── agents/
│   ├── claim_parser.py
│   ├── visual_analyzer.py
│   ├── evidence_engine.py
│   ├── risk_detector.py
│   ├── verifier.py
│   └── part_matcher.py
│
├── pipeline/
│   ├── orchestrator.py
│   ├── ingestion.py
│   ├── output_writer.py
│   └── state.py
│
├── models/
│   └── schemas.py
│
├── services/
│   ├── retry_llm.py
│   └── cache.py
│
├── utils/
│   └── logging.py
│
├── evaluation/
│   ├── main.py
│   └── report.md
│
├── config.py
└── main.py

dataset/
├── claims.csv
├── sample_claims.csv
├── user_history.csv
├── evidence_requirements.csv
└── images/

output/
README.md
requirements.txt
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone <repo-url>
cd Multi-Modal-Orchestrate
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

> ⚠️ Never commit `.env` files to version control.

### 5. Verify Installation

```bash
python -m code.test_gemini_api
```

Expected output:

```text
✅ Gemini API key works.
```

---

## 🤖 Agents

| Agent                | Responsibility                                             |
| -------------------- | ---------------------------------------------------------- |
| `claim_parser.py`    | Converts conversations into structured claim intents       |
| `visual_analyzer.py` | Detects damage, severity, visible parts, and image quality |
| `evidence_engine.py` | Validates evidence sufficiency using deterministic rules   |
| `risk_detector.py`   | Generates fraud and quality risk signals                   |
| `verifier.py`        | Produces the final claim decision                          |
| `part_matcher.py`    | Performs fuzzy part matching and synonym expansion         |

---

## 🎯 Important Design Decisions

### 1. Hybrid AI + Rule-Based Verification

LLMs are excellent at understanding text and images but less reliable for enforcing strict business rules.

Therefore:

- Gemini handles **claim understanding** and **visual analysis**
- Rule engines handle **evidence sufficiency**
- Final verification combines both approaches

This design improves:

- Reliability
- Explainability
- Consistency
- Reproducibility

---

### 2. Strongly Typed Data Flow

All agents exchange information using **Pydantic models** rather than raw dictionaries.

Benefits:

- Type safety
- Easier debugging
- Schema enforcement
- Reduced runtime failures

---

### 3. Synonym-Aware Part Matching

Users and vision models often describe the same object differently.

Examples:

| User Description | Vision Output |
| ---------------- | ------------- |
| hood             | bonnet        |
| corner           | edge          |
| seal             | tape          |
| side mirror      | wing mirror   |

A shared fuzzy matcher ensures semantic consistency across the entire pipeline.

---

## 🧠 LLM Usage & Optimizations

### Claim Parsing

- Gemini 2.5 Flash with structured outputs
- Enum-constrained prompts
- Automatic fallback on ambiguity

### Visual Analysis

- Multimodal Gemini inference
- Damage classification
- Severity estimation
- Visible part extraction
- Image quality assessment

### Reliability Features

- Tenacity-based exponential retry
- Automatic malformed JSON repair
- Graceful fallbacks on failures
- Optional DiskCache integration

These mechanisms ensure robust execution even under transient API failures.

---

## 🔍 Evidence Evaluation Strategy

The system evaluates claims for:

### 🚗 Cars

- Body panels
- Bumpers
- Glass components
- Mirrors
- Lights

### 💻 Laptops

- Screen
- Keyboard
- Hinges
- Corners
- Body panels

### 📦 Packages

- Exterior damage
- Seals and labels
- Water or stain damage
- Contents visibility

Evidence requirements are loaded dynamically from:

```text
dataset/evidence_requirements.csv
```

This keeps business logic configurable without modifying code.

---

## 🚀 Usage

### Run the Full Pipeline

```bash
python -m code.main run \
  --claims dataset/claims.csv \
  --history dataset/user_history.csv \
  --requirements dataset/evidence_requirements.csv \
  --output output/output.csv
```

### Evaluate Against Ground Truth

```bash
python -m code.main evaluate \
  --claims dataset/sample_claims.csv \
  --history dataset/user_history.csv \
  --requirements dataset/evidence_requirements.csv \
  --output-predictions output/eval_predictions.csv \
  --report evaluation/report.md
```

Add:

```bash
--verbose
```

to display detailed agent logs.

---

## 📄 Example Output

```csv
claim_id,claim_status,evidence_standard_met,risk_flags
C001,supported,true,none
C002,contradicted,false,image_blurry
C003,not_enough_information,true,manual_review_required
```

---

## 📈 Evaluation

The evaluation pipeline compares predictions against labelled claims and reports:

- Claim status accuracy
- Issue type accuracy
- Object part accuracy
- Severity accuracy
- Evidence sufficiency accuracy
- Risk flag accuracy

Detailed reports are automatically generated at:

```text
evaluation/report.md
```

---

## 🔮 Future Improvements

- Multi-model backend support
- Async image processing
- Human-in-the-loop review workflows
- Explainable visual reasoning
- Web dashboard using Streamlit or Gradio
- Database-backed storage
- Additional multilingual support

---

## NOTE

It's better to replace the images in /dataset/images for ensuring relevant output during setup.

## 📄 License

MIT License

This version is concise enough for reviewers to scan quickly while still demonstrating solid architecture and engineering decisions.
