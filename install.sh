#!/bin/bash

# Print help info
function help {
	cat << EOF
$0  [--help|-h] ... print this help
    [--prefix=<prefix>] ... common prefix for installed files [/usr/local]
    [--usrbin-prefix=<prefix for bin files>] ... [$PREFIX/bin]
    [--etc-prefix=<prefix for conf. files>] ... [$PREFIX/etc]
    [--systemd-prefix=<prefix for systemd>] ... [/usr/lib/systemd/system]
EOF
	[[ $# -ne 0 ]] && exit $1
}

# Parse input params
while [[ $# -ne 0 ]]; do
		case "$1" in
			--help|-h)
				help 0
				;;
			--prefix)
				shift
				PREFIX="$1"
				;;
			--prefix=*)
				PREFIX=$(echo "$1" | sed 's/^--prefix=//')
				;;
		    --usrbin-prefix)
				shift
				USRBIN_PREFIX="$1"
				;;
			--usrbin-prefix=*)
				PREFIX=$(echo "$1" | sed 's/^--usrbin-prefix=//')
				;;
			--etc-prefix)
				shift
				ETC_PREFIX="$1"
				;;
			--etc-prefix=*)
				PREFIX=$(echo "$1" | sed 's/^--etc-prefix=//')
				;;
		    --systemd-prefix)
				shift
				SYSTEMD_PREFIX="$1"
				;;
			--systemd-prefix=*)
				PREFIX=$(echo "$1" | sed 's/^--systemd-prefix=//')
				;;
		esac
		shift
done

PREFIX="${PREFIX:-/usr/local}"
USRBIN_PREFIX="${USRBIN_PREFIX:-${PREFIX}/bin}"
ETC_PREFIX="${ETC_PREFIX:-${PREFIX}/etc}"
SYSTEMD_PREFIX="${SYSTEMD_PREFIX:-/usr/lib/systemd/system}"

install --mode=0755 bin/s_termo.py "${USRBIN_PREFIX}"
install --mode=0755 bin/w1_term.py "${USRBIN_PREFIX}"
install --mode=0755 bin/sg_sqlite.py "${USRBIN_PREFIX}"
install --mode=0755 bin/sg_csv.py "${USRBIN_PREFIX}"
install --mode=0755 bin/redis_pubq.py "${USRBIN_PREFIX}"
install --mode=0755 bin/redis_subq.py "${USRBIN_PREFIX}"

install --mode=0644 systemd/s_termo.service "${SYSTEMD_PREFIX}"
