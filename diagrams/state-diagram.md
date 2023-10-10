# ADCS State Diagram
```mermaid
stateDiagram
    [*] --> Detumbling

    Safe --> Detumbling
    
    SunPointing -->|color:red| Safe
    Detumbling --> Safe
    TargetTracking --> Safe


    SunPointing --> Detumbling
    TargetTracking --> Detumbling

```