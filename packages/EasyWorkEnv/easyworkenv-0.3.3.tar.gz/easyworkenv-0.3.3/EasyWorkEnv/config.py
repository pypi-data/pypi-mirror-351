import json
import re
import yaml
import os
import inspect
class DynamyqueObject:
    def __init__(self):
        pass
class Config:

    def __init__(self,fileName):
        callerFrame = inspect.stack()[1]
        callerFile = callerFrame.filename
        self.__base_dir = os.path.dirname(os.path.abspath(callerFile))
        self.__fileName = fileName
        self.__filePath = os.path.join(self.__base_dir,self.__fileName)
        self.__extensions = self.__findGoodExtensions()

        match self.__extensions :
            case "json":
                self.__data = self.__getEnvData()
            case "env" :
                self.__data = self.__getEnvFromDotEnv()
            case "yaml":
                self.__data = self.__getEnvData()
            case _ :
                self.__data = {}
        self.__setAttribute(self, self.__data)

    def __setAttribute(self,obj, data):
        for key, value in data.items():
            if isinstance(value, dict):
                sub_object = DynamyqueObject()
                setattr(obj, key, sub_object)
                self.__setAttribute(sub_object, value)
            else:
                setattr(obj, key, value)

    def __getEnvData(self):
        with open(self.__filePath, 'r') as f:
            if self.__extensions == "json":
                return json.loads(f.read())
            elif self.__extensions == "yaml":
                return yaml.safe_load(f)



    def __findGoodExtensions(self):
        extensions = re.findall(r"\.[a-zA-Z]+$", self.__fileName)[0].split(".")[1]
        match extensions:
            case "env":
                return "env"
            case "json":
                return "json"
            case "yaml":
                return "yaml"
            case _:
                return False

    def __getEnvFromDotEnv(self):
        dico = {}
        with open(self.__filePath, "r") as f:
            data = f.readlines()
            cleanData = [line.replace("\n", "") for line in data]
            for line in cleanData:
                if re.match(r"^\s*#", line):
                    continue
                match = re.match(r"^\.?([a-zA-Z0-9_.-]+)=(.+)$", line)
                if match:
                    dico[match.group(1)] = match.group(2)
        return dico