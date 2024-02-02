# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, doudoudzj
# All rights reserved.
#
# InPanel is distributed under the terms of the New BSD License.
# The full license can be found in 'LICENSE'.

'''Module for Configurations Management.'''

from os.path import exists

from lib.filelock import FileLock

try:
    from ConfigParser import ConfigParser  # python 2.x
except:
    from configparser import ConfigParser


def configurations(inifile=None, configs=None):
    '''the configurations for InPanel'''
    default_configs = {
        'server': {
            'ip': '*',
            'port': '18888',
            'forcehttps': 'off',  # force use https
            'lastcheckupdate': 0,
            'updateinfo': '',
            'sslkey': '/usr/local/inpanel/core/certificate/inpanel.key',
            'sslcrt': '/usr/local/inpanel/core/certificate/inpanel.crt'
        },
        'auth': {
            'username': 'admin',
            'password': '',  # empty password never validated
            'passwordcheck': 'on',
            'accesskey': '',  # empty access key never validated
            'accesskeyenable': 'off',
        },
        'runtime': {
            'mode': '',  # format: demo | dev | prod
            'loginlock': 'off',
            'loginfails': 0,
            'loginlockexpire': 0,
        },
        'file': {
            'lastdir': '/root',
            'lastfile': '',
        },
        'time': {
            'timezone': ''  # format: timezone = Asia/Shanghai
        },
        'ecs': {
            'accounts': ''
        },
        'inpanel': {
            'Instance Name': 'Access key'
        }
    } if configs is None else configs

    return Config('data/config.ini' if inifile is None else inifile, default_configs)

class Config(object):
    def __init__(self, inifile=None, configs=None):
        if inifile is None:
            return None
        self.inifile = inifile
        self.cfg = ConfigParser()

        with FileLock(self.inifile):
            if exists(self.inifile):
                self.cfg.read(self.inifile)

            # initialize configurations
            default_configs = {} if configs is None else configs
            needupdate = False
            for sec, secdata in default_configs.items():
                if not self.cfg.has_section(sec):
                    self.cfg.add_section(sec)
                    needupdate = True
                for opt, val in secdata.items():
                    if not self.cfg.has_option(sec, opt):
                        self.cfg.set(sec, opt, val)
                        needupdate = True

            # update ini file
            if needupdate:
                self.update(False)

    def update(self, lock=True):
        if lock:
            flock = FileLock(self.inifile)
            flock.acquire()

        try:
            inifp = open(self.inifile, 'w')
            self.cfg.write(inifp)
            inifp.close()
            if lock:
                flock.release()
            return True
        except:
            if lock:
                flock.release()
            return False

    def has_option(self, section, option):
        return self.cfg.has_option(section, option)

    def remove_option(self, section, option):
        return self.cfg.remove_option(section, option)

    def get(self, section, option):
        if self.cfg.has_option(section, option):
            return self.cfg.get(section, option)
        else:
            return None

    def getboolean(self, section, option):
        return self.cfg.getboolean(section, option)

    def getint(self, section, option):
        return self.cfg.getint(section, option)

    def has_section(self, section):
        return self.cfg.has_section(section)

    def add_section(self, section):
        return self.cfg.add_section(section)

    def remove_section(self, section=None):
        if section is None:
            return False
        else:
            return self.cfg.remove_section(section)

    def set(self, section, option, value):
        try:
            self.cfg.set(section, option, value)
        except:
            return False
        return self.update()

    def get_section_list(self):
        '''Return a list of section names, excluding [DEFAULT]'''
        return self.cfg.sections()

    def get_option_list(self, section):
        '''Return a list of option names for the given section name.'''
        return self.cfg.options(section)

    def get_config_list(self):
        '''Return a list of all config for the given config file.'''
        config_list = []
        sections = self.cfg.sections()
        for section in sections:
            sec = {'section': section, 'option': {}}
            options = self.cfg.options(section)
            for key in options:
                sec['option'][key] = self.cfg.get(section, key)
            config_list.append(sec)
        return config_list

    def get_config(self):
        '''Return a dict of all config for the given config file.'''
        config = {}
        for section in self.cfg.sections():
            config[section] = {}
            for item in self.cfg.options(section):
                config[section][item] = self.cfg.get(section, item)
        return config

    def addsection(self, section, data):
        '''add one section'''
        try:
            if not self.cfg.has_section(section):
                self.cfg.add_section(section)
            for option, value in data.items():
                self.cfg.set(section, option, value)
            return self.update(False)
        except:
            return False

    def addsections(self, section):
        '''add some sections'''
        try:
            for sec, data in section.items():
                if not self.cfg.has_section(sec):
                    self.cfg.add_section(sec)
                for option, value in data.items():
                    self.cfg.set(sec, option, value)
            return self.update(False)
        except:
            return False

if __name__ == '__main__':
    import json
    default_config = {
        '1.1.1.1': {
            'server': '1.1.1.1',
            'port': 8023,
            'accesskey': 'O64Td9EWEj8THu+RlHuoO8tjJzUmdsx37pTluP+aVc0='
        },
        '1.1.1.2': {
            'server': '1.1.1.1',
            'port': 8023,
            'accesskey': 'O64Td9EWEj8THu+RlHuoO8tjJzUmdsx37pTluP+aVc0='
        }
    }
    config = Config('data/clients.ini', {})
    print(config)
    print(config.get_section_list())
    config.update()
    config.addsection('accccc', {'abc': 2345, 'ccc': 34567654345})
    config.addsections(default_config)
    print(config.get_section_list())
    # print(config.update())
    print('abc')
    config_list = config.get_config_list()
    print(json.dumps(config_list))
    config_dict = config.get_config()
    print(json.dumps(config_dict))
