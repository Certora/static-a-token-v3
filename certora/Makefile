default: help

PATCH         = applyHarness.patch
CONTRACTS_DIR = ../src
LIBS_DIR = ../lib
MUNGED_SRC    = munged/src
MUNGED_LIB    = munged/lib

help:
	@echo "usage:"
	@echo "  make clean:  remove all generated files (those ignored by git)"
	@echo "  make $(MUNGED_DIR): create $(MUNGED_DIR) directory by applying the patch file to $(CONTRACTS_DIR)"
	@echo "  make record: record a new patch file capturing the differences between $(CONTRACTS_DIR) and $(MUNGED_DIR)"

<<<<<<< Updated upstream
munged:  $(wildcard $(CONTRACTS_DIR)/*.sol) $(PATCH)
	rm -rf $@
	mkdir $@
	cp -r ../lib $@
	cp -r ../src $@
	patch -p0 -d $@ < $(PATCH)

record:
	mkdir tmp
	cp -r ../lib tmp
	cp -r ../src tmp
	diff -ruN tmp $(MUNGED_DIR) | sed 's+tmp/++g' | sed 's+$(MUNGED_DIR)/++g' > $(PATCH)
	rm -rf tmp
=======
munged:  $(wildcard $(CONTRACTS_DIR)/*.sol) $(wildcard $(LIBS_DIR)/*.sol) $(PATCH)
	rm -rf $@/*
	cp -r $(CONTRACTS_DIR) $(LIBS_DIR) $@
	patch -p0 -d $(MUNGED_SRC) < $(PATCH)
	patch -p0 -d $(MUNGED_LIB) < $(PATCH)

record:
	diff -ruN $(CONTRACTS_DIR) $(MUNGED_SRC) | sed 's+\.\./$(CONTRACTS_DIR)/++g' | sed 's+$(MUNGED_SRC)/++g' > $(PATCH)
	diff -ruN $(LIBS_DIR) $(MUNGED_LIB) | sed 's+\.\./$(LIBS_DIR)/++g' | sed 's+$(MUNGED_LIB)/++g' >> $(PATCH)
>>>>>>> Stashed changes

clean:
	git clean -fdX
	touch $(PATCH)

