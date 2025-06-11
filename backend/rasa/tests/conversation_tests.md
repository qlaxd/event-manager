## Agentic Event Creation Success
* user: "csinálj egy eventet a hétvégi grillezésnek, kelleni fog csevap"
  intent: create_event_unstructured
  entities:
    - event_title: "hétvégi grillezés"
    - event_description: "kelleni fog csevap"
    - event_occurrence_text: "hétvégi"
* slot_was_set:
    - event_title: "hétvégi grillezés"
* slot_was_set:
    - event_description: "kelleni fog csevap"
* slot_was_set:
    - event_occurrence_text: "hétvégi"
* action: action_create_event_from_llm
* slot_was_set:
    - event_title: null
* slot_was_set:
    - event_description: null
* slot_was_set:
    - event_occurrence_text: null

## Agentic Event Creation Without Title
* user: "hozz létre egy eseményt"
  intent: create_event_unstructured
* action: action_create_event_from_llm
* bot: utter_ask_event_title 