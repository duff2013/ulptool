#!/bin/bash
# set -x

# Define some functions for error handling.  Abort at first error and print the reason.
function die { echo "$@" >&2 ; exit 1 ; }
function try { echo "$1" >&2 ; shift  ; eval $@ | sed -e "s/^/  /" || die "Failed $1" ; }
trap 'echo "Sorry, something failed."' 0
set -e

# Find the existing arduino tools, if any
if [ `uname` = "Darwin" ]
then
    LIBDIR="${HOME}/Library/Arduino15"
else
    LIBDIR="${HOME}/.arduino15"
fi
test -d "${LIBDIR}" || die "Could not find Arduino library directory"
echo "Attempting to install arduino_ulp extensions to ${LIBDIR}"

PKGDIR="${LIBDIR}/packages/esp32"
test -d "${PKGDIR}"|| die "ESP32 board support package not found.  You need to install that first"

COREVERSION=`ls -1t "${PKGDIR}/hardware/esp32" | head -1`
COREDIR="${PKGDIR}/hardware/esp32/${COREVERSION}"
TOOLS_DIR="${COREDIR}/tools"
BINUTILS_DIST=`ls -1t binutils-esp32ulp-*.tar.gz | head -1`
PLATFORM_FILE="${COREDIR}/platform.txt"
PLATFORM_OVERRIDE_FILE="${COREDIR}/platform.local.txt"
ULPSIZE=2048

test -d "${PKGDIR}-orig" || try "Backing up original ESP32 core" rsync -qa "${PKGDIR}/" "${PKGDIR}-orig/"

grep compiler.ulp.path ${PLATFORM_OVERRIDE_FILE} >/dev/null 2>/dev/null || try "Appending to platform.local.txt" cat platform.local.txt >>${PLATFORM_OVERRIDE_FILE}
grep ulp_main.ld ${PLATFORM_FILE} >/dev/null 2>/dev/null || try "Patching platform.local.txt" sed -i .orig -e \"s/-T esp32_out.ld/\\\"-L{build.path}\\/sketch\\/\\\" -T ulp_main.ld -T esp32_out.ld/\" ${PLATFORM_FILE}

try "Installing build scripts" rsync -av tools/ ${TOOLS_DIR}/
try "Setting ULP memory size to ${ULPSIZE}" sed -i .orig -e \"s/CONFIG_ULP_COPROC_RESERVE_MEM.*/CONFIG_ULP_COPROC_RESERVE_MEM ${ULPSIZE}/\" ${TOOLS_DIR}/sdk/include/config/sdkconfig.h
test -f "${BINUTILS_DIST}" || die "ESP32 ULP binutils not found.  Download archive, save it here, then rerun"
test -d "${TOOLS_DIR}/esp32ulp-elf-binutils" || try "Unpacking ${BINUTILS_DIST} to ${TOOLS_DIR}" tar -C "${TOOLS_DIR}" -xf "${BINUTILS_DIST}"
trap 0
echo "You're good to go!"
