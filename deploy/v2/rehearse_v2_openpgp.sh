#!/bin/sh
# Disposable cryptographic rehearsal only; never supply operator keys or data.
set -eu
umask 077
test "${CH_V2_OWN_DISPOSABLE_CONTAINER:-}" = 1
test -f /.dockerenv
test "$(ls /sys/class/net)" = lo
test "$(id -u)" = 0
work="$(mktemp -d)"
mkdir "$work/home" "$work/sender"
export GNUPGHOME="$work/home"
gpg_cmd() { gpg --no-options --batch --no-tty "$@"; }
trap 'gpgconf --homedir "$work/home" --kill gpg-agent || true; gpgconf --homedir "$work/sender" --kill gpg-agent || true' EXIT
members='database.dump runtime.json fixture.json'

case "${1:-}" in
seal)
    test ! -e /custody/recovery.gpg
    test ! -e /sealed/SHA256SUMS
    chmod 700 /custody /sealed
    openssl rand -hex 24 > /custody/passphrase.synthetic
    gpg_cmd --pinentry-mode loopback --passphrase-fd 0 --quick-gen-key \
        'CH synthetic recovery <restore@example.invalid>' rsa2048 cert,encr 1d < /custody/passphrase.synthetic
    recipient="$(gpg_cmd --with-colons --fingerprint restore@example.invalid | awk -F: '$1=="fpr"{print $10; exit}')"
    test "${#recipient}" -eq 40
    gpg_cmd --pinentry-mode loopback --passphrase-fd 0 --export-secret-keys "$recipient" \
        < /custody/passphrase.synthetic > /custody/recovery.gpg
    test -s /custody/recovery.gpg
    gpg_cmd --export "$recipient" > "$work/public.gpg"
    export GNUPGHOME="$work/sender"
    gpg_cmd --import "$work/public.gpg"
    test -z "$(gpg_cmd --with-colons --list-secret-keys)"
    for name in $members; do
        test -f "/input/$name"
        gpg_cmd --trust-model always --recipient "$recipient" --output "/sealed/$name.gpg" --encrypt "/input/$name"
    done
    cd /sealed
    sha256sum database.dump.gpg runtime.json.gpg fixture.json.gpg > SHA256SUMS
    printf '%s\n' 'OPENPGP_SEAL=PASS; public-key-only sender'
    ;;
open)
    test ! -e /output/database.dump
    chmod 700 /output
    cd /sealed
    sha256sum --check --strict SHA256SUMS > /dev/null
    if gpg_cmd --decrypt database.dump.gpg > /dev/null 2>&1; then
        exit 1
    fi
    gpg_cmd --pinentry-mode loopback --passphrase-fd 0 --import /custody/recovery.gpg < /custody/passphrase.synthetic
    for name in $members; do
        gpg_cmd --pinentry-mode loopback --passphrase-fd 0 --output "/output/$name" --decrypt "$name.gpg" < /custody/passphrase.synthetic
        test -s "/output/$name"
    done
    printf '%s\n' 'OPENPGP_OPEN=PASS; verified ciphertext recovered in fresh keyring'
    ;;
*) exit 2 ;;
esac
