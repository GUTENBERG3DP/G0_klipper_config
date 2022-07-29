#/bin/bash
# move to script dir
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/src"
# remove old config
rm ~/klipper_config/*.cfg
# copy new over
yes | cp *.cfg ~/klipper_config
echo "Done!"