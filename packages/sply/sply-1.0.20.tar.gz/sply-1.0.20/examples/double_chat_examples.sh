#!/bin/sh

sply_path="$(dirname $(realpath "$0"))/.."
ai1_default="AI_1"
ai1_desc_ai1_default="is an LLM"
ai2_default="AI_2"
ai1_desc_ai2_default="is a different LLM",
ai2_desc_ai1_default="$ai1_desc_ai1_default"
ai2_desc_ai2_default="$ai1_desc_ai2_default"
ai1_temp_default=0.7
ai2_temp_default=0.7
ai1_port_default=8080
ai2_port_default=8081
ai1_num_ctx_default=16384
ai2_num_ctx_default=16384


[ "$ai1" ] || {
    ai1="$ai1_default"
    echo "$0: note: using default ai1 \"$ai1_default\""
    }

[ "$ai2" ] || {
    ai2="$ai2_default"
    echo "$0: note: using default ai2 \"$ai2_default\""
    }

[ "$ai1_desc_ai1" ] || {
    ai1_desc_ai1="$ai1_desc_ai1_default"
    echo "$0: note: using default ai1_desc \"$ai1_desc_ai1_default\""
    }

[ "$ai1_desc_ai2" ] || {
    ai1_desc_ai2="$ai1_desc_ai2_default"
    echo "$0: note: using default ai2_desc \"$ai1_desc_ai2_default\""
    }

[ "$ai2_desc_ai1" ] || {
    ai2_desc_ai1="$ai2_desc_ai1_default"
    echo "$0: note: using default ai1_desc \"$ai2_desc_ai1_default\""
    }

[ "$ai2_desc_ai2" ] || {
    ai2_desc_ai2="$ai2_desc_ai2_default"
    echo "$0: note: using default ai2_desc \"$ai2_desc_ai2_default\""
    }

[ "$ai1_temp" ] || {
    ai1_temp="$ai1_temp_default"
    echo "$0: note: using default ai1_temp \"$ai1_temp_default\""
    }

[ "$ai2_temp" ] || {
    ai2_temp="$ai2_temp_default"
    echo "$0: note: using default ai2_temp \"$ai2_temp_default\""
    }

[ "$ai1_port" ] || {
    ai1_port="$ai1_port_default"
    echo "$0: note: using default ai1_port \"$ai1_port_default\""
    }

[ "$ai2_port" ] || {
    ai2_port="$ai2_port_default"
    echo "$0: note: using default ai2_port \"$ai2_port_default\""
    }

[ "$ai1_num_ctx" ] || {
    ai1_num_ctx="$ai1_num_ctx_default"
    echo "$0: note: using default ai1_num_ctx \"$ai1_num_ctx_default\""
    }

[ "$ai2_num_ctx" ] || {
    ai2_num_ctx="$ai2_num_ctx_default"
    echo "$0: note: using default ai2_num_ctx \"$ai2_num_ctx_default\""
    }
    

PYTHONPATH="$sply_path" \
  $sply_path/bin/sply_double_chat.py \
    c1_backend="llama-server" \
    c1_model_id="" \
    c1_hostname="localhost" \
    c1_port="$ai1_port" \
    c1_user_name="$ai2" \
    c1_user_desc="$ai1_desc_ai2" \
    c1_ai_name="$ai1" \
    c1_ai_desc="$ai1_desc_ai1" \
    c1_in_suffix="$ai1:" \
    c1_in_suffix_enabled="False" \
    c1_rev_prompt="$ai2:" \
    c1_temp="$ai1_temp" \
    c1_num_ctx="$ai1_num_ctx" \
    c2_backend="llama-server" \
    c2_model_id="" \
    c2_hostname="localhost" \
    c2_port="$ai2_port" \
    c2_user_name="$ai1" \
    c2_user_desc="$ai2_desc_ai1" \
    c2_ai_name="$ai2" \
    c2_ai_desc="$ai2_desc_ai2" \
    c2_in_suffix="$ai2:" \
    c2_in_suffix_enabled="False" \
    c2_rev_prompt="$ai1:" \
    c2_temp="$ai2_temp" \
    c2_num_ctx="$ai1_num_ctx" \
    "$@"

