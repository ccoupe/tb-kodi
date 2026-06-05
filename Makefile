# Makefile for restart-node
PRJ=kodi-track
DESTDIR=/usr/local/lib/$(PRJ)
SRCDIR=$(HOME)/Projects/iot/kodi
LAUNCH=$(PRJ).sh
SERVICE=$(PRJ).service
PYENV ?= ${DESTDIR}/.venv
PYVER ?= 3.11

NODE := $(shell hostname)
SHELL := /bin/bash 

${PYENV}: ${SRCDIR}/requirements.txt
	sudo mkdir -p ${DESTDIR}
	sudo chown ${USER} ${DESTDIR}
	uv venv --python ${PYVER} --no-project ${PYENV}
	( \
	set -e ;\
	source ${PYENV}/bin/activate ; \
	uv pip install -r $(SRCDIR)/requirements.txt ; \
	)

setup_launch:
	sudo systemctl enable ${SERVICE}
	sudo systemctl daemon-reload
	sudo systemctl restart ${SERVICE}

setup_dir:
	sudo mkdir -p ${DESTDIR}
	sudo mkdir -p ${DESTDIR}/lib	
	sudo cp ${SRCDIR}/Makefile ${DESTDIR}
	sudo cp ${SRCDIR}/requirements.txt ${DESTDIR}
	sudo cp ${SRCDIR}/${SERVICE} ${DESTDIR}
	sudo chown -R ${USER} ${DESTDIR}
	sed  s!PYENV!${PYENV}! <${SRCDIR}/launch.sh >$(DESTDIR)/$(LAUNCH)
	sudo chmod +x ${DESTDIR}/${LAUNCH}
	sudo cp ${DESTDIR}/${SERVICE} /etc/systemd/system
	
update: 
	cp ${SRCDIR}/tbkodi.py ${DESTDIR}
	cp ${SRCDIR}/Settings.py ${DESTDIR}
	cp ${SRCDIR}/*.json ${DESTDIR}
	cp ${SRCDIR}/wake_wayland.sh ${DESTDIR}

install: ${PYENV} setup_dir update setup_launch

clean: 
	sudo systemctl stop ${SERVICE}
	sudo systemctl disable ${SERVICE}
	sudo rm -f /etc/systemd/system/${SERVICE}
	sudo rm -rf ${DESTDIR}

realclean: clean
	rm -rf ${PYENV}
