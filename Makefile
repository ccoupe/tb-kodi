# Makefile for restart-node
PRJ=kodi-track
DESTDIR=/usr/local/lib/$(PRJ)
SRCDIR=$(HOME)/Projects/iot/kodi
LAUNCH=$(PRJ).sh
SERVICE=$(PRJ).service
PYENV ?= ${DESTDIR}/kd-env

NODE := $(shell hostname)
SHELL := /bin/bash 

${PYENV}:
	sudo mkdir -p ${PYENV}
	sudo chown ${USER} ${PYENV}
	python3 -m venv ${PYENV}
	( \
	set -e ;\
	source ${PYENV}/bin/activate; \
	pip install -r $(SRCDIR)/requirements.txt; \
	)

setup_launch:
	sudo systemctl enable ${SERVICE}
	sudo systemctl daemon-reload
	sudo systemctl restart ${SERVICE}

setup_dir:
	sudo mkdir -p ${DESTDIR}
	sudo mkdir -p ${DESTDIR}/lib	
	sudo cp -a ${SRCDIR}/Makefile ${DESTDIR}
	sudo cp -a ${SRCDIR}/requirements.txt ${DESTDIR}
	sudo cp -a ${SRCDIR}/${SERVICE} ${DESTDIR}
	sudo chown -R ${USER} ${DESTDIR}
	sed  s!PYENV!${PYENV}! <${SRCDIR}/launch.sh >$(DESTDIR)/$(LAUNCH)
	sudo chmod +x ${DESTDIR}/${LAUNCH}
	sudo cp ${DESTDIR}/${SERVICE} /etc/systemd/system
	
update: 
	cp ${SRCDIR}/tbkodi.py ${DESTDIR}

install: ${PYENV} setup_dir update setup_launch

clean: 
	sudo systemctl stop ${SERVICE}
	sudo systemctl disable ${SERVICE}
	sudo rm -f /etc/systemd/system/${SERVICE}
	sudo rm -rf ${DESTDIR}

realclean: clean
	rm -rf ${PYENV}
