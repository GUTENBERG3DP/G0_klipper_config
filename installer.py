#!/usr/bin/python3
# G-ZERO Klipper config installler V0.1b

import configparser
import os
import sys
import logging

LOG_FILE = "/home/pi/klipper-config-installer.log"
LOG_LEVEL = logging.INFO
SRC_FW_DIR = str(os.path.dirname(os.path.realpath(sys.argv[0]))) + "/src"
DEST_FW_DIR = "/home/pi/klipper_config"
OVERRIDE_CONFIG = "/home/pi/machine_override.cfg"
EXCLUDE_LIST = []

logging.basicConfig(level=LOG_LEVEL,  handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()], format="%(asctime)-15s %(levelname)-8s %(message)s")

class ConfigSrc(object):
    fileName = ""
    src = None

    # The class "constructor" - It's actually an initializer 
    def __init__(self, fileName, src):
        self.fileName = fileName
        self.src = src

    def getconfig(self,srcFile):
        self.src.read(srcFile)

def getSavedConfig(configFile):
    savedConfig = []
    try:
        with open(configFile) as configfile:
            lines = configfile.readlines()
            foundSavedConfig = False
            for line in lines:
                if line == "#*# <---------------------- SAVE_CONFIG ---------------------->\n":
                    foundSavedConfig = True
                if foundSavedConfig:
                    savedConfig.append(line)
    except Exception as e:
        logging.warning("Cannot load saved config!")
        return []
    return savedConfig

# remove old config 
def removeOldConfig():
    for localFile in os.listdir(DEST_FW_DIR):  
            if (localFile.endswith(".cfg") or localFile.endswith(".conf")) and localFile not in EXCLUDE_LIST:
                try:
                    logging.info("\tRemove  : " + str(localFile))
                    os.remove(DEST_FW_DIR + "/" + localFile) 
                    logging.info("\tOK")
                except Exception as e:
                    logging.error(str(e))

def getConfigSource():
    srcFileList = []
    for srcFile in os.listdir(SRC_FW_DIR):
        if (srcFile.endswith(".cfg") or  srcFile.endswith(".conf")) and srcFile not in EXCLUDE_LIST:
            srcFileList.append(srcFile)

    configSources = []
    for srcFile in srcFileList:
        try:
            tmpConf = configparser.ConfigParser(delimiters=(':','='))
            tmpConf.read(SRC_FW_DIR + "/" + srcFile)
            logging.debug("\t" + str(tmpConf.sections()))
            if len(tmpConf.sections()) ==0:
                logging.warning(msg)("\tEmpty!")
            else:
                configSrcObj = ConfigSrc(srcFile,tmpConf)
                configSources.append(configSrcObj)
        except Exception as e:
            logging.error("\t" + str(e))
    return configSources

def getOverrideConfig():
    try:
        config = configparser.ConfigParser(delimiters=(':','='))
        config.read(OVERRIDE_CONFIG)
        if len(config.sections()) == 0:
            return None
        return config
    except Exception as e:
        logging.error("\t" + str(e))
        return None

def generateNewConfig(overrideConfig , configSources = []):
    newConfigs = []
    checkedSection = []
    overrideConfigSections = overrideConfig.sections()
    for configObj in configSources:
        configObjSections = configObj.src.sections()
        for configSection in configObjSections:
            # list of checked configs
            checkedSection.append(configSection)
            # override exist config
            if configSection in overrideConfigSections:
                for key in overrideConfig[configSection]:
                    configObj.src[configSection][key] = overrideConfig[configSection][key]
        newConfigs.append(configObj)
    return newConfigs

def writeConfigs(newConfigs,currentSavedConfig,srcSavedConfig):
    for configObj in newConfigs:
        try:
            logging.info("\tWrite config file : " + str(configObj.fileName))
            with open(DEST_FW_DIR + "/" + configObj.fileName, 'w') as configFile:
                configObj.src.write(configFile)
                # if the savedConfig is empty(first install), use the value in source files instead
                if configObj.fileName == "printer.cfg":
                    configFile.write("\n")
                    if len(currentSavedConfig) > 0:
                        configFile.writelines(currentSavedConfig)
                    else:
                        configFile.writelines(srcSavedConfig)
            logging.info("\tOK")
        except Exception as e:
            logging.error(str(e))
    return

def writeDebug(dir,configs):
    for config in configs:
        with open(dir + "/" + config.fileName, 'w') as configfile:
            config.src.write(configfile)

################### main #############################
def main():
    # get current saved config
    logging.info("# Loading saved config...")
    currentSavedConfig = getSavedConfig(DEST_FW_DIR + "/" + "printer.cfg")
    if len(currentSavedConfig) == 0:
        logging.info("\tNo saved config found.")
    else:
        logging.info("\tloaded " + str(len(currentSavedConfig)) + " lines.")
    # get the default saved config from source files,
    # if the above currentSavedConfig is empty srcSavedConfig will be used
    logging.info("# Loading default saved config...")
    srcSavedConfig = getSavedConfig(SRC_FW_DIR + "/" + "printer.cfg")
    if len(srcSavedConfig) == 0:
        logging.info("\tNo default saved config found.")
    else:
        logging.info("\tloaded " + str(len(srcSavedConfig)) + " lines.")
    # get config from source files
    logging.info("# Loading config source files...")
    configSources = getConfigSource()
    if len(configSources) == 0:
        logging.error("\tCannot load config source!")
        os._exit(os.EX_IOERR)
    else:
        logging.info("\tLoaded " + str(len(configSources)) + " files.")
    # get values from machine specified config file. 
    # machine specified values will be used to override the values in configSources
    logging.info("# Loading machine specified config...")
    overrideConfigs = getOverrideConfig()
    if overrideConfigs == None:
        logging.error("\tCannot load machine specified config!")
        os._exit(os.EX_IOERR)
    else:
        logging.info("\tLoaded " + str(len(overrideConfigs.sections())) + " sections.")

    # generate/merge new configs 
    logging.info("# Merging new config(s)...")
    newConfigs = generateNewConfig(overrideConfigs,configSources)
    if len(newConfigs) == 0:
        logging.error("\tCannot generate new config!")
        os._exit(os.EX_IOERR)
    # the number of noew config files should be the same as the config source files
    if len(newConfigs) != len(configSources):
        logging.error("\tConfig length mismatch!")
        os._exit(os.EX_IOERR)
    logging.info("\tOK")

    # remove old and write new merged config
    logging.info("# Delete old config files...")
    removeOldConfig()
    logging.info("# Writing new config files...")
    writeConfigs(newConfigs, currentSavedConfig, srcSavedConfig)

    logging.info("# Firmware update completed!")
    os._exit(os.EX_OK)

if __name__=="__main__":
    main()