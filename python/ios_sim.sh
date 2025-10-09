#!/bin/bash -e

set -x

app=
device="IPhone 16"
stderr_file=.tmp.stderr
stdout_file=.tmp.stdout
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
   exit 1
fi

# Ensure stdout and stderr are not stale
echo -n > $stdout_file
echo -n > $stderr_file

# If simimulator is running the boot call fails but says it is Booted state
(xcrun simctl boot "${device}" | tee .tmp.boot.out) || fgrep -s "boot device in current state: Booted" .tmp.boot.out
xcrun simctl install "${device}" "${app}"
# Use --console and > redirects, not official --stdout and --stderr. Later don't seem to work.
xcrun simctl launch --console "${device}" ${POLLY_IOS_BUNDLE_IDENTIFIER} 2>"$stderrfile" >"$stdout_file"
echo "reached end"
