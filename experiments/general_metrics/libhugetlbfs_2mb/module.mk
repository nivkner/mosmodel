MODULE_NAME := experiments/general_metrics/libhugetlbfs_2mb
SUBMODULES := 

include $(ROOT_DIR)/common.mk

include $(GENERAL_METRICS_LIBHUGETLBFS_COMMON_INCLUDE)

$(EXPERIMENT_DIRS): REQUESTED_LARGE_PAGES := $(LARGE_PAGES_FOOTPRINT)
$(EXPERIMENT_DIRS): REQUESTED_HUGE_PAGES := 0
$(EXPERIMENT_DIRS): HUGETLB_MORECORE := 2mb

$(EXPERIMENT_DIRS): $(LIBHUGETLBFS_LIB)

