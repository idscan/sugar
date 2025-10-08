#!/bin/bash -e

set -x

app=
device="IPhone 16"
stderr_file=
stdout_file=
while getopts a:d:e:o: name
do
   case $name in
   a)    app="$OPTARG";;
   d)    device="$OPTARG";;
   e)    stderr_file="$OPTARG";;
   o)    stdout_file="$OPTARG";;
   ?)   printf "Usage: %s: -a application_path [-d device] [-d stderr_file] [-o stdout_file]\n" $0
         exit 2;;
   esac
done
if [ -z "$app" ]; then
   printf "Option -a is required\n"
fi
if [ ! -z "$stderr_file" ]; then
   echo -n > $stderr_file
fi
if [ ! -z "$stderr_file" ]; then
   echo -n > $stderr_file
fi

xcrun simctl boot "${device}"
xcrun simctl install "${device}" "${app}"
xcrun simctl launch --console "${device}" ${POLLY_IOS_BUNDLE_IDENTIFIER} ${stdout_file:+> ${stdout_file}} ${stderr_file:+2> ${stderr_file}}
