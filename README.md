# Agentic Profile Matching

A local resume-search and candidate-ranking project. A LangGraph workflow
extracts job criteria, searches resumes, ranks candidates, and creates a
first-round report. During one CLI session, follow-up messages can compare
candidates, explain rankings, refine criteria, request deeper analysis, and
produce final hire/no-hire recommendations.

The project provides both a terminal interface and a Streamlit chat interface.

## Features

- Search supported PDF, TXT, and DOCX resumes in `data/resumes/`.
- Find known technology skills using exact term boundaries. For example, a
  search for `Java` does not match `JavaScript` alone.
- Search semantically with ChromaDB when a vector index exists.
- Fall back to local lexical search when the vector index is empty and the
  request is not an exact-skill search.
- Rank up to 10 candidates by default. A request such as `top 3` changes the
  number of candidates shown.
- Keep the latest job criteria and shortlist available for follow-up requests
  until the CLI process exits.
- Compare shortlisted candidates and explain their relative scores.
- Adjust requirements and report ranking changes.
- Generate screening questions from the active job description and criteria.
- Generate evidence-only reports during the initial and second-round screens.
- Generate heuristic hire/no-hire decisions only in the final round.

## Requirements

- Python 3.10 or newer.
- The packages listed in `requirements.txt`.
- An internet connection the first time the Hugging Face embedding model is
  downloaded, if you want to build or query a populated Chroma vector index.

An OpenAI API key is not required by the current CLI workflow. Although
`openai` is in the dependency list, the current matching workflow does not
require an OpenAI API key.

## Setup on Windows

From the project root, create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Or install dependencies and run the CLI without activating the environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Run the application

Start the conversation:

```powershell
.\.venv\Scripts\python.exe main.py
```

Enter an initial job description or search request. Then enter follow-up
requests at the next `You:` prompt. Type `exit` or `quit` to end the session.
The shortlist is held in memory and is not saved when the process exits.

## Run the Streamlit chat interface

From the project root, run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui\streamlit_app.py
```

Open the local URL printed by Streamlit, usually
`http://localhost:8501`. The interface shows chat history, keeps the agent
shortlist in the browser session, and provides a sidebar with the number of
supported resumes, example requests, and a button to start over.

Example conversation:

```text
Find candidates with React and 3+ years experience
Compare the top 3 matches side by side
Why did Ethan rank higher than Leila?
Prioritize Python and raise the minimum to 5 years
Run deep analysis on the top 10
Give a final hire or no hire recommendation
```

Other refinement examples:

```text
Make React preferred
Add Docker as a requirement
Remove Java
Lower the minimum to 2 years
```

Follow-up requests apply to the latest shortlist. To start over with another
job, enter a new search request; this replaces the current shortlist.

## How search and ranking work

`tools/rag_tools.py` reads supported files from `data/resumes/` when a search
runs. For a recognized skill query, it checks resume text directly and returns
all exact skill matches before ranking. This works even if no Chroma index has
been built.

For other queries, search uses the persisted Chroma vector database when it
contains indexed documents. When the database is empty, the search uses a
local lexical fallback. To build a vector database for semantic search, run:

```powershell
.\.venv\Scripts\python.exe resume_rag.py
```

The indexer loads PDF, TXT, and DOCX resumes, splits their contents into
overlapping text chunks, adds basic name/skill/experience metadata, and writes
the embeddings to `vector_db/`. The Hugging Face
`all-MiniLM-L6-v2` model is used for embeddings.

The requirement extractor recognizes a fixed list of technologies from the
job text and looks for numeric experience expressions such as `3+ years`.
Ranking uses the retrieval distance, required-skill matches, preferred-skill
matches, and detected experience. It is a lightweight rule-based score, not a
learned hiring model.

## Screening rounds and reports

1. **Initial screen:** ranks up to 10 candidates by default and reports their
   score, evidence, strengths, gaps, and follow-up suggestions.
2. **Second round:** ask for `deep analysis` to see a more detailed report for
   the shortlisted candidates. Add `top N` to request a different count.
3. **Final recommendation:** ask for a final hire/no-hire recommendation. The
   rule-based decision checks missing required skills and experience, then
   applies a score threshold.

These reports summarize resume text and extracted metadata. The second round
does not call an LLM or independently verify candidate claims. Treat scores
and decisions as decision-support information and have a person review the
resumes and make hiring decisions.

## State-machine diagram

The state machine for message routing and the initial/refinement workflows is
shown in [docs/state-machine.md](./docs/state-machine.md).

## Project structure

```text
.
├── agents/
│   ├── conversation.py     # Identify search, comparison, refinement, and screening requests
│   ├── graph_builder.py    # Connect the LangGraph workflow nodes
│   ├── matching_agent.py   # Workflow nodes and conversation entry point
│   ├── reporting.py        # Search, comparison, and explanation reports
│   ├── screening.py        # Deep analysis and final recommendation reports
│   └── state.py            # Data passed through the graph
├── data/
│   └── resumes/            # Input resumes (PDF, TXT, and DOCX)
├── docs/
│   └── state-machine.md    # Mermaid conversation and workflow diagram
├── tests/
│   ├── test_conversation_flows.py
│   ├── test_matching_agent.py
│   └── test_rag_search.py
├── tools/
│   ├── fs_tools.py         # Read, list, and search resume files
│   ├── matching_tools.py   # Extract criteria, rank, compare, and create questions
│   └── rag_tools.py        # Exact-skill, Chroma, and lexical search
├── ui/
│   └── streamlit_app.py    # Streamlit conversational interface
├── vector_db/              # Local Chroma database created by the indexer
├── main.py                 # Terminal chat entry point
├── requirements.txt
└── resume_rag.py           # Build the Chroma vector index
```

## Tests

Run the test suite from the project root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests cover requirement extraction, conversation flows, round-one
shortlist limits, and Java/Python skill searches across the resume folder.

## Current limitations

- Conversation state is in-memory only and is lost when the CLI exits.
- Skill recognition uses a fixed list in `tools/matching_tools.py` and
  `tools/rag_tools.py`; add a skill to those lists to recognize it explicitly.
- Experience is estimated from resume text and may not reflect overlapping
  roles or career breaks accurately.
- Search and recommendations are rule-based. The Streamlit UI is a chat
  interface to the same local agent; it does not generate decisions with an
  LLM.
- Some LangChain dependencies may emit compatibility warnings on newer Python
  versions; use the project environment and run the tests after dependency
  updates.
