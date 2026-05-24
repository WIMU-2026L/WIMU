PYTHON ?= python3
MIDILLM_PYTHON ?= $(PYTHON)
MAIN := $(PYTHON) src/main.py
XMIDI_TOOL := $(PYTHON) scripts/xmidi_tool.py

XMIDI_SOURCE ?= data/XMIDI_Dataset
XMIDI_REFERENCE_DIR ?= data/XMIDI_Organized
PROMPT_TEMPLATE ?= data/prompts/prompt_example.txt
PROMPTS_DIR ?= data/prompts
MIDILLM_DIR ?= data/generated/midi-llm
MUSECOCO_DIR ?= data/generated/musecoco
MIDILLM_OUTPUTS ?= 3

.PHONY: help check-submodules check-midillm-submodule check-clamp3-submodule download-data organize-xmidi prepare-prompts merge-prompts generate-midillm eval-fmd eval-fmd-musecoco eval-clamp3-midillm eval-clamp3-musecoco all

help:
	@printf "Available targets:\n"
	@printf "  make check-submodules    Verify that required git submodules are initialized\n"
	@printf "  make check-midillm-submodule Verify that MIDI-LLM submodule is initialized\n"
	@printf "  make check-clamp3-submodule Verify that CLaMP3 submodule is initialized\n"
	@printf "  make download-data        Download and extract the XMIDI dataset\n"
	@printf "  make organize-xmidi       Organize XMIDI files into genre/vibe directories\n"
	@printf "  make prepare-prompts      Generate prompt files from the XMIDI reference tree\n"
	@printf "  make merge-prompts        Merge prompt JSON files into all_prompts.json (legacy flow)\n"
	@printf "  make generate-midillm     Generate MIDI-LLM samples\n"
	@printf "  make eval-fmd             Calculate FMD scores for MIDI-LLM outputs\n"
	@printf "  make eval-fmd-musecoco    Calculate FMD scores for MuseCoco outputs when available\n"
	@printf "  make eval-clamp3-midillm  Run CLaMP3 evaluation for MIDI-LLM outputs\n"
	@printf "  make eval-clamp3-musecoco Run CLaMP3 evaluation for MuseCoco outputs\n"
	@printf "  make all                  Run the default MIDI-LLM workflow end to end\n"

check-submodules:
	@$(MAKE) check-midillm-submodule
	@$(MAKE) check-clamp3-submodule

check-midillm-submodule:
	@test -f external/midi-llm/generate_transformers.py || (printf "Missing external/midi-llm. Run: git submodule update --init --recursive\n" && exit 1)

check-clamp3-submodule:
	@test -f external/clamp3/clamp3_score.py || (printf "Missing external/clamp3. Run: git submodule update --init --recursive\n" && exit 1)

download-data:
	$(MAIN) download-data

organize-xmidi:
	$(MAIN) organize-xmidi --source $(XMIDI_SOURCE) --output $(XMIDI_REFERENCE_DIR)

prepare-prompts: organize-xmidi
	$(XMIDI_TOOL) prompts --template $(PROMPT_TEMPLATE) --out $(PROMPTS_DIR) --cluster-dir $(XMIDI_REFERENCE_DIR) --cluster-type xmidi

merge-prompts: prepare-prompts
	$(XMIDI_TOOL) merge --dir $(PROMPTS_DIR) --cluster-dir $(XMIDI_REFERENCE_DIR) --cluster-type xmidi

generate-midillm: check-midillm-submodule prepare-prompts
	MIDILLM_PYTHON=$(MIDILLM_PYTHON) $(MAIN) generate-midillm --n-outputs $(MIDILLM_OUTPUTS)

eval-fmd:
	$(XMIDI_TOOL) fmd --xmidi $(XMIDI_REFERENCE_DIR) --xmidi-type musecoco --midillm $(MIDILLM_DIR)

eval-fmd-musecoco:
	$(XMIDI_TOOL) fmd --xmidi $(XMIDI_REFERENCE_DIR) --xmidi-type musecoco --musecoco $(MUSECOCO_DIR)

eval-clamp3-midillm: check-clamp3-submodule
	$(MAIN) eval-clamp3 --model midillm --reference-dir $(XMIDI_REFERENCE_DIR)

eval-clamp3-musecoco: check-clamp3-submodule
	$(MAIN) eval-clamp3 --model musecoco --reference-dir $(XMIDI_REFERENCE_DIR)

all: generate-midillm eval-fmd eval-clamp3-midillm
