# Vijil Dome 

## Installing the library

You can install ```vijil-dome``` as a library by running the command 

```pip install git+https://github.com/vijilAI/vijil-dome.git@domelibrary```

See the examples folder for usage examples

## Cloning/Syncing the repo

### Clone

`git clone --recurse-submodules git@github.com:vijilAI/vijil-dome.git`

### Sync

`git pull --recurse-submodules`

### Submodule init

`git submodule update --init --recursive`

### Submodule update

`git submodule update --recursive --remote`: --remote: Fetches the latest changes from the remote repository for each submodule.

## Configuration Overview

This README provides detailed information about the configuration file used for setting up a Dome. 

## Running locally:

### Build and run

```
# Set a local API_KEY
$ export API_KEY=test-123
$ make build
```

### Test locally

#### Status check
```
$ curl localhost:80/status
```

#### Add/Update dome config
```
$ curl -XPATCH "localhost:80/config" \
-H "Content-Type: application/json" \
-d '{
  "input-guards": ["prompt-injection", "input-toxicity"],
  "output-guards": ["output-toxicity"],
  "input-early-exit": false,
  "prompt-injection": {
    "type": "security",
    "early-exit": false,
    "methods": ["prompt-injection-deberta-v3-base", "security-llm"],
    "security-llm": {
      "model_name": "gpt-4o"
    }
  },
  "input-toxicity": {
    "type": "moderation",
    "methods": ["moderations-oai-api"]
  },
  "output-toxicity": {
    "type": "moderation",
    "methods": ["moderation-prompt-engineering"]
  }
}'
```

#### Input detections
```
$ curl -XGET "localhost:80/input_detection?api_key=test-123&input_str=hello"
$ curl -XGET "localhost:80/async_input_detection?api_key=test-123&input_str=hello"
```

#### Output detections
```
$ curl -XGET "localhost:80/output_detection?api_key=test-123&output_str=goodbye"
$ curl -XGET "localhost:80/async_output_detection?api_key=test-123&output_str=goodbye"
```

## Table of Contents
1. [General Structure](#general-structure)
2. [Method-Specific Settings](#method-specific-settings)
    - [Security Methods](#1-security-methods)
        - [DeBERTa Prompt-Injection Model](#i-deberta-prompt-injection-model-prompt-injection-deberta-v3-base)
        - [Security Prompt Engineering](#ii-security-prompt-engineering-security-llm)
        - [Length-Per-Perplexity Heuristic](#iii--length-per-perplexity-heuristic-jb-length-per-perplexity)
        - [Prefix-Suffix Perplexity Heuristic](#iv-prefix-suffix-perplexity-heuristic-jb-prefix-suffix-perplexity)
        - [Security Embeddings](#v-security-embeddings-security-embeddings)
    - [Moderation Methods](#2-moderation-methods)
        - [Flashtext Banlist](#i-flashtext-banlist-moderation-flashtext)
        - [Moderation Prompt Engineeering](#iii-moderation-prompt-engineering-moderation-prompt-engineering)
        - [OpenAI Moderation API](#iv-openai-moderations-api-moderations-oai-api)
        - [Perspective API](#v-perspective-api-moderation-perspective-api)
        - [DeBERTa Toxicity Model](#vi-deberta-toxicity-model-moderation-deberta)
    - [Privacy Methods](#3-privacy-methods)
        - [Presidio](#i-presidio-privacy-presidio)
    - [Integrity Methods](#4-integrity-methods)
        - [HHEM](#i-hhem-hhem-hallucination)
        - [Hallucination Prompt Engineering](#ii-hallucination-prompt-engineering-hallucination-llm)
        - [RoBERTa Fact-Check](#iii-roberta-fact-check-model-fact-check-roberta)
        - [Fact-Check Prompt Engineering](#iv-fact-check-prompt-engineering-fact-check-llm)

## General Structure

Dome configurations can be specified via either a dictionary or a TOML file. An example of a TOML configuration is shown below

```toml
[guardrail]
input-guards = ["prompt-injection", "input-toxicity"] 
output-guards = ["output-toxicity"] 
input-early-exit = false

[prompt-injection] 
type="security"
early-exit = false
methods = ["prompt-injection-deberta-v3-base", "security-llm"]

[prompt-injection.security-llm]
model_name = "gpt-4o"

[input-toxicity]
type="moderation"
methods = ["moderations-oai-api"]

[output-toxicity]
type="moderation"
methods = ["moderation-prompt-engineering"]
```

Configurations can also be provided via dictionaries. The same configuration as a dictionary is shown below
```python
example_config = {
            "input-guards": ["prompt-injection", "input-toxicity"],
            "output-guards": ["output-toxicity"],
            "input-early-exit": False,
            "prompt-injection": {
                "type": "security",
                "early-exit":False,
                "methods" : ["prompt-injection-deberta-v3-base", "security-llm"],
                "security-llm": {
                    "model_name": "gpt-4o"
                }
            },
            "input_toxicity":{
                "type":"moderation",
                "methods":["moderations-oai-api"]
            },
            "output_toxicity":{
                "type":"moderation",
                "methods":["moderation-prompt-engineering"]
            },
        }
```

The ```guardrail``` field describes the high level structure of the Dome object. ```guardrail``` has four attributes that must be specified 
- ```input-guards``` - A list of user-defined guard-group names that will be used to scan the input to the LLM
- ```output-guards``` - A list of user-defined guard-group names that will be used to scan the output from the LLM
- ```input-early-exit``` - A boolean value to determine if the input-guards will run in "early-exit" mode, i.e, stop execution as soon as one of the groups has flagged the input. (Default value : true)
- ```output-early-exit``` - A boolean value to determine if the output-guards will run in "early-exit" mode, i.e, stop execution as soon as one of the groups has flagged the output. (Default value : true)
- ```input-run-parallel``` - A boolean value to determine if the input guard-groups will be executed in parallel or not. (Default value : false)
- ```output-run-parallel``` - A boolean value to determine if the output guard-groups will be executed in parallel or not. (Default value : false)

Once the guardrail structure has been specified, the configuration of each guard-group can be specified by creating a new field with the guard-group's name. In the example above, we have three guard-groups  ```prompt-injection```,  ```input-toxicity``` and  ```output-toxicity```. ```prompt-injection``` and  ```input-toxicity``` apply to the input, and ```output-toxicity``` is applied only to the output. 

Each guard-group has three attributes:
- ```type``` - this must be specified, and controls the type of the guard-group. A guard-group's type is the category of guards that it holds. Every guard-group can only be exactly one type. We currently support four types =  ```security```,  ```moderation```,  ```privacy``` and  ```integrity``` (Note: Integrity is a WIP and has not yet been tested)
- ```methods``` - a list that describes which methods are to be used in the guard-group. The methods that can be used depend on the type selected (See model-specific settings for a list of all the methods available for each type of guardgroup). Note that the name in this list **must** match a name of a method exactly. 
- ```early-exit``` - a boolean flag that determines if the methods run in "early-exit" mode, i.e, stop execution as soon as one of the methods has flagged the output. (Default value : true)
- ```run-parallel``` - a boolean flag that determins if the methods run in parallel or sequentially. (Note: if this is enabled, then the value of early-exit is ignored and execution stops as soon as one method flags the query). (Default value: false)


Finally, to customize settings at the method-level, create a new field with the name ```<GROUP-NAME>.<METHOD-NAME>```. In the example above, ```prompt-injection.security-llm``` describes the configuration settings for the ```security-llm``` method of the ```prompt-injection``` guard-group. This configuration scheme lets users create custom settings for different groups and use the same method with different settings in a guardrail. See the next section for detailed instructions on the options available for each method. 


## Method-Specific Settings

This section outlines all the methods currently supported for the various types of guard-groups that can be created. 

### 1. Security Methods
Security guards are guards meant to block against malicious prompts that attempt to cause the LLM to break its intended behaviour and guidelines. We currently support methods that aim to detect prompt injections, and jailbreak attacks. Security methods should typically be used in input guardrails.

#### i. DeBERTa Prompt-Injection Model (```prompt-injection-deberta-v3-base```)
This is a [fine-tuned deberta-v3-base model](https://huggingface.co/protectai/deberta-v3-base-prompt-injection), intended to be a classifier for detecting jailbreaks and prompt injection attacks. It has the following parameters
- ```truncation``` : optional boolean. Determines if the model input should be truncated or not. (Default: true)
- ```max_length``` : optional int. Maximum length of input string. (Default: 512)

#### ii. Security Prompt Engineering (```security-llm```)
A detector that uses custom prompt-engineering to determine if the query string is a prompt-injection or jailbreak attempt. It has the following parameters
- ```hub_name``` : optional str. The hub that hosts the model you want to use. Currently supports OpenAI (```"openai"```), Together (```"together"```) and Octo (```"octo"```). Default value : ```"openai"```
- ```model_name``` : optional str. The model that you want to use. Default: ```"gpt-4-turbo"```. Please ensure that the model you wish to use is compatible with the hub you selected. 
- ```api_key```: optional str. Specify the API key you want to use. By default, this is None, and the API key is pulled directly from the environment variables. The environment variables used are ```OPENAI_API_KEY```, ```OCTO_API_KEY```, and ```TOGETHER_API_KEY```

#### iii.  Length-Per-Perplexity Heuristic (```jb-length-per-perplexity```)
This method uses a hueristic based on perplexity outputs of GPT-2 and the length of a query string to determine if a prompt is a possible jailbreak attack. See [NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/user_guides/guardrails-library.html#jailbreak-detection-heuristics) for additional details. It has the following parameters
- ```stride_length```: optional int. Stride of the LLM. Default value: 512
- ```threshold```: optional float. the threshold of the heuristic. A string with a score higher than the threshold is classified as a jailbreak. Default: 89.79

#### iv. Prefix-Suffix-Perplexity Heuristic (```jb-prefix-suffix-perplexity```)
Similar to the previous method, this method uses a hueristic based on the perplexity of the first and last 20 words of a query. See [NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/user_guides/guardrails-library.html#jailbreak-detection-heuristics) for additional details. It has the following parameters
- ```stride_length```: optional int. Stride of the LLM. Default value: 512
- ```prefix_threshold```: optional float. The threshold for prefix perplexity. Any query string with a prefix threshold higher than this is flagged as a jailbreak attempt. Default: 1845.65
- ```suffix_threshold```: optional float. The threshold for suffix perplexity. Any query string with a suffix threshold higher than this is flagged as a jailbreak attempt. Default: 1845.65
- ```prefix_length```: optional int. The number of words to consider in the prefix. If this is larger than the number of words in the query string, the max length of the query string is used. Default: 20
- ```suffix_length```: optional int. The number of words to consider in the suffix. If this is larger than the number of words in the query string, the max length of the query string is used. Default: 20

#### v. Security Embeddings (```security-embeddings```)
Creates an embeddings index using the garak-in-the-wild-jailbreaks dataset. It has the following parameters:
- ```engine```: optional str. The engine to perform the embeddings. We currently support ```SentenceTransformer``` and ```FastEmbed```. Default: ```SentenceTransformer```
- ```model```: optional str. The embedding model to use. Default: ```all-MiniLM-L6-v2```
- ```threshold```: optional float. The default similarity threshold. If the similarity between a query and its nearest neighbour is greater than or equal to this value, the query is flagged. Default: 0.8
- ```in_mem```: optional bool. Keep the index in memory via a Pandas dataframe (if true) or via Annoy (if False). (Note: Annoy appears to have some instability on Windows environments). Default: true


### 2. Moderation Methods
Moderation methods are aimed to catch content that can be deemed offensive, hurtful, toxic or inappropriate. They also provide support for catching content that might violate other policies such as containing words of phrases that should be banned.  Moderation methods can be used at both the input and output level. 

#### i. Flashtext Banlist (```moderation-flashtext```)
Uses the [Flashtext](https://github.com/vi3k6i5/flashtext) algorithm for fast keyword matching to block any string that contains a phrase or word that is present in a banlist. It has the following parameters
- ```banlist_filepaths```: optional list[str]. A list of paths to text files that contain banned phrases. If not provided, the default banlist (```vijil_core/detectors/configs/banlists/default_banlist.txt```) is used. 

#### ii. Moderation Prompt Engineering (```moderation-prompt-engineering```)
A detector that uses custom prompt-engineering to determine if the query string contains toxicity. It has the following parameters
- ```hub_name``` : optional str. The hub that hosts the model you want to use. Currently supports OpenAI (```"openai"```), Together (```"together"```) and Octo (```"octo"```). Default value : ```"openai"```
- ```model_name``` : optional str. The model that you want to use. Default: ```"gpt-4-turbo"```. Please ensure that the model you wish to use is compatible with the hub you selected. 
- ```api_key```: optional str. Specify the API key you want to use. By default this is not specified and the API key is pulled directly from the environment variables. The environment variables used are ```OPENAI_API_KEY```, ```OCTO_API_KEY```, and ```TOGETHER_API_KEY``` for the corresponding hubs. 

#### iii. OpenAI Moderations API (```moderations-oai-api```)
Uses the latest text-moderation model from OpenAI to classify content for hate, harassment, self-harm, sexual content and violence. It supports the following parameters
- ```score_threshold_dict```: optional dict[str : float]. This dictionary sets the per-category score threshold for each of the different toxicity dimensions. Scores above the threshold will be flagged as toxic. If this is not set, a default value of 0.5 is used for each category. If the dictionary is provided, only the categories in the dictionary are considered. For example, setting this to ```{"violence" : 0.8, "self-harm" : 0.3}``` will cause the method to ignore every category except violence and self-harm, setting their thresholds to 0.8 and 0.3 respectively. For a full list of the categories available, see [here](https://platform.openai.com/docs/guides/moderation/overview).

#### iv. Perspective API (```moderation-perspective-api```)
Uses Google Jigsaw's [Perspective API](https://www.perspectiveapi.com/) to detect toxicity in text. It supports the following parameters
- ```attributes```: optional dict. We do not recommend changing this since it is required by the API. By default, the value is ```{'TOXICITY':{}}```
- ```score_threshold_dict```: optional dict[str: float]. Provide a score threshold for the API. Values that cross the threshold are flagged by the detector. Default: ```{"TOXICITY": 0.5}```. If you wish to change the threshold then change the dictionary accordingly (eg. ```{"TOXICITY": 0.75}``` would set the threshold to 0.75.)

#### v. DeBERTa Toxicity Model (```moderation-deberta```)
Uses a [fine-tuned deberta v3 model](https://huggingface.co/cooperleong00/deberta-v3-large_toxicity-scorer) to detect the presence of toxicity in text. It has the following parameters 
- ```truncation``` : optional boolean. The truncation strategy used by the model. Default:true, 
- ```max_length``` : optional int. Maximum sequence length that can be processed. Default:208
- ```device``` : Optional str. The device to run on ("cuda" or "cpu"). By default uses CUDA if available, else the CPU. 


### 3. Privacy Methods
Privacy methods are aimed to detect and obfuscate the presence of private information and personally identifiable information (PII) in a string. They can be used at both the input and output levels. 

#### i. Presidio (```privacy-presidio```)
Uses [Microsoft's Presidio Data Protection and De-Identification SDK](https://microsoft.github.io/presidio/) to detect the presence of PII in a query string. Depending on the configuration it can be used to just detect PII, or obfuscate it instead. It has the following parameters
- ```score_threshold```: optional float. The threshold for a string to be classified as PII. Default value : 0.5
- ```anonymize```: optional boolean. Determine whether or not anonymization should be enabled. **Important**: if anonymization is enabled, this method will never flag any text. Instead, it will return an anonymized version of the query string with all the PII redacted. Default value: true
- ```allow_list_files```: Optional List[str]. A list of filepaths that contain PII whitelists. Each file should be a text file where every line corresponds to one PII entry that should be ignored. By default, no files are specified in the allow list.

### 4. Integrity Methods
(Note: integrity methods are still currently a WIP and have not yet been thoroughly tested! We still need to think about how to best integrate it into Dome's workflow in a RAG setting. For thoroughnesses; sake, we still document our methods here.)

Integrity methods evaluate query strings based on some available context to check for possible hallucinations and ungrounded or incorrect conclusions. Integrity methods will typically only apply to output guards in RAG-based applications. All integrity models support ```context``` as a parameter where the context for the detector can be initialized. 

#### i. HHEM (```hhem-hallucination```)
Uses the [HHEM Model by Vectara](https://huggingface.co/vectara/hallucination_evaluation_model) to determine if there might be possible model hallucinations. It supports the following parameters
- ```context```: optional str. Set the initial context
- ```factual_consistency_score_threshold``` : optional float. The factual consistency score threshold. **Important** - any input where the factual consistency score is **lower** than the threshold is classified as a possible hallucination. Default value: 0.5

#### ii. Hallucination Prompt Engineering (```hallucination-llm```)
Uses a prompt template outlined in [NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/user_guides/guardrails-library.html#hallucination-detection) to detect hallucinations given a context and hypothesis
- ```context```: optional str. Set the initial context
- ```hub_name``` : optional str. The hub that hosts the model you want to use. Currently supports OpenAI (```"openai"```), Together (```"together"```) and Octo (```"octo"```). Default value : ```"openai"```
- ```model_name``` : optional str. The model that you want to use. Default: ```"gpt-4-turbo"```. Please ensure that the model you wish to use is compatible with the hub you selected. 
- ```api_key```: optional str. Specify the API key you want to use. By default this is not specified and the API key is pulled directly from the environment variables. The environment variables used are ```OPENAI_API_KEY```, ```OCTO_API_KEY```, and ```TOGETHER_API_KEY``` for the corresponding hubs. 

#### iii. RoBERTa fact-Check model (```fact-check-roberta```)
Uses a [fine-tuned Roberta model](https://huggingface.co/Dzeniks/roberta-fact-check) to detect possible factual inconsistencies by examining the joint encoding of a context string and a query string and classifying if the context supports or refutes the claim. It supports the following parameters
- ```context```: optional str. Set the initial context

#### iv. Fact-Check Prompt Engineering (```fact-check-llm```)
Uses a prompt template outlined in [NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/user_guides/guardrails-library.html#fact-checking) to detect if a claim is grounded in some context. It supports the following parameters:
- ```context```: optional str. Set the initial context
- ```hub_name``` : optional str. The hub that hosts the model you want to use. Currently supports OpenAI (```"openai"```), Together (```"together"```) and Octo (```"octo"```). Default value : ```"openai"```
- ```model_name``` : optional str. The model that you want to use. Default: ```"gpt-4-turbo"```. Please ensure that the model you wish to use is compatible with the hub you selected. 
- ```api_key```: optional str. Specify the API key you want to use. By default this is not specified and the API key is pulled directly from the environment variables. The environment variables used are ```OPENAI_API_KEY```, ```OCTO_API_KEY```, and ```TOGETHER_API_KEY``` for the corresponding hubs. 
