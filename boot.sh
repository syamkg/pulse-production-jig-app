#!/usr/bin/env bash

script_path=$(realpath "$0")
dir_path=$( dirname "${script_path}" )
cd "${dir_path}" || error=1

source app.env

if [ -z "${APP_DIR}" ]; then
  [ -n "${msg}" ] && msg="${msg}\n"
  msg="${msg}APP_DIR is not set!"
  error=1
fi

if [ -z "${TARGET}" ]; then
  [ -n "${msg}" ] && msg="${msg}\n"
  msg="${msg}TARGET is not set!"
  error=1
fi

if [ "${error}" == 1 ]; then
  if [ -z "${msg}" ]; then
    error_msg="Error occurred!"
  else
    error_msg="${msg}"
  fi

  zenity --error \
    --text="${error_msg}" \
    --no-wrap
  exit 1
fi

now=$(date "+%Y-%m-%d %H:%M:%S")
today=$(date "+%Y%m%d")

log_dir="${APP_DIR}"/logs
log_file="${log_dir}/${today}".log

mkdir -p "${log_dir}"

printf "
*********************************************
*  Jig app starting at %s  *
*********************************************\n" "${now}" >> "${log_file}"

(
DISPLAY=:0 "${APP_DIR}"/run.sh python app.py >> "${log_file}" 2>&1 &
echo "20" ; sleep 8
echo "40" ; sleep 8
echo "50" ; sleep 6
echo "60" ; sleep 6
echo "70" ; sleep 4
echo "80" ; sleep 4
echo "90" ; sleep 2
echo "100" ; sleep 2
) |
zenity --progress \
  --title="Pulse Production Jig" \
  --text="Initialising app..." \
  --percentage=0 \
  --width=300 \
  --auto-close \
  --no-cancel

