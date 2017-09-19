##  bash function

# setup:
#   WINDOWS_HOSTNAME
#   BASE_LOCAL
#   BASE_REMOTE

# usage:
#   $ open path

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
    a=$BASE_REMOTE${a#$BASE_LOCAL};
    a=${a//\//\\};
    echo "opening: $a";
    command ssh "$WINDOWS_HOSTNAME" "@explorer $a"
}
