#!/usr/bin/env python

import os


def _conv(val, as_type, trace_s, trace_n):
    result = None
    if val is not None:
        if as_type == "int":
            if len(val) > 0:
                result = int(val)
            else:
                result = 0
                print("WARNING in save1d _conv: " +
                      " no value for " + as_type + " in '" + trace_s +
                      "' line " + str(trace_n))
        elif as_type == "float":
            if len(val) > 0:
                result = float(val)
            else:
                result = 0.0
                print("WARNING in save1d _conv: " +
                      " no value for " + as_type + " in '" + trace_s +
                      "' line " + str(trace_n))
        elif as_type == "string":
            result = val
        else:
            print("ERROR in save1d _conv: bad as_type param '" +
                  str(as_type) +
                  " (should be: 'int', 'float', 'string')")
    return result


def _to_literal(val_original):
    val = val_original.strip()
    if val != "None":
        if len(val) >= 2 and val[0] == "\"" and val[-1] == "\"":
            return val[1:-1].replace("\\\"", "\"").replace("\\n", "\n")
        else:
            return val
    return None


def _to_writable(val):
    if val is not None:
        val = str(val)
        return '"'+val.replace("\n", "\\n").replace("\"", "\\\"")+'"'
    return "None"


def load(name, default=None, file_format='list', as_type='string'):
    result = None
    f_name = name + '.' + file_format
    if os.path.isfile(f_name):
        f = open(f_name, 'r')
        counting_n = 1
        if file_format == 'list':
            result = []
            line = True
            while line:
                line = f.readline()
                if line:
                    if len(line.strip()) > 0:
                        result.append(_conv(_to_literal(line),
                                      as_type, f_name, counting_n))
                    counting_n += 1
        elif file_format == 'dict':
            result = {}
            line_original = True
            while line_original:
                line_original = f.readline()
                if line_original:
                    op = "="
                    line = line_original.rstrip()
                    op_i = line.find(op)
                    if op_i > 0:
                        result[line[:op_i].strip()] = \
                            _conv(_to_literal(line[op_i+1:]),
                                  as_type, f_name, counting_n)
                    counting_n += 1
        elif file_format == "value":
            if as_type == 'string':
                result = ""
                line = True
                while line:
                    line = f.readline()
                    if line:
                        result += line.rstrip("\n").rstrip("\r") + "\n"
                        counting_n += 1
                result = result.rstrip("\n")
            else:
                result = _conv(_to_literal(f.readline()), as_type,
                               f_name, counting_n)
        else:
            print("ERROR in save1d load: file_format must be"
                  " 'list', 'dict', or 'value'")
        f.close()
    else:
        return default
    return result


def save(name, data, file_format='list'):
    f = open(name+'.'+file_format, 'w')
    if file_format == 'list':
        for v in data:
            f.write(_to_writable(v)+"\n")
    elif file_format == 'dict':
        op = "="
        for key in data:
            if op not in key:
                v = data[key]
                f.write(key+"="+_to_writable(v)+"\n")
            else:
                print("ERROR in save1d save: " +
                      "failed to save value since key is '" + str(key) +
                      " (should not contain '" + sign + "'")
    elif file_format == 'value':
        f.write(str(data)+"\n")
    else:
        print("ERROR in save1d load: file_format must be"
              " 'list', 'dict', or 'value'")
    f.close()

if __name__ == "__main__":
    print("Instead of running this file, use it in your program like:\n"
          "from save1d import *")
