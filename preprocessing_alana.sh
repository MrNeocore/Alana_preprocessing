# Alana data preprocessing bash root script
# Jonathan Meyer
# V1.1

# Note : Using Windows ? ... Just port the sed commands to the equivalent in Python or any other language
# Note 2 : Not the fastest script ever, doing more work at once (Python / sed command) would probably be much faster [no need to load the file several times]
 
if [ $# != 1 ]
then
	printf "Missing argument -> Alana JSON raw file\nExiting\n"
	exit 1
fi

if [ ! -f $1 ]
then
	printf "File '$1' does not exist !\nExiting\n"
	exit 1
fi

pip3 list &>/dev/null | grep pandas /dev/null 2>&1

if [ $? == 0 ]
then
	printf "Python3 'pandas' module not installed - install with 'sudo pip3 install pandas'\nExiting\n"
else
	printf "Processing - please wait... (~0.5-3 minutes)\n"
	python3 preprocessing_alana.py $1 
	
	sed -i '1! s/\({"conv\)/,\n\1/' out.json 
	sed -i 's/\({\"bot\)/\n\t\1/g' out.json
	sed -i 's/\(\"}],\)/\1\n/g' out.json
	
	printf "Done ! See file 'out.json'\n"
	printf "Note : Large file -> Slow to open using a text editor\n"
	printf "Note 2 : Open with pandas.read_json('out.json')\n"
fi