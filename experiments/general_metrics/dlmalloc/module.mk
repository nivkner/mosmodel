MODULE_NAME := experiments/general_metrics/dlmalloc
SUBMODULES := 

include $(ROOT_DIR)/common.mk

include $(GENERAL_METRICS_COMMON_INCLUDE)

$(EXPERIMENT_DIRS): REQUESTED_THP_VALUE := never
$(EXPERIMENT_DIRS): REQUESTED_LARGE_PAGES := 0
$(EXPERIMENT_DIRS): REQUESTED_HUGE_PAGES := 0
$(EXPERIMENT_DIRS): EXPORT_ENVIRONMENT_VARIABLES := \
	export LD_PRELOAD=$(MOSALLOC_TOOL)

$(EXPERIMENT_DIRS): $(MOSALLOC_TOOL)

