#/bin/bash
set -e

echo "Pulling new files..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
git pull

/usr/bin/python3 "$DIR/installer.py"
echo "Done!"