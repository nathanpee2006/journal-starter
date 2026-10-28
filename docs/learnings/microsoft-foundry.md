10/28/2026

# What did I do?

I was able to make AI do sentiment analysis on journal entry texts with **Microsoft Foundry** as the provider. Microsoft Foundry provides access to models through Azure, which hosts the models.

# What worked?

I got the OpenAI API calls to work, which performed sentiment analysis on journal entries. This involved comparing different models namely `gpt-5-mini` and `gpt-5.4-nano`. Chose `gpt-5.4-nano` as it did not use reasoning tokens unlike gpt-5-mini, which meant that I pay less. Essentially, the more input/output tokens that were being used the more money I am spending for the API calls. I also validated OpenAI response before returning it to client.

# What I struggled with, and how did I solve it?

Originally, I was getting 400 Bad Request responses whenever I tried to make an API call to the `OPENAI_BASE_URL` endpoint. A 400 status code signifies that the request body is in the incorrect format. So I got Claude to help me figure out what was wrong with my request body, and it turned out that the analysis schema dictionary is incorrect.

Wrong
```python
analysis_schema = {
    "name": "analysis_response",
    "schema": {
        "type": "object",
        "properties": {
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral"],
            },
            "summary": {"type": "string"},
            "topics": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["sentiment", "summary", "topics"],
        "additionalProperties": False,
    },
}
```


Correct
```python
analysis_schema = {
    "type": "object",
    "properties": {
        "sentiment": {
            "type": "string",
            "enum": ["positive", "negative", "neutral"],
        },
        "summary": {"type": "string"},
        "topics": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["sentiment", "summary", "topics"],
    "additionalProperties": False,
}
```

_Useful notes:_

model_validate() : Dict/JSON/Object → Model

model_dump() : Model → Dict/JSON