#!/bin/bash

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
EXECUTABLE=""
VERBOSE=0
EXECUTE=1


debug () {
	if [[ ${VERBOSE} = 1 ]]
	then
		echo "$1"
	fi
}


while getopts "h?vnf:" opt; do
	case "$opt" in
    h|\?)
		echo "Usage $0 [-v] [-n] [-f file]"
		echo "Options :"
		echo " -v		    Activer le mode verbeux"
		echo " -n       Désactiver l'exécution"
		echo " -f file  Mets 'file' comme exécutable"
		exit 0
		;;
	v) VERBOSE=1
		;;
	n) EXECUTE=0
		;;
	f) EXECUTABLE=$OPTARG
		;;
	esac
done

shift $((OPTIND-1))

[ "${1:-}" = "--" ] && shift


FILES="Main.py printer.py Test.py Sketcher.py"
PROJECT_NAME="Printer"

if [[ -z ${EXECUTE+x} ]]
then
	EXECUTE=1
	debug "Set Execution on"
else
	debug "Execution set to off"
fi

if [[ -z ${EXECUTABLE+x} ]]
then
	EXECUTABLE="Main.py"
	debug "Set executable variable to 'Main.py'"
else
	debug "Executable variable is set to '$EXECUTABLE'"
fi

debug ""
debug "Verbose :	'$VERBOSE'"
debug "Exécution :	'$EXECUTE'"
debug "Exécutable :	'$EXECUTABLE'"
debug ""

echo "Uploading... "

rsync -avh --progress ${FILES} robot@ev3:"/home/robot/$PROJECT_NAME/"

if [[ $? -ne 0 ]]
then
	echo ""
	echo "Error when uploading files !"
	exit 1
fi

echo "Done !"

if [[ ${EXECUTE} = 1 ]]
then
	echo ""
	echo "Executing... "
	ssh robot@ev3 "brickrun -r /home/robot/$PROJECT_NAME/$EXECUTABLE"
fi
