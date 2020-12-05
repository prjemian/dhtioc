#!/bin/bash

# publish this package

## Define the release

STARTED=$(date)
PACKAGE=$(python setup.py --name)
RELEASE=$(python setup.py --version)
echo "# ($(date)) PACKAGE: ${PACKAGE}"
echo "# ($(date)) RELEASE: ${RELEASE}"

if [[ ${RELEASE} == *dirty || ${RELEASE} == *+* ]] ; then
  echo "# version: ${RELEASE} not ready to publish"
  exit 1
fi

echo "# ($(date)) - - - - - - - - - - - - - - - - - - - - - - build for PyPI"

## PyPI Build and upload::

echo "# ($(date)) Building for upload to PyPI"
python setup.py sdist bdist_wheel
echo "# ($(date)) Built for PyPI"

echo "# ($(date)) - - - - - - - - - - - - - - - - - - - - - - upload to PyPI"

twine upload "dist/${PACKAGE}-${RELEASE}*"
echo "# ($(date)) Uploaded to PyPI"

echo "# (${STARTED}) started publishing script"
echo "# ($(date)) finished publishing script"
