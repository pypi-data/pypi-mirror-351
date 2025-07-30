# Reproducing OE builds

This feature is currently a work in progress and might break from time to
time.

For every OE build triggered using tuxsuite, you can re-run the same build locally.

TuxOE is using [TuxBake](https://gitlab.com/Linaro/tuxbake) for building OE
on both cloud or local host. In order to use the exact same environments, TuxBake
is leveraging [docker](https://docker.com/) with custom container images.

## Setting up

### Host dependencies

Install `docker` and `python`:

```shell
sudo apt install docker.io
sudo apt install python3 python3-pip
```

### TuxBake

Install TuxBake from PyPi: [PyPi](https://pypi.org/project/tuxbake/):

```shell
python3 -m pip install --upgrade tuxbake
```

## Reproducing

To reproduce
[2OupdAGYCmVM7AaaScR60RN02m7](https://tuxapi.tuxsuite.com/v1/groups/demo/projects/demo/oebuilds/2OupdAGYCmVM7AaaScR60RN02m7),
download
[pinned-manifest.xml](https://storage.tuxsuite.com/public/demo/demo/oebuilds/2OupdAGYCmVM7AaaScR60RN02m7/pinned-manifest.xml)
and
[build-definition.json](https://storage.tuxsuite.com/public/demo/demo/oebuilds/2OupdAGYCmVM7AaaScR60RN02m7/build-definition.json).

```shell
wget https://storage.tuxsuite.com/public/demo/demo/oebuilds/2OupdAGYCmVM7AaaScR60RN02m7/build-definition.json
wget https://storage.tuxsuite.com/public/demo/demo/oebuilds/2OupdAGYCmVM7AaaScR60RN02m7/pinned-manifest.xml
tuxbake --build-definition build-definition.json --pinned-manifest pinned-manifest.xml

```