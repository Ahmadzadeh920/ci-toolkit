#!/usr/bin/env python3
"""
Compare the `on.workflow_call` contract (inputs/secrets/outputs) of two
versions of a reusable workflow file and report anything that was removed.

A "removal" is a key present in the OLD file's inputs/secrets/outputs that
is absent from the NEW file. A rename shows up as a removal on one side
(the old name disappears) -- this script doesn't try to distinguish a
rename from a genuine removal, because from a caller's point of view both
break existing invocations the same way.

This script never fails on its own -- it always exits 0 and prints a
report. The calling workflow decides whether the report warrants
failing the job.
"""
import argparse
import sys

import yaml


def load_contract(path):
    with open(path) as f:
        doc = yaml.safe_load(f) or {}

    # PyYAML (1.1 resolver) parses a bare `on:` key as boolean True unless
    # it's quoted in the source file, so check both.
    on_block = doc.get("on", doc.get(True, {})) or {}
    if isinstance(on_block, str):
        on_block = {}  # e.g. "on: workflow_call" with no sub-block at all

    wc = on_block.get("workflow_call", {}) or {}
    return {
        "inputs": set((wc.get("inputs") or {}).keys()),
        "secrets": set((wc.get("secrets") or {}).keys()),
        "outputs": set((wc.get("outputs") or {}).keys()),
    }


def normalize(name):
    return name.replace("_", "").replace("-", "").lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True, help="path to the previously released workflow file")
    parser.add_argument("--new", required=True, help="path to the PR's version of the workflow file")
    args = parser.parse_args()

    old = load_contract(args.old)
    new = load_contract(args.new)

    had_removal = False
    for section in ("inputs", "secrets", "outputs"):
        removed = old[section] - new[section]
        added = new[section] - old[section]

        for name in sorted(removed):
            had_removal = True
            candidates = [a for a in added if normalize(a) == normalize(name)]
            if candidates:
                print(f"RENAMED {section}: '{name}' -> possibly '{candidates[0]}'")
            else:
                print(f"REMOVED {section}: '{name}'")

        for name in sorted(added):
            print(f"ADDED {section}: '{name}' (non-breaking)")

    if not had_removal:
        print("OK: no removed or renamed inputs/secrets/outputs vs. the last release.")

    sys.exit(0)


if __name__ == "__main__":
    main()
