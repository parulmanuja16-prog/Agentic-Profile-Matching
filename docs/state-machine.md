# Conversation State Machine

The diagram shows how the terminal and Streamlit chat interfaces route user
messages. A new search enters the LangGraph screening workflow. Follow-up
requests use the saved shortlist until the user starts a new search or ends
the session.

```mermaid
stateDiagram-v2
    [*] --> Ready
    Ready --> ClassifyMessage: user submits a message
    ClassifyMessage --> EndSession: message is exit or quit
    ClassifyMessage --> ParseJob: new job/search request
    ClassifyMessage --> CompareCandidates: compare request
    ClassifyMessage --> ExplainRanking: why/explain request
    ClassifyMessage --> RefineRequirements: criteria update
    ClassifyMessage --> DeepAnalysis: deep analysis / second round
    ClassifyMessage --> FinalRecommendation: final hire/no-hire request

    state "Initial LangGraph screen" as InitialScreen {
        ParseJob --> ExtractRequirements
        ExtractRequirements --> SearchResumes
        SearchResumes --> RankCandidates
        RankCandidates --> GenerateReport
    }

    GenerateReport --> SaveShortlist
    CompareCandidates --> SaveShortlist
    ExplainRanking --> SaveShortlist
    DeepAnalysis --> SaveShortlist
    FinalRecommendation --> SaveShortlist

    state "Refinement LangGraph pass" as RefinementPass {
        UpdateRequirements --> SearchAgain
        SearchAgain --> RerankCandidates
        RerankCandidates --> ExplainChanges
    }
    RefineRequirements --> UpdateRequirements
    ExplainChanges --> SaveShortlist

    SaveShortlist --> Ready: display response and await next message
    EndSession --> [*]
```

Conversation state is held in application memory. The CLI keeps it in a local
variable, while Streamlit keeps it in the current browser session. It is not
persisted between process restarts.
