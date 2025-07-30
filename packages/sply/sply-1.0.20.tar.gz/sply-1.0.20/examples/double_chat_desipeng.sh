#!/bin/sh

sply_path="$(dirname $(realpath "$0"))/.."

export ai1="Peng"
export ai2="Desi"

export ai1_desc_ai1="is a prompt engineer who wants to form $ai2's designs into a programming prompt for an LLM. If any of $ai2's requests are not entirely clear, $ai1 will ask for details; otherwise, $ai1 will use markdown, sharing specs for $ai2 to review in the chat"
export ai2_desc_ai1="$ai1_desc_ai1"

export ai2_desc_ai2="wants to design a single-file pygame (no external assets) with a prompt by $ai1. It will have an original design. $ai2 will try to be clear and concise with feature requests and when asking or answering follow-up questions"
export ai1_desc_ai2="$ai2_desc_ai2"

[ "$ai2_new_english" ] && {
    export ai1_desc_ai2="$ai1_desc_ai2"". $ai2 is a new English speaker and is self-conscious about it"
    echo "$0: note: using ai2_new_english enhancement"
    }

$sply_path/examples/double_chat_examples.sh

