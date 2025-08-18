Full langgraph spec
graph TD

A[User Input] --> B[Router Node];

B --> B2{Is it a valid hint request?};

B2 -- No --> D[Respond Directly];

B2 -- Yes --> C{Is this a repeat query?};

C -- Yes --> E[Hint Escalation Path];

C -- No --> F[New Query Path];

E --> G[Find Hint Node Agent];

F --> G;

G --> H[Verify Correctness Node Agent];

H --> I{Is the hint correct?};

I -- Yes --> J[Maintain Character Agent];

I -- No --> K[Generate Error Message];

K -- Retries < Limit --> G;

K -- Retries == Limit --> L[Respond to User];

J --> M[Format Output];

M --> N[Respond to User];

![[Screenshot 2025-08-17 at 8.36.49 PM.png]]

--- 


### MVP: no retry; no progressive hinting
flowchart TD

A["User Input"] --> B["Router Node"]
B -- Is it a valid hint request? --> C{"Hint Request"}
C -- Yes --> E["Find Hint Node Agent"]
C -- No --> D["Respond Directly"]
E --> F["Verify Correctness Node Agent"]
F --> G{"Is the hint correct?"}
G -- Yes --> H["Maintain Character Agent"]
H --> L["Format Output"]
L --> M["Respond to User"]
G -- No --> I["Generate Error Message"]
I -- "Retries == Limit" --> N("Respond to user")

![[Screenshot 2025-08-17 at 8.52.58 PM.png]]
---

### With progressive hinting; no retry loop

graph TD

A[User Input] --> B[Router Node];

B --> B2{Is it a valid hint request?};

B2 -- No --> D[Respond Directly];

B2 -- Yes --> C{Is this a repeat query?};

C -- Yes --> E[Hint Escalation Path];

C -- No --> F[New Query Path];

E --> G[Find Hint Node Agent];

F --> G;

G --> H[Verify Correctness Node Agent];

H --> I{Is the hint correct?};

I -- Yes --> J[Maintain Character Agent];

I -- No --> K[Generate Error Message];

K -- Retries == Limit --> L[Respond to User];

J --> M[Format Output];

M --> N[Respond to User];

![[Screenshot 2025-08-17 at 8.38.51 PM.png]]


---

### With retry loop; without progressive hinting


graph TD

A[User Input] --> B[Router Node];
B -- Is it a valid hint request? --> C{Hint Request};
C -- Yes --> E[Find Hint Node Agent];
C -- No --> D[Respond Directly];
E --> F[Verify Correctness Node Agent];
F --> G{Is the hint correct?};
G -- Yes --> H[Maintain Character Agent];
G -- No --> I[Generate Error Message];
I --> J{Retries == Limit?};
J -- Yes --> K[Respond to User];
J -- No --> E;
H --> L[Format Output];
L --> M[Respond to User];
![[Screenshot 2025-08-17 at 7.57.57 PM.png]]

---

