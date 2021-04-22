import json
import sys
import math

def main():
    # Parse provided spec into a dict
    spec = json.loads(sys.stdin.read())
    evaluate(spec)

def evaluate(spec):
    try:
        sys.stderr.write("--> DEBUG - evaluate")
        sys.stderr.write(json.dumps(spec))

        # Build JSON dict with targetReplicas
        evaluation = {}
        evaluation["targetReplicas"] = 1

        # Output JSON to stdout
        sys.stdout.write(json.dumps(evaluation))
    except ValueError as err:
        # If not an integer, output error
        sys.stderr.write(f"Invalid metric value: {err}")
        exit(1)

if __name__ == "__main__":
    main()
