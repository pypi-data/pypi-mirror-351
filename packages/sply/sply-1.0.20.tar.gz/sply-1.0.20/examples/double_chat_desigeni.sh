#!/bin/sh

sply_path="$(dirname $(realpath "$0"))/.."

export ai1="Geni"
export ai2="Desi"

export ai1_desc_ai1="is a programmer who wants to implement $ai2's designs. If any of $ai2's requests are unclear, $ai1 will ask for details; otherwise, $ai1 will use python, sharing source code for $ai2 to examine in the chat"
export ai2_desc_ai1="$ai1_desc_ai1"

export ai2_desc_ai2="wants to design a single-file pygame (no external assets) with code by $ai1. It will have an original design. $ai2 will be clear and concise with feature requests and when asking or answering follow-up questions"
export ai1_desc_ai2="$ai2_desc_ai2"

[ "$ai2_new_english" ] && {
    export ai1_desc_ai2="$ai1_desc_ai2"". $ai2 is a new English speaker and is self-conscious about it"
    echo "$0: note: using ai2_new_english enhancement"
    }

$sply_path/examples/double_chat_examples.sh

