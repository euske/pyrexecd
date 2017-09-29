##  bash function

# usage:
#   $ open path
#   $ edit path
#   $ print path
#   $ explore path

WINDOWS_HOST=${WINDOWS_HOST:-windows}
BASE_LOCAL=$HOME
BASE_REMOTE=.

rexec_cmd ()
{
    local host;
    local path;
    local cmd;
    if [[ $# -lt 3 ]]; then
	echo "Usage: rexec_cmd hostname @cmd path";
	return 1;
    fi;
    host=$1; shift;
    cmd=$1; shift
    path=$1; shift;
    if [[ $path =~ ^/ ]]; then
	:;
    else
	path=$PWD/${path:-.};
    fi;
    if [[ ! $path =~ ^$BASE_LOCAL ]]; then
	echo "Invalid path: $1";
	return 1;
    fi;
    path=${path#$BASE_LOCAL};
    path=$BASE_REMOTE${path//\//\\};
    echo "Sending: $cmd for $path";
    echo "$path" | command ssh "$host" "$cmd"
}

open() { rexec_cmd "$WINDOWS_HOST" @open "$@"; }
edit() { rexec_cmd "$WINDOWS_HOST" @edit "$@"; }
print() { rexec_cmd "$WINDOWS_HOST" @print "$@"; }
