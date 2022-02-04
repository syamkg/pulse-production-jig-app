#!/usr/bin/env bash

set -e
set -u

# Set colors to format output
NORMAL="\e[0m"
GREEN="\e[32m"
YELLOW="\e[33m"
RED="\e[31m"
BLUE="\e[36m"
MAGENTA="\e[35m"

INFO="${GREEN}[INFO]${NORMAL} "
ERROR="${RED}[ERROR]${NORMAL} "

# See what I can do
if [ $(id | grep 'uid=0(root)' | wc -l) -ne "1" ]
then
    echo -e "${ERROR}You are not root "
    exit
fi

# Set temp mout location
temp_base="/tmp/raspios"
boot_mount="${temp_base}/boot"
root_mount="${temp_base}/root"
mkdir -pv ${boot_mount}
mkdir -pv ${root_mount}

# Set download location
downloads="downloads"
mkdir -pv ${downloads}

image_url="https://downloads.raspberrypi.org/raspios_armhf_latest"
image_zip_file="${downloads}/raspios_image.zip"

url_base="https://downloads.raspberrypi.org/raspios_armhf/images/"
version="$( wget -q ${url_base} -O - | awk -F '"' '/raspios_armhf-/ {print $8}' - | sort -nr | head -1 )"
sha_file=$( wget -q ${url_base}/${version} -O - | awk -F '"' '/armhf.zip.sha256/ {print $8}' - )
sha_sum=$( wget -q "${url_base}/${version}/${sha_file}" -O - | awk '{print $1}' )

# Download the latest image, using the  --continue "Continue getting a partially-downloaded file"
wget --continue --show-progress ${image_url} -O ${image_zip_file}

echo -e "${INFO}Checking the SHA-256 of the downloaded image matches \"${sha_sum}\""

if [ $( sha256sum ${image_zip_file} | grep ${sha_sum} | wc -l ) -eq "1" ]
then
    echo -e "${INFO}The SHA-256 matches"
else
    echo -e "${ERROR}The SHA-256 did not match"
    exit 5
fi

# unzip
extracted_image="${downloads}/"$( 7z l ${image_zip_file} | awk '/-raspios-/ {print $NF}' )
echo -e "${INFO}The name of the image is \"${extracted_image}\""

7z x -o${downloads} ${image_zip_file}

if [ ! -e ${extracted_image} ]
then
    echo -e "${ERROR}Can't find the image \"${extracted_image}\""
    exit 6
fi

loop_base=$( losetup --find --show --partscan "${extracted_image}" )
lsblk ${loop_base}

echo -e "${INFO}Mounting the boot disk to: ${boot_mount}"
mount ${loop_base}p1 "${boot_mount}"

echo -e "${INFO}Mounting the root disk to: ${root_mount}"
mount -v ${loop_base}p2 "${root_mount}"

# Changing Boot disk
echo -e "${INFO}Enabling SSH"
touch "${boot_mount}/ssh"

echo -e "${INFO}Unmountinng..."
umount ${boot_mount}
umount ${root_mount}

new_name="${extracted_image%.*}-ssh-enabled.img"
cp -v "${extracted_image}" "${new_name}"

losetup --detach ${loop_base}
lsblk

echo -e "${MAGENTA}"
echo -e "Now you can burn the disk using something like:"
echo -e "      dd bs=4M status=progress if=${new_name} of=/dev/disk0"
echo -e "${NORMAL}"
