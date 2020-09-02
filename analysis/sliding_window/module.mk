MODULE_NAME := analysis/sliding_window
SUBMODULES := 

$(MODULE_NAME)/%: NUM_OF_REPEATS := $(SLIDING_WINDOW_NUM_OF_REPEATS)
$(MODULE_NAME)/%: CONFIGURATION_LIST := \
	$(call array_to_comma_separated,$(SLIDING_WINDOW_CONFIGURATIONS))

include $(COMMON_ANALYSIS_MAKEFILE)

