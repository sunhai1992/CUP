#!/usr/bin/python
# -*- coding: utf-8 -*
# #############################################################################
#
#  Copyright (c) 2014 Baidu.com,  Inc. All Rights Reserved
#
# #############################################################################
"""
:author:
    Liu.Jia Guannan Ma
:create_date:
    2014
:descrition:
    Complex conf support
"""

import os
import time
import copy
import shutil
from xml.dom import minidom
# import subprocess
import json

import cup

# G_TOOL_PATH = None


class CConf(object):
    """
    Depreciated class. Please do not use it. Use python configparser instead.
    """
    def __init__(self, path, name, revert_version=''):
        self.name = name
        self.path = path
        self.file_abspath = self.path + '/' + self.name
        self.exclude = ['# ', '[']
        self.sep = ':'
        self.bakfile = self.path + '/' + self.name + '.bak.' + revert_version

    def __del__(self):
        if os.path.exists(self.bakfile):
            os.unlink(self.bakfile)

    def _backup(self, new_bakfile):
        shutil.copyfile(self.file_abspath, new_bakfile)

    def __getitem__(self, key):
        with open(self.file_abspath) as src:
            value = ''
            for line in src.readlines():
                if len(line) > 0 and line[0] not in self.exclude:
                    spstrs = line.split(':')
                    k = spstrs[0].strip()
                    if k == key:
                        value = spstrs[1].strip()
        return value

    def __len__(self):
        """
            This function should not be used
        """
        return 0

    def update(self, kvs):
        """
        update conf with a dict.

        dict = {'key' : 'value', 'key1': 'value'}
        """
        self._backup(self.bakfile)
        with open(self.bakfile) as src:
            with open(self.file_abspath, 'w') as trg:
                for line in src.readlines():
                    if len(line) > 0 and line[0] not in self.exclude:
                        splist = line.splistlit(':')
                        k = splist[0].strip()
                        if k in kvs.keys():
                            line = k + ' : ' + kvs[k] + '\n'
                    trg.write(line)

    def revert(self):
        """
        revert the conf
        """
        os.rename(self.bakfile, self.file_abspath)

    def write_kv_into_conf(self, kvkvs):
        """
        将key-value写进conf
        """
        with open(self.file_abspath, 'w+') as fhandle:
            for i in kvkvs.keys:
                fhandle.write('%s:%s\n' % (i, kvkvs[i]))


class CConfModer(object):
    """
    历史遗留类. 请忽略.
    操作我厂configure公共库conf的类。
    主要调用cfmod这个工具进行.
    推荐使用Configure2Dict转换成dict,在使用Dict2Configure类来操作conf文件.
    如果只是简单的更新某个key, 可以使用此类.

    """
    def __init__(self, toolpath):
        if not os.path.exists(toolpath):
            raise IOError(
                'File not found - The cfmod tool cannot be found: %s'
                % toolpath
            )
        self._modtool = toolpath

    def updatekv(self, confpath, key, val):
        """
        update key with value
        """
        cmd = "%s -c %s -u %s:%s " % (self._modtool, confpath, key, val)
        try_times = 0
        while True:
            # ret = subprocess.call(cmd, shell=True)
            ret = cup.shell.ShellExec().run(cmd, 120)
            # print ret
            if(
                ret['returncode'] == 0
                or not ret['returncode']
                or try_times > 1
            ):
                ret['stdout'] = ret['stdout'].decode('gbk')
                ret['stdout'] = ret['stdout'].encode('utf-8')
                # print ret['stdout']
                break
            else:
                try_times += 1
                print 'err:updatekv'
                time.sleep(1)

    def updatekvlist(self, confpath, kvlist):
        """
        更新confpath文件里的内容。 kvlist是一个list.
        list里面每一个item是一个dict { 'key' : 'xxx:xx:xx', 'value' : 'updated'}
        """
        strcmd = ''
        for key_value in kvlist:
            strcmd += ' -u %s:%s ' % (key_value['key'], key_value['value'])
        cmd = "%s  -c %s %s" % (self._modtool, confpath, strcmd)
        try_times = 0
        while True:
            ret = cup.shell.ShellExec().run(cmd, 120)
            if(
                ret['returncode'] == 0
                or not ret['returncode']
                or try_times > 1
            ):
                ret['stdout'] = ret['stdout'].decode('gbk')
                ret['stdout'] = ret['stdout'].encode('utf-8')
                print ret['stdout']
                break
            else:
                try_times += 1
                print 'err:updatekvlist'
                time.sleep(1)

    def addkv(self, confpath, key, val):
        """
        增加某个key/value到confpath
        """
        cmd = "%s -c %s -i %s:%s &>/dev/null" % (
            self._modtool, confpath, key, val
        )
        try_times = 0
        while True:
            ret = cup.shell.ShellExec().run(cmd, 120)
            if(
                ret['returncode'] == 0
                or not ret['returncode']
                or try_times > 1
            ):
                ret['stdout'] = ret['stdout'].decode('gbk')
                ret['stdout'] = ret['stdout'].encode('utf-8')
                print ret['stdout']
                break
            else:
                try_times += 1
                print 'err:addkv'
                time.sleep(1)

            if(ret == 0 or try_times > 1):
                print cmd
                break
            else:
                time.sleep(1)
                try_times += 1

    def delkv(self, confpath, key):
        """
        删除confpath文件中的某个key
        """
        cmd = "%s -c %s -d %s " % (self._modtool, confpath, key)
        try_times = 0
        while True:
            ret = cup.shell.ShellExec().run(cmd, 120)
            if(
                ret['returncode'] == 0
                or not ret['returncode']
                or try_times > 1
            ):
                ret['stdout'] = ret['stdout'].decode('gbk')
                ret['stdout'] = ret['stdout'].encode('utf-8')
                print ret['stdout']
                break
            else:
                try_times += 1
                print 'err:delkv'
                time.sleep(1)

            if(ret == 0 or try_times > 1):
                print cmd
                break
            else:
                time.sleep(1)
                try_times += 1


class ArrayFormatError(cup.err.BaseCupException):
    """
    数组类型错误
    """
    def __init__(self, errmsg):
        super(self.__class__, self).__init__(errmsg)


class LineFormatError(cup.err.BaseCupException):
    """
    Line error class
    """
    def __init__(self, errmsg):
        super(self.__class__, self).__init__(errmsg)


class KeyFormatError(cup.err.BaseCupException):
    """
    Key error class
    """
    def __init__(self, errmsg):
        super(self.__class__, self).__init__(errmsg)


class ValueFormatError(cup.err.BaseCupException):
    """
    value error class
    """
    def __init__(self, errmsg):
        super(self.__class__, self).__init__(errmsg)


class UnknowConfError(cup.err.BaseCupException):
    """
    unkown error class
    """
    def __init__(self, errmsg):
        super(self.__class__, self).__init__(errmsg)


class ConfDictSetItemError(cup.err.BaseCupException):
    """
    ConfDict Error
    """
    def __init__(self, errmsg):
        super(self.__class__, self).__init__(errmsg)


class ConfListSetItemError(cup.err.BaseCupException):
    """
    ConfList Error
    """
    def __init__(self, errmsg):
        super(self.__class__, self).__init__(errmsg)


class ConfList(list):
    """
    增加一个conf的数组属性. 以ConfList的数据方式表现

    e.g.

    @disk: /home/disk1
    @disk: /home/disk2
    """
    def __init__(self):
        super(self.__class__, self).__init__()
        # list.__init__(self, [int(x) for x in itr])
        self._ind = 0
        self._comments = []

    def append_ex(self, item, comments):
        """
        append a item with conf comments
        """
        assert type(comments) == list, 'comments should be a list'
        super(self.__class__, self).append(item)
        self._ind += 1
        self._comments.append(comments)

    def get_ex(self, ind):
        """
        get conf list item with its comments
        """
        try:
            return (self.__getitem__(ind), self._comments[ind])
        except IndexError:
            return (self.__getitem__(ind), [])

    def __delitem__(self, index):
        list.__delitem__(index)
        del self._comments[index]

    def append(self, item):
        self.append_ex(item, [])

    def insert(self, ind, item):
        raise ConfDictSetItemError(
            'Do not support "insert". Use "append" instead'
        )

    def extend(self, seqs):
        raise ConfDictSetItemError(
            'Do not support "extend". Use "append" instead'
        )


class ConfDict(dict):
    """
    ConfDict that Configure2Dict and Dict2Configure can use.
    """
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        self._index = 0
        self._extra_dict = {}
        self._tail = None
        self._reverse_ind = -99999999

    def __delitem__(self, key):
        dict.__delitem__(key)
        del self._extra_dict[key]

    def set_ex(self, key, value, comments):
        """
        In addtion to dict['key'] = value, set_ex also set comments along with
        the key.
        """
        super(self.__class__, self).__setitem__(key, value)
        if key not in self._extra_dict:
            if isinstance(value, list) or isinstance(value, dict):
                self._extra_dict[key] = (self._index, comments)
                self._index += 1
            else:
                self._extra_dict[key] = (self._reverse_ind, comments)
                self._reverse_ind += 1

    def get_ex(self, key):
        """
        get (value, comments) with key, comments is a list
        """
        value = self.get(key)
        comments = self._extra_dict.get(key)
        if comments is None:
            comments = []
        return (value, comments)

    def __setitem__(self, key, value):
        super(self.__class__, self).__setitem__(key, value)
        if key not in self._extra_dict:
            if isinstance(value, list) or isinstance(value, dict):
                self._extra_dict[key] = (self._index, [])
                self._index += 1
            else:
                self._extra_dict[key] = (self._reverse_ind, [])
                self._reverse_ind += 1

    def _compare_keys(self, keyx, keyy):
        if self._extra_dict[keyx][0] == self._extra_dict[keyy][0]:
            return 0
        elif self._extra_dict[keyx][0] < self._extra_dict[keyy][0]:
            return -1
        else:
            return 1

    def get_ordered_keys(self):
        """
        get keys in order
        """
        keys = sorted(self.keys(), self._compare_keys)
        return keys


#  @brief translate configure(public/configure) conf to dict
class Configure2Dict(object):  # pylint: disable=R0903
    """
    Configure2Dict support conf features below:

    1. comments
        As we support access/modify comments in a conf file, you should obey
        rules below:

        Comment closely above the object you want to comment.
        Do NOT comment after the line.

        Otherwise, you might get/set a wrong comment above the object.

    2. sections

        2.1 global section

            - if key:value is not under any [section], it is under the global layer
                by default
            - global section is the 0th layer section

            e.g.
            test.conf:
                # test.conf
                global-key: value
                global-key1: value1

        2.2 child section
            - [section1] means a child section under Global. And it's the
                1st layer section
            - [.section2] means a child section under the nearest section
                above. It's the 2nd layer section.
            - [..section3] means a child section under the nearest section
                above. And the prefix .. means it is the 3rd layer section

            e.g.:
            test.conf:
            ::

                global-key: value
                [section]
                    host:  abc.com
                    port:  8080
                    [.section_child]
                        child_key: child_value
                        [..section_child_child]
                            control: ssh
                            [...section_child_child_child]
                                wow_key:  wow_value

        2.3 section access method
            get_dict method will convert conf into a ConfDict which is derived

            from python dict.

            - Access the section with confdict['section']['section-child'].
            - Access the section with confdict.get_ex('section') with (value,
                comments)


    3. key:value and key:value array

        3.1 key:value
            key:value can be set under Global section which is closely after the
            1st line with no [section] above.

            key:value can also be set under sections.
            ::
                # test.conf
                key1: value1
                [section]
                    key_section: value_in_section
                    [.seciton]
                        key_section_child: value_section_child

        3.2 key:value arrays
            key:value arrays can be access with confdict['section']['disk'].
            You will get a ConfList derived from python list.
        ::

            # test.conf
            # Global layer, key:value
            host: abc.com
            port: 12345
            # 1st layer [monitor]
            @disk: /home/data0
            @disk: /home/data1
            [section]
                @disk: /home/disk/disk1
                @disk: /home/disk/disk2

    4. Example
    ::
        # test.conf
        # Global layer, key:value
        host: abc.com
        port: 12345
        # 1st layer [monitor]
        @disk: /home/data0
        @disk: /home/data1
        [section]
            @disk: /home/disk/disk1
            @disk: /home/disk/disk2

        [monitor]
            timeout: 100
            regex:  sshd
            # 2nd layer that belongs to [monitor]
            [.timeout]
                # key:value in timeout
                max: 100
                # 3rd layer that belongs to [monitor] [timeout]
                [..handler]
                    default: exit
    """

    def __init__(self, configure_file, remove_comments=True, separator=':'):
        """
        @param configure_file:
            configure file path
        @param remove_comments:
            if you comment after key:value # comment, whether we should
            remove it when you access the key
        @raise:
            IOError configure_file not found
            cup.util.conf.KeyFormatError Key format error
            cup.util.conf.ValueFormatError value value
            cup.util.conf.LineFormatError  line format error
            cup.util.conf.ArrayFormatError @array format error
            cup.util.conf.UnknowConfError unknown error
        """
        self._file = configure_file
        if not os.path.exists(configure_file):
            raise IOError('%s does not exists' % configure_file)
        if not os.path.isfile(configure_file):
            raise IOError('%s is not a file' % configure_file)
        self._lines = []
        self._dict = ConfDict()
        self._remove_comments = remove_comments
        self._blank_and_comments = {}
        self._separator = separator

    def _strip_value(self, value):
        if self._remove_comments:
            rev = value.split('#')[0].strip()
        else:
            rev = value
        return rev

    def _handle_key_value_tuple(self, linenum, conf_dict_now, comments):
        num = linenum
        line = self._lines[num]
        key, value = line
        rev_comments = comments
        if not key.startswith('@'):
            conf_dict_now.set_ex(key, value, rev_comments)
            rev_comments = []
        else:
            # @key: value
            # it's a conf array.
            # e.g.
            # @disk : /home/disk1
            # @disk : /home/disk2
            # conf_dict_now[key[1:]] = [value]
            if not key[1:] in conf_dict_now:
                conf_array = ConfList()
                conf_dict_now.set_ex(key[1:], conf_array, rev_comments)
            else:
                conf_array = conf_dict_now[key[1:]]
            conf_array.append_ex(value, [])
            rev_comments = []
            num += 1
            while num < len(self._lines):  # get all items
                if self._handle_comments(rev_comments, self._lines[num]):
                    num += 1
                    continue
                if not type(self._lines[num]) == tuple or \
                        self._lines[num][0] != key:
                    num -= 1
                    break
                conf_dict_now[key[1:]].append_ex(
                    self._lines[num][1], rev_comments
                )
                rev_comments = []
                num += 1
        return (num, rev_comments)

    @classmethod
    def _handle_comments(cls, comments, line):
        if line[0] == '__comments__':
            comments.append(line[1])
            return True
        return False

    @classmethod
    def _handle_group_keys(
        cls, key, conf_dict_now, conf_layer_stack, comments
    ):
        for groupkey in key.split('.'):
            conf_dict_now = conf_layer_stack[-1]
            while isinstance(conf_dict_now, list):
                conf_dict_now = conf_dict_now[-1]
            if groupkey in conf_dict_now:
                conf_dict_now = conf_dict_now[groupkey]
                # push this layer into the stack
                conf_layer_stack.append(conf_dict_now)
            else:
                if groupkey[0] == '@':
                    groupkey = groupkey[1:]
                    if groupkey in conf_dict_now:
                        conf_dict_now[groupkey].append_ex(
                            {}, comments
                        )
                        comments = []
                    else:
                        conflist = ConfList()
                        conf_dict_now.set_ex(
                            groupkey, conflist, comments
                        )
                        comments = []
                        conflist.append(ConfDict())
                else:
                    conf_dict_now.set_ex(
                        groupkey, ConfDict(), comments
                    )
                    comments = []
                conf_layer_stack.append(conf_dict_now[groupkey])
        return comments

    # GLOBAL level 1
    # [groupA] level 2
    #     [.@groupB] level 3
    #         [..@groupC] level 4
    # pylint: disable=R0912, R0915
    def get_dict(self):
        """
        get conf_dict which you can use to access conf info
        """
        comments = []
        self._get_input_lines()
        conf_layer_stack = [self._dict]
        num = 0
        length = len(self._lines)
        last_list_key = None
        while num < length:
            line = self._lines[num]
            if self._handle_comments(comments, line):
                num += 1
                continue
            conf_dict_now = conf_layer_stack[-1]  # conf_dict_now is current
            while isinstance(conf_dict_now, list):  # [], find the working dict
                conf_dict_now = conf_dict_now[-1]
            # line with (key : value)
            # or line with (@key : value)
            if isinstance(line, tuple):  # key value
                num, comments = self._handle_key_value_tuple(
                    num, conf_dict_now, comments
                )
            else:
                key = line.lstrip('.')
                # determine the level of the key
                level = len(line) - len(key) + 2
                if key == 'GLOBAL':
                    # GLOBAL is the 1st level
                    level = 1
                    conf_layer_stack = [self._dict]

                # [Group1.SubGroup1] sub-key: Value
                # if sth below level cannot be computed as len(line) - len(key)
                elif '.' in key:  # conf_layer_stack back to [self._dict]
                    conf_layer_stack = [self._dict]
                    comments = self._handle_group_keys(
                        key, conf_dict_now, conf_layer_stack, comments
                    )
                elif level > len(conf_layer_stack) + 1:
                    raise ArrayFormatError(line)
                elif level == len(conf_layer_stack) + 1:
                    # new grou for
                    if key[0] == '@':
                        key = key[1:]
                        conflist = ConfList()
                        conflist.append(ConfDict())
                        conf_dict_now.set_ex(key, conflist, [])
                    else:
                        conf_dict_now.set_ex(key, ConfDict(), comments)
                        comments = []
                    conf_layer_stack.append(conf_dict_now[key])
                elif level == len(conf_layer_stack):
                    # -1 means the last item. -2 means the second from the end
                    conf_dict_now = conf_layer_stack[-2]   # back one
                    while isinstance(conf_dict_now, list):
                        conf_dict_now = conf_dict_now[-1]
                    if key[0] == '@':
                        tmpkey = key[1:]
                        if tmpkey in conf_dict_now:   # the same group
                            # pylint: disable=E1101
                            # conf_dict_now[tmpkey] = ConfDict()
                            if tmpkey != last_list_key:
                                conf_layer_stack[-1] = conf_dict_now[tmpkey]
                            conf_layer_stack[-1].append_ex(
                                ConfDict(), comments
                            )
                            comments = []
                        else:  # different group
                            conflist = ConfList()
                            conflist.append(ConfDict())
                            conf_dict_now.set_ex(tmpkey, conflist, comments)
                            # conf_dict_now.set_ex(tmpkey, conflist, [])
                            comments = []
                            conf_layer_stack[-1] = conf_dict_now[tmpkey]
                        last_list_key = tmpkey
                    else:
                        conf_dict_now.set_ex(key, ConfDict(), comments)
                        comments = []
                        conf_layer_stack[-1] = conf_dict_now[key]
                elif level < len(conf_layer_stack):
                    conf_dict_now = conf_layer_stack[level - 2]  # get back
                    while isinstance(conf_dict_now, list):
                        conf_dict_now = conf_dict_now[-1]
                    if key[0] == '@':
                        tmpkey = key[1:]
                        if tmpkey in conf_dict_now:  # the same group
                            tmpdict = ConfDict()
                            conf_layer_stack[level - 1].append(tmpdict)
                        else:  # different group
                            # comments
                            conflist = ConfList()
                            conflist.append(ConfDict())
                            conf_dict_now.set_ex(tmpkey, conflist, [])
                            conf_layer_stack[level - 1] = conf_dict_now[tmpkey]
                    else:
                        conf_dict_now.set_ex(key, ConfDict(), comments)
                        comments = []
                        conf_layer_stack[level - 1] = conf_dict_now[key]
                    conf_layer_stack = conf_layer_stack[:level]
                else:
                    raise UnknowConfError('exception occured')
            num += 1
        return self._dict

    # Check the key id format
    def _check_key_valid(self, key):  # pylint: disable=R0201
        if key == '' or key == '@':
            raise KeyFormatError(key)

        if key[0] == '@':
            key = key[1:]
        for char in key:
            if not char.isalnum() and char != '_' \
                    and char != '-' and char != '.':
                raise KeyFormatError(key)

    # Check the [GROUP] key format
    def _check_groupkey_valid(self, key):
        for groupkey in key.split('.'):
            self._check_key_valid(groupkey)

    # Read in the file content, with format check
    def _get_input_lines(self):  # pylint: disable=R0912,R0915
        """
        read conf lines
        """
        try:
            fhanle = open(self._file, 'r')
        except IOError as error:
            cup.log.error('open file failed:%s, err:%s' % (self._file, error))
            raise IOError(str(error))
        for line in fhanle.readlines():
            line = line.strip()
            # if it's a blank line or a line with comments only
            if line == '':
                line = '__comments__:%s' % '\n'
            if line.startswith('#'):
                line = '__comments__:%s\n' % line
            # if it's a section
            if line.startswith('['):
                if not line.endswith(']'):
                    raise LineFormatError('Parse line error, line:\n' + line)
                line = line[1:-1]
                key = line.lstrip('.')
                self._check_groupkey_valid(key)  # check if key is valid
                self._lines.append(line)
                continue
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip(' \t')
            # if remove_comments is True, delete comments in value.

            self._check_key_valid(key)
            if value.startswith('"'):     # if the value is a string
                if not value.endswith('"'):
                    raise ValueFormatError(line)
            else:
                if key != '__comments__':
                    value = self._strip_value(value)
            tmp_value = ''
            # reserve escape in the value string
            escape = False
            for single in value:
                if escape:
                    if single == '0':
                        tmp_value += '\0'
                    elif single == 'n':
                        tmp_value += '\n'
                    elif single == 'r':
                        tmp_value += '\r'
                    elif single == 't':
                        tmp_value += '\t'
                    elif single == 'v':
                        tmp_value += '\v'
                    elif single == 'a':
                        tmp_value += '\a'
                    elif single == 'b':
                        tmp_value += '\b'
                    elif single == 'f':
                        tmp_value += '\f'
                    elif single == "'":
                        tmp_value += "'"
                    elif single == '"':
                        tmp_value += '"'
                    elif single == '\\':
                        tmp_value += '\\'
                    else:
                        # raise ValueFormatError(line)
                        pass
                    escape = False
                elif single == '\\':
                    escape = True
                else:
                    tmp_value += single
            if escape:
                raise ValueFormatError(line)
            value = tmp_value
            self._lines.append((key, value))
        fhanle.close()


class Dict2Configure(object):
    """
    Convert Dict into Configure.
    You can convert a ConfDict or python dict into a conf file.
    """
    ##
    # @param dict the conf dict, make sure the type format is right
    #
    def __init__(self, conf_dict):
        self._dict = None
        self.set_dict(conf_dict)
        self._level = 0
        self._str = ''

    # The separator between a field and its value
    @classmethod
    def _get_field_value_sep(cls):
        return ':'

    # The separator between each line
    @classmethod
    def _get_linesep(cls):
        return '\n'

    # The flag of an array
    @classmethod
    def _get_arrayflag(cls):
        return '@'

    def _get_levelsep(self):
        return '.' * self._level

    def _get_arraylevel_sep(self):
        return '.' * self._level + self._get_arrayflag()

    def _get_indents(self):
        return ' ' * self._level * 4

    def _get_write_string(self):
        self._str = ''
        self._level = 0
        self._get_confstring(self._dict)
        return self._str

    def write_conf(self, conf_file):
        """
        write the conf into of the dict into a conf_file
        """
        with open(conf_file, 'w') as fhandle:
            fhandle.write(self._get_write_string())

    # pylint: disable=R0911
    @classmethod
    def _comp_write_keys(cls, valuex, valuey):
        _py_type = [bool, int, float]

        if type(valuex) == type(valuey):
            return 0

        for py_type in _py_type:
            if isinstance(valuex, py_type):
                return -1

        for py_type in _py_type:
            if isinstance(valuey, str):
                return 1

        if isinstance(valuex, list) and isinstance(valuey, list):
            try:
                if isinstance(valuex[0], dict) or isinstance(valuex[0], list):
                    return 1
                else:
                    return -1
            # pylint: disable=W0703
            except Exception:
                return -1
            else:
                return -1
        # if isinstance(valuex, list) and isinstance(valuey, str):
        #     return 1
        if isinstance(valuex, dict):
            return 1
        if isinstance(valuey, dict):
            return -1
        return 1

    # pylint: disable=R0912
    def _get_confstring(self, _dict):
        # for item in sorted(
        #     _dict.items(), lambda x, y: self._comp_type(x[1], y[1])
        # ):
        try:
            order_keys = _dict.get_ordered_keys()
        except AttributeError:
            order_keys = sorted(
                _dict.keys(), lambda x, y: self._comp_write_keys(
                    _dict[x], _dict[y]
                )
            )
        for key in order_keys:
            try:
                item = _dict.get_ex(key)
                value = item[0]
                comments = item[1][1]
            except AttributeError:
                value = _dict.get(key)
                comments = []
            for comment in comments:
                self._str += self._get_indents() + comment
            if isinstance(value, tuple) or isinstance(value, list):
                if isinstance(value, tuple):
                    print 'its a tuple, key:%s, value:%s' % (key, value)
                if len(value) > 0 and isinstance(value[0], dict):
                    # items are all arrays
                    # [..@section]
                    #   abc:
                    # [..@section]
                    #   abc:
                    for ind in xrange(0, len(value)):
                        try:
                            item = value.get_ex(ind)
                        except AttributeError:
                            item = (value[ind], [])
                        for comment in item[1]:
                            self._str += self._get_indents() + comment
                        self._add_arraylevel(key)
                        self._get_confstring(item[0])
                        self._minus_level()
                else:
                    # a array list and array list has no sub-dict
                    # @item
                    # @item
                    for ind in xrange(0, len(value)):
                        try:
                            item = value.get_ex(ind)
                        except AttributeError:
                            item = (value[ind], [])
                        for comment in item[1]:
                            self._str += self._get_indents() + comment
                        self._appendline(
                            self._get_arrayflag() + str(key), item[0]
                        )
            elif isinstance(value, dict):
                self._addlevel(key)
                self._get_confstring(value)
                self._minus_level()
            else:
                # type(value) == type(""):
                self._appendline(key, value)

    def _get_confstring_ex(self, _dict):
        pass

    def _appendline(self, key, value):
        self._str += (
            self._get_indents() + str(key) +
            self._get_field_value_sep()+str(value)+self._get_linesep()
        )

    def _addlevel(self, key):
        self._str += (
            self._get_indents() + '[' + self._get_levelsep() + str(key) + ']'
            + self._get_linesep()
        )
        self._level += 1

    def _add_arraylevel(self, key):
        self._str += (
            self._get_indents() + '[' + self._get_arraylevel_sep() +
            str(key) + ']' + self._get_linesep()
        )
        self._level += 1

    def _minus_level(self):
        self._level -= 1

    # Set the conf dict
    def set_dict(self, conf_dict):
        """
        set a new conf_dict
        """
        if not isinstance(conf_dict, dict):
            raise TypeError('conf_dict is not a type of dict')
        self._dict = conf_dict
        # itemlist=sorted(dict.items(), lambda x,y: _comp_type(x[1],y[1]))

    # sort the dict, make type{dict} last
    @classmethod
    def _comp_type(cls, item_a, item_b):
        if type(item_a) in (tuple, list):
            if len(item_a) > 0:
                item_a = item_a[0]
        if type(item_b) in (tuple, list):
            if len(item_b) > 0:
                item_b = item_b[0]

        if type(item_a) == type(item_b):
            return 0
        elif type(item_b) == dict:
            return -1
        elif type(item_a) == dict:
            return 1
        # if type(item_a)!=type({}) or type(item_b)==type({}):
        #    return -1
        return 1


class HdfsXmlConf(object):
    """
    hdfs xmlconf modifier.

    Example:
    ::

        # modify and write new conf into hadoop-site.xmlconf
        xmlobj = xmlconf.HdfsXmlConf(xmlfile)

        # get hdfs conf items into a python dict
        key_values = xmlobj.get_items()

        # modify hdfs conf items
        for name in self._confdict['journalnode']['hadoop_site']:
            if name in key_values:
                key_values[name]['value'] = \
                self._confdict['journalnode']['hadoop_site'][name]
        else:
            key_values[name] = {
                'value': self._confdict['journalnode']['hadoop_site'][name],
                'description': ' '
            }
        hosts = ','.join(self._confdict['journalnode']['host'])
        key_values['dfs.journalnode.hosts'] = {
            'value': hosts, 'description':' journalnode hosts'
        }

        # write back conf items with new values
        xmlobj.write_conf(key_values)
    """
    def __init__(self, filepath):
        if not os.path.exists(filepath):
            raise IOError('file not found:{0}'.format(filepath))
        if not os.path.isfile(filepath):
            raise IOError('{0} not a file'.format(filepath))

        self._xmlpath = filepath
        self._confdict = None

    def _load_items(self):
        self._confdict = {}
        dom = minidom.parse(self._xmlpath)
        properties = dom.getElementsByTagName('property')
        for pro in properties:
            tmpdict = {}
            try:
                tmpdict['value'] = pro.getElementsByTagName(
                    'value'
                )[0].childNodes[0].nodeValue
            except IndexError:
                tmpdict['value'] = None
            try:
                tmpdict['description'] = pro.getElementsByTagName(
                    'description'
                )[0].childNodes[0].nodeValue
            except IndexError:
                tmpdict['description'] = None
            self._confdict[
                pro.getElementsByTagName('name')[0].childNodes[0].nodeValue
            ] = tmpdict
        return self._confdict

    def get_items(self):
        """
        return hadoop config items as a dict.

        ::
            {
                'dfs.datanode.max.xcievers':  {
                    'value': 'true', 'description': 'xxxxxxxxxx'
                },
                ......
            }
        """
        return self._load_items()

    def _write_to_conf(self, new_confdict):
        dom = minidom.parse(self._xmlpath)
        properties = dom.getElementsByTagName('property')
        tmpdict = copy.deepcopy(new_confdict)

        # modify if name exists
        for pro in properties:
            name = pro.getElementsByTagName('name')[0].childNodes[0].nodeValue
            valuenode = pro.getElementsByTagName('value')[0]
            if name in tmpdict:
                need_modify = False
                if valuenode.firstChild is None:
                    if tmpdict[name]['value'] is not None:
                        valuenode.appendChild(dom.createTextNode(''))
                        need_modify = True
                else:
                    need_modify = True
                if need_modify:
                    valuenode.firstChild.replaceWholeText(
                        tmpdict[name]['value']
                    )
                del tmpdict[name]
            else:
                parent = pro.parentNode
                parent.insertBefore(dom.createComment(pro.toxml()), pro)
                parent.removeChild(pro)

        configuration_node = dom.getElementsByTagName('configuration')[0]
        for name in tmpdict:
            new_pro = dom.createElement('property')
            new_name = dom.createElement('name')
            new_name.appendChild(dom.createTextNode(name))
            new_pro.appendChild(new_name)
            # value in the new property
            new_value = dom.createElement('value')
            if new_value is not None:
                new_value.appendChild(
                    dom.createTextNode(tmpdict[name]['value'])
                )
            new_pro.appendChild(new_value)
            # description
            new_desc = dom.createElement('description')
            new_desc.appendChild(
                dom.createTextNode(tmpdict[name]['description'])
            )
            new_pro.appendChild(new_desc)
            configuration_node.appendChild(new_pro)
        return dom.toprettyxml(newl='\n')

    def write_conf(self, kvs):
        """
        update config items with a dict kvs. Refer to the example above.

        ::
            {
                key : { 'value': value, 'description': 'description'},
                ......
            }
        """
        self._load_items()
        str_xml = self._write_to_conf(kvs)
        with open(self._xmlpath, 'w') as fhandle:
            fhandle.write(str_xml)
        self._confdict = kvs


def _main_hanle():
    dict4afs = Configure2Dict('/tmp/metaserver.conf')
    dictafs = dict4afs.get_dict()
    print json.dumps(dictafs, sort_keys=True, indent=4)

if __name__ == "__main__":
    # conf = CConf(g_prodUnitRuntime + 'Unitserver0/conf/','UnitServer.conf')
    # conf.update({'MasterPort':'1234','ProxyPortDelta':'0'})
    # conf.addAfterKeywordIfNoexist(
    #     'SnapshotPatchLimit', ('DelServerPerHourLimit', '99')
    # )
    _main_hanle()
