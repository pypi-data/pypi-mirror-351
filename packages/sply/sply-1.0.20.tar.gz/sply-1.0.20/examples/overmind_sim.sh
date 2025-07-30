#!/bin/sh

rev_prompt=$(printf "\n>>> ")

sply_chat_interact.py \
  in_suffix_enabled="False" \
  rev_prompt="$rev_prompt" \
  prompt_file="$(dirname $(realpath $0))/overmind_sim.prompt" \
  seed="$RANDOM" \
  temp="0.8" \
  num_ctx="8_000" \
  "$@"

