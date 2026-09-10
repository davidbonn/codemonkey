import math
import random

import orjson


def generate_text_from_logprobs(logprobs_list: list, temperature: float = 1.0) -> str:
    """
    Given a list of token logprob dictionaries from Ollama and a temperature,
    samples tokens sequentially and returns the reconstructed text string.
    """
    # Defensive programming for edge cases
    if temperature < 0.0:
        raise ValueError("Temperature must be 0.0 or greater.")

    generated_tokens = []

    for token_slot in logprobs_list:
        # Pull alternative candidate tokens available for this position
        candidates = token_slot.get("top_logprobs", [])

        if not candidates:
            # Fallback to the model's chosen token if top_logprobs array is empty
            generated_tokens.append(token_slot.get("token", ""))
            continue

        # --- Temperature Handling ---

        # 1. Greedy Decoding (Temperature = 0)
        if temperature == 0.0:
            # Pick the candidate with the highest logprob (least negative)
            best_candidate = max(candidates, key=lambda x: x["logprob"])
            generated_tokens.append(best_candidate["token"])
            continue

        # 2. Temperature Scaling (Temperature > 0)
        tokens = [c["token"] for c in candidates]

        # Convert logprob back to standard unnormalized probability: p = e^(logprob)
        # We apply temperature scaling directly to logprobs: scaled_logprob = logprob / temperature
        scaled_probs = []
        for c in candidates:
            try:
                # Divide logprob by temperature before exponentiating
                p_scaled = math.exp(c["logprob"] / temperature)
                scaled_probs.append(p_scaled)
            except OverflowError:
                # Handle extreme values safely
                scaled_probs.append(0.0)

        # Normalize the probabilities so they sum up to 1.0
        total_prob = sum(scaled_probs)
        if total_prob == 0:
            # Fallback if math goes out of bounds
            chosen_token = random.choice(tokens)
        else:
            normalized_probs = [p / total_prob for p in scaled_probs]
            # Weighted random sampling based on scaled probabilities
            chosen_token = random.choices(tokens, weights=normalized_probs, k=1)[0]

        generated_tokens.append(chosen_token)

    # Join tokens into a single cohesive string
    return "".join(generated_tokens)


def main():
    with open("logprobs.json", "rb") as f:
        logprobs_list = orjson.loads(f.read())

    rc = generate_text_from_logprobs(logprobs_list, temperature=1.2)

    try:
        where = rc.index("```")
        rc = "# " + rc[where + 3 :]
        where = rc.index("```")
        rc = rc[:where]

    except ValueError as e:
        rc = "# ERROR: " + str(e) + "\n\n# END OF ERROR"

    print(rc)


if __name__ == "__main__":
    main()