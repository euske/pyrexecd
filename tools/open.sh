##  bash function

# usage:
#   $ open path

WINDOWS_HOSTNAME=windows
BASE_LOCAL=$HOME
BASE_REMOTE='C:\Users\euske'

open ()
{
    local a;
    if [[ $1 =~ ^/ ]]; then
	a=$1;
    else
	a=$PWD/${1:-.};
    fi;
    if [[ ! $a =~ ^$BASE_LOCAL ]]; then
	echo "invalid path: $1";
	return 1;
    fi;
    a=${a#$BASE_LOCAL};
    a=$BASE_REMOTE${a//\//\\};
    echo "opening: $a";
    echo "$a" | command ssh "$WINDOWS_HOSTNAME" @open
}
