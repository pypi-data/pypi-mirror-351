prj-dir := $(shell pwd)
src-dir := $(prj-dir)
venv-dir := $(prj-dir)/venv
python-native := python3
python := $(venv-dir)/bin/python
pytest := $(venv-dir)/bin/pytest
pip := $(venv-dir)/bin/pip
pip-compile := $(venv-dir)/bin/pip-compile

define get_site_dir
$(shell $(python) -c "import sysconfig; print(sysconfig.get_path(\"purelib\"))")
endef

prepare-dev: create-env install-build-tools install-dev-deps set-path

prepare-prod: create-env install-build-tools install-prod-deps set-path

create-env:
	$(python-native) -m venv $(venv-dir)

install-build-tools:
	$(pip) install --upgrade pip
	$(pip) install pip-tools

install-dev-deps:
	$(pip-compile) --strip-extras -v
	$(pip) install -e .[test]

install-prod-deps:
	$(pip-compile) --strip-extras -v
	$(pip) install -r requirements.txt

set-path:
	echo $(src-dir) > $(call get_site_dir)/path.pth

run:
	$(python) $(filter-out $@, $(MAKECMDGOALS))

pytest:
	$(pytest) --cov=./two1 --ignore=tests/channels --ignore=tests/bitserv --ignore=tests/blockchain --ignore=tests/wallet/test_two1_wallet.py --ignore=tests/wallet/test_utxo_selectors.py tests/

publish:
	$(python) -m build && venv/bin/twine check dist/* && venv/bin/twine upload -r pypi dist/*

publish-test:
	$(python) -m build && twine check dist/* && twine upload -r pypitest dist/*

clean:
	rm -rf $(venv-dir) 
	rm -rf $(prj-dir)/build $(prj-dir)/dist ${prj-dir}/*.egg-info
	rm -rf $(prj-dir)/two1/__pycache__
	rm -rf $(prj-dir)/tests/__pycache__
	rm -rf $(prj-dir)/.pytest_cache
