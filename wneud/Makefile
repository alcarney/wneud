include ../.devcontainer/tools.mk

FLATPAK_EXE ?= wneud
FLATPAK_MANIFEST ?= io.github.swyddfa.Wneud.json
FLATPAK_BUILD_DIR ?= build

SRC_FILES = $(shell find src -type f -name '*.py' -or -name '*.qml')
#$(info src = $(SRC_FILES))

.PHONY: run
run: $(FLATPAK_BUILD_DIR)/files/.ref
	flatpak-builder  --env=QT_QPA_PLATFORM=wayland --run $(FLATPAK_BUILD_DIR) $(FLATPAK_MANIFEST) $(FLATPAK_EXE)

.PHONY: test
test: | $(UV)
	$(UV) run pytest

.PHONY: clean
clean:
	test -d $(FLATPAK_BUILD_DIR) && rm -r $(FLATPAK_BUILD_DIR)
	test -d dist && rm -r dist

$(FLATPAK_BUILD_DIR)/files/.ref: $(FLATPAK_MANIFEST) dist/.ref
	flatpak-builder --force-clean --install-deps-from flathub $(FLATPAK_BUILD_DIR) $<

dist/.ref: $(SRC_FILES) pyproject.toml
	uv build
	touch $@

# e.g. ARGS=varlink make flatpak-pip-generator
flatpak-pip-generator: .venv/bin/flatpak-pip-generator.py
	uv run python $< $(ARGS)

.venv/bin/flatpak-pip-generator.py: .venv/pyvenv.cfg
	wget https://raw.githubusercontent.com/flatpak/flatpak-builder-tools/master/pip/flatpak-pip-generator.py --directory-prefix .venv/bin

.venv/pyvenv.cfg: pyproject.toml
	uv sync
