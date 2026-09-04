

import argparse
import os

import ollama
import orjson


def instructions():
    with open("instructions.md", "r") as f:
        return f.read()

def query():
    client = ollama.Client(host="http://goode:11434",)
    response = client.chat(
        model="qwen2.5-coder:14b",
        messages=[dict(role="user", content=instructions(),)],
        logprobs=True,
        top_logprobs=20,
    )

    if "logprobs" in response:
        raw_logprobs = response.get("logprobs", [])

        serializable_logprobs = []
        for item in raw_logprobs:
            # Safely convert custom objects or Pydantic models to regular dicts
            if hasattr(item, "model_dump"):
                item_dict = item.model_dump()
            elif hasattr(item, "__dict__"):
                item_dict = item.__dict__
            else:
                item_dict = dict(item)

            serializable_logprobs.append(item_dict)

        # 3. Save to a JSON file using standard library json
        return orjson.dumps(serializable_logprobs, option=orjson.OPT_INDENT_2)
    else:
        raise RuntimeError("No logprobs in response")


def main():
    rc = query()

    with open("logprobs.json", "wb") as f:
        f.write(rc)


if __name__ == "__main__":
    main()
