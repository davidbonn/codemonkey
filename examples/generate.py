
import argparse
import math
import random
import subprocess

import orjson

from db import DB


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


def grab_code_block(text: str) -> str:
    try:
        where = text.index("```")
        rc = "# " + text[where + 3 :]
        where = rc.index("```")
        rc = rc[:where]

    except ValueError as e:
        rc = None

    return rc


def run_test(args, code: str, failed) -> bool:
    if code is None:
        return False

    if code in failed:
        return False

    with open(args.tester, "w") as f:
        f.write(code)

    rc = subprocess.run(["uv", "run", "test_calc.py"], capture_output=True, check=False)

    if rc.returncode == 0:
        return True
    else:
        print(f"Test failed: {rc.stderr.decode()}")
        failed[code] = True
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logprobs_file", default="./logprobs.json", type=str, help="Path to the logprobs.json file")
    ap.add_argument("--tester", default="calc.py", type=str, help="Path to the test script to run")
    ap.add_argument("--count", default=1, type=int, help="Max number of times to run the test script")
    ap.add_argument("--label", default="test", type=str)
    ap.add_argument("--db", default="db.sqlite3", type=str, help="Path to the database file")
    ap.add_argument("--temperature", default=None, type=float, help="Temperature for sampling")
    ap.add_argument("--verbose", default=False, action="store_true", help="Print debug messages")
    args = ap.parse_args()

    if args.temperature is None:
        args.temperature = random.uniform(0.0, 2.0)

    with open(args.logprobs_file, "rb") as f:
        logprobs_list = orjson.loads(f.read())

    if args.verbose:
        print(f"Temperature: {args.temperature}")
        print(f"Logprobs: {len(logprobs_list)}")
        print(f"Count: {args.count}")
        print(f"Label: {args.label}")

    failed = dict()

    success = False
    db = DB(args.db)
    with db:
        for i in range(args.count):
            if args.verbose:
                print(f"Running test {i+1} of {args.count}")

            rc = generate_text_from_logprobs(logprobs_list, temperature=args.temperature)
            rc = grab_code_block(rc)

            if run_test(args, rc, failed):
                print(f"Test passed at #{i}")
                db.note_success(args.label, rc, args.temperature, i+1, args.count)
                success = True
                break

        if not success:
            if args.verbose:
                print("No successful test runs, logging failure to database.")
            db.note_failure(args.label, args.temperature, args.count)


if __name__ == "__main__":
    main()