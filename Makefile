CC      := gcc
CFLAGS  := -std=c11 -Wall -Wextra -Wpedantic -O2
LDFLAGS := -lm

SRC_DIR := src
BIN_DIR := bin
DATA_DIR := data
FIG_DIR := figures

SAMPLER := $(BIN_DIR)/gaussian_sampler
SAMPLE_DAT := $(DATA_DIR)/sample.dat
HISTOGRAM := $(FIG_DIR)/histogram_vs_pdf.png

N      ?= 5000
MU     ?= 2.5
SIGMA  ?= 3.5
SEED   ?= 42
BINS   ?= 50

.PHONY: all sample plot clean help

all: plot

$(BIN_DIR) $(DATA_DIR) $(FIG_DIR):
	mkdir -p $@

$(SAMPLER): $(SRC_DIR)/main.c $(SRC_DIR)/box_muller.c $(SRC_DIR)/box_muller.h | $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRC_DIR)/main.c $(SRC_DIR)/box_muller.c -o $@ $(LDFLAGS)

sample: $(SAMPLER) | $(DATA_DIR)
	$(SAMPLER) --n $(N) --mu $(MU) --sigma $(SIGMA) --seed $(SEED) --output $(SAMPLE_DAT)

plot: sample | $(FIG_DIR)
	python3 scripts/visualize.py \
		--input $(SAMPLE_DAT) \
		--mu $(MU) \
		--sigma $(SIGMA) \
		--bins $(BINS) \
		--output $(HISTOGRAM)

clean:
	rm -rf $(BIN_DIR) $(DATA_DIR) $(FIG_DIR)

help:
	@echo "Targets:"
	@echo "  make          Build sampler, generate sample, and plot"
	@echo "  make sample   Generate Gaussian sample only"
	@echo "  make plot     Generate sample and histogram figure"
	@echo "  make clean    Remove build artifacts and outputs"
	@echo ""
	@echo "Parameters (override with make VAR=value):"
	@echo "  N=$(N)  MU=$(MU)  SIGMA=$(SIGMA)  SEED=$(SEED)  BINS=$(BINS)"
