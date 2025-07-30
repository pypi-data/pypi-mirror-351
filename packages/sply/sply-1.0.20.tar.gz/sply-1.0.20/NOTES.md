# Notes

## Table of Contents

- [Using "sply_chat_interact.py"](#using-sply_chat_interactpy)
- [Tested suitable models](#tested-suitable-models)
- [Unsuitable models](#unsuitable-models)
- [Dealing with incorrect output](#dealing-with-incorrect-output)
- [Misc](#misc)

## Using "sply_chat_interact.py"
  * Run "sply_chat_interact.py --help" for command line options and defaults
  * Enter "/h" at the input prompt ("> ") for help
  * Hit Ctrl-C to interrupt generation and enter input mode

## Tested suitable models
  * trashpanda-org_QwQ-32B-Snowdrop-v0-Q4_0.gguf
    - sha256sum: 5e1679a314e70d35295c210b4a9e3e03869bb8c30e6e11fb434384962fb918e6
    - SPLY-1.0.15
    - model review: fantastic model, very well suited

  * qwen2.5-coder-14b-instruct-q4_0.gguf
    - sha256sum: 561c8955089ad330dff56a40a001eb8bb4e12746354e76d0262bd65ab4640864
    - SPLY-1.0.15
    - model review: great model, very well suited, my reference model for general testing

  * mistralai_Mistral-Small-3.1-24B-Instruct-2503-Q4_0.gguf
    - sha256sum: f9e71cfc59d011d1ff20b8444dcfa9c9fbbdfe9bfb40ebe6ae226be1f7c48d8f
    - SPLY-1.0.16
    - model review: good model, well suited
  
  * Blabbertron-1.2.i1-Q4_0.gguf
    - sha256sum: 18dc24a96e1b5cab6b614e6a4ec497ba1013ad20c33bb616c39d952af8e8ff6f
    - SPLY-1.0.15
    - model review: good model, well suited
  
  * DRT-o1-14B-Q4_0.gguf
    - sha256sum: b3c53bf7c4e958950598cf5cff722db97605c585b402a6a6860b56fadd51c88d
    - SPLY-1.0.15
    - model review: good model, well suited
  
  * google_gemma-3-12b-it-Q4_0.gguf
    - sha256sum: 9a7b70be8727da9fb28523b35946dd42d4fe0f622cce03daa44fccff0775516d
    - SPLY-1.0.15
    - model review: good model, well suited
  
  * Marco-o1-Q4_0.gguf
    - sha256sum: 71fe2bef6ffea98a2e315b865337474c3c99c00564df65b14dd7741bdb1e9daa
    - SPLY-1.0.15
    - model review: good model, well suited
  
  * ibm-granite_granite-3.2-8b-instruct-Q4_0.gguf
    - sha256sum: 9115cddcad150f908b402072dafe860ce41b35e83613bfbdc7c0dce4afb04bc8
    - SPLY-1.0.15
    - model review: decent model, mostly suitable

  * phi-4-abliterated.Q6_K.gguf
    - sha256sum: 5cd97edadf2eb9d884ed3be3c7943b314b7ee35ba352de036c466c8b51e86377
    - SPLY-1.0.17
    - model review: good model, mostly suitable

## Unsuitable models
  * RekaAI_reka-flash-3-Q4_0.gguf
    - sha256sum: 8fa4f55937c4ea0c968e5c9cc3b4770f4f6e080651eb714c28eddc9d2bdec6ca
    - SPLY-1.0.15
    - model review: good model but not well suited due to rambling
  
  * phi-4-Q4_0.gguf
    - sha256sum: 7c3e1b5bfb03bb4b13cf7ff4889676c5ad4ea92049352d8e1ded3f443f9b68c6
    - SPLY-1.0.15
    - model review: not well suited due to high strangeness. consider phi-4-abliterated instead
  
  * SicariusSicariiStuff_Phi-Line_14B-Q4_0.gguf
    - sha256sum: eea06466ab2c7ce9d01498e8741da792d610b632299bb3fcea139669dad02422
    - SPLY-1.0.15
    - model review: not well suited; too random, like its base model
  
  * huihui-ai_Mistral-Small-24B-Instruct-2501-abliterated-Q4_0.gguf
    - sha256sum: 165086808981b1f449c232aff7d2f7c610ef15a665f085a52fe25fcf0c787963
    - SPLY-1.0.15
    - model review: not well suited due to formatting and simulated python errors (unlike the newer 2503 version above)
  
  * NousResearch_DeepHermes-3-Mistral-24B-Preview-Q4_0.gguf
    - sha256sum: 071a8b73091b22edb96f4fe3e4a3cc4c3f9db2ae7ac2e766244917837fedf115
    - SPLY-1.0.15
    - model review: not well suited due to formatting and simulated python errors, like its base model (mistral-small-2501)
  
  * DeepSeek-R1-Distill-Qwen-14B-Q4_0.gguf
    - sha256sum: 906b3382f2680f4ce845459b4a122e904002b075238080307586bcffcde49eef
    - SPLY-1.0.15
    - model review: unsuitable due to rambling and formatting unpredictability
  
## Dealing with incorrect output
  * Try a different model - see the [tested suitable models list](#tested-suitable-models)
  * Modify the prompt to show examples of expected behavior
  * Try a lower temperature value
  * Try an alternate seed number
  * Reuse a working model/prompt/temp/seed combo
  * When all else fails, Ctrl-C + "edit_prompt()" are your friends

## Misc
  * The model lists are in flux; refer to older versions of this document as needed
  * The default prompt editor is "vim -b" - customize with the "editor=" options and parameters
  * "prompt_file=" args always have precedence over "prompt=" args
  * "edit_prompt" currently leaves prompt tempfiles intact (for manual review)
  * "make_prompt" is jailbroken - modify to taste, or provide a custom prompt

