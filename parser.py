import re
import argparse
import urllib2
from pprint import pprint

def check_file(name):
    try:
        with open(name,'r') as fd:
            return fd.read()
    except:
        raise argparse.ArgumentTypeError('Corrupted File')

def check_url(url):
    try:
        return urllib2.urlopen(url).read()
    except:
         raise argparse.ArgumentTypeError('Error in URL parsing')

def commaParser(data):
    if data and data[0]==',':
        return (',', data[1:].strip())

def nullParser(data):
    if data[0:4]=='null':
        return (None,data[4:].strip())

def booleanParser(data):
    if data[0:4]=='true':
        return (True, data[4:].strip())
    elif data[0:5]=='false':
        return (False, data[5:].strip())

def numberParser(data):
    if data:
        regEx = re.findall('^(-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)',data)
        if regEx:
            index = len(regEx[0])
            try: return (int(regEx[0]), data[index:].strip())
            except ValueError:
                try: return (float(regEx[0]), data[index:].strip())
                except ValueError:
                    return (regEx, data[index:].strip())
            
def colonParser(data):
    if data[0]==':':
        return (':', data[1:].lstrip())
    
def stringParser(data):
    if data[0] == '"':
        data = data[1:]
        index = data.find('"')
        while data[index-1] == '\\':
            index += data[index+1:].find('"')+1
        return (data[:index], data[index+1:].strip())

def arrayParser(data):
    parsedarray = []
    if data[0] == '[':
        data = data[1:].strip()
        while len(data)> 0:
            result = parser_factory(stringParser, numberParser, booleanParser, nullParser, arrayParser, objectParser)(data)
            if result != None:
                parsedarray.append(result[0])
                data = result[1].strip()
                result = commaParser(data)
                if result != None:
                    data = result[1].strip()
                else:
                    if data and data[0].strip() != ']':
                        raise SyntaxError
            if data and data[0] == ']':
                return (parsedarray, data[1:].strip())

def objectParser(data):
    parsedobj = {}
    if data[0] == '{':
        data = data [1:].strip()
        while data[0] != '}':
            result = stringParser(data)
            if result == None:
                raise SyntaxError
            key = result[0]
            result = colonParser(result[1].strip())
            if result == None:
                raise SyntaxError
            result = parser_factory(stringParser, numberParser, booleanParser, nullParser, arrayParser, objectParser)(result[1].strip())
            if result == None:
                raise SyntaxError
            parsedobj[key] = result[0]
            data = result[1].lstrip()
            result = commaParser(data)
            if result:
                data = result[1].strip()
            elif data[0]!='}':
                raise SyntaxError
        return (parsedobj, data[1:])

def parser_factory(*args):
    def custom_parser(data):
        for each_parser in args:
            result = each_parser(data)
            if result:
                return result
    return custom_parser

if "__main__" == __name__:
    arg_parser = argparse.ArgumentParser(prog='json Parser')
    arg_group  = arg_parser.add_mutually_exclusive_group(required=True)
    arg_group.add_argument('-f', '--filename', type=check_file, help='file name, that contains JSON')
    arg_group.add_argument('-u', '--url', type=check_url, help='url')
    args = arg_parser.parse_args()
    if args.filename:
        data = args.filename
    elif args.url:
        data = args.url
    pprint(parser_factory(arrayParser, objectParser)(data.strip())[0])
