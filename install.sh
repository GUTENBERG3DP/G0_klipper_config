#/bin/bash
# move to script dir
set -e

echo "Pulling new files..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
git pull

# make default config override file
yes | cp "$DIR/template/machine_override.cfg" ~/machine_override.cfg
# launch editor
nano ~/machine_override.cfg

# apply update
python3 "$DIR/installer.py"
echo "Done!"