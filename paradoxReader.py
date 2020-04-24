import argparse
import json
from os import listdir
from os.path import isfile, join, isdir, basename
import re
import sys
import time
from tqdm import tqdm

def main():
    start_time = time.time()
    args = _get_args()

    if isdir(args.file_name):
        successful = 0
        files = [f for f in listdir(args.file_name) if isfile(join(args.file_name, f)) and str.endswith(f, '.txt')]
        for file_name in tqdm(files):
            result = decode(join(args.file_name, file_name), args.intermediate, args.no_json)
            if result is not None:
                successful += 1

        print("{} out of {} succesful".format(successful, len(files)))

    else:
        decode(args.file_name, args.intermediate, args.no_json)
        print("--- %s seconds ---" % (time.time() - start_time))


def _get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name')
    parser.add_argument('--intermediate', '-i', help="Save the intermediate code. Useful for debugging", action="store_true", default=False)
    parser.add_argument('--no_json', '-n', action="store_true", default=False)

    return parser.parse_args()


def decode(file_path, save_intermediate, no_json):
    try:
        file = open(file_path, 'r')
    except FileNotFoundError:
        print('ERROR: Unable to find file: ' + file_path)
        return None

    file_name = basename(file_path)

    data = file.read()
    data = re.sub(r'#.*', '', data) # Remove comments
    data = re.sub(r'(?<=^[^\"\n])*(?<=[0-9\.\-a-zA-Z])+(\s)(?=[0-9\.\-a-zA-Z])+(?=[^\"\n]*$)', '\n', data, flags=re.MULTILINE) # Seperate one line lists
    data = re.sub(r'[\t ]', '', data) # Remove tabs and spaces

    definitions = re.findall(r'(@\w+)=(.+)', data) # replace @variables with value

    if definitions:
        for definition in definitions:
            data = re.sub(r'^@.+', '', data, flags=re.MULTILINE)
            data = re.sub(definition[0], definition[1], data)

    data = re.sub(r'\n{2,}', '\n', data) # Remove excessive new lines
    data = re.sub(r'\n', '', data, count=1)  # Remove the first new line
    data = re.sub(r'{(?=\w)', '{\n', data) # reformat one-liners
    data = re.sub(r'(?<=\w)}', '\n}', data) # reformat one-liners
    data = re.sub(r'^[\w-]+(?=[\=\n><])', r'"\g<0>"', data, flags=re.MULTILINE)  # Add quotes around keys
    data = re.sub(r'([^><])=', r'\1:', data)  # Replace = with : but not >= or <=
    data = re.sub(r'(?<=:)(?!-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)(?!\".*\")[^{\n]+', r'"\g<0>"', data)  # Add quotes around string values
    data = re.sub(r':"yes"', ':true', data) # Replace yes with true
    data = re.sub(r':"no"', ':false', data)  # Replace no with false
    data = re.sub(r'([<>]=?)(.+)', r':{"value":\g<2>,"operand":"\g<1>"}', data) # Handle < > >= <=
    data = re.sub(r'(?<![:{])\n(?!}|$)', ',', data)  # Add commas
    data = re.sub(r'\s', '', data) # remove all white space
    data = re.sub(r'{(("[a-zA-Z_]+")+)}', r'[\g<1>]', data) # make lists
    data = re.sub(r'""', r'","', data) # Add commas to lists
    data = re.sub(r'{("\w+"(,"\w+")*)}', r'[\g<1>]', data)
    data = re.sub(r'((\"hsv\")({\d\.\d{1,3}(,\d\.\d{1,3}){2}})),', r'{\g<2>:\g<3>},', data) # fix hsv objects
    data = re.sub(r':{([^}{:]*)}', r':[\1]', data) # if there's no : between list elements need to replace {} with []
    data = re.sub(r'\[(\w+)\]', r'"\g<1>"', data)
    data = re.sub(r'\",:{', '":{', data) # Fix user_empire_designs
    data = '{' + data + '}'

    file_name = basename(file_path)

    if save_intermediate:
        with open('./output/' + file_name + '.intermediate', 'w') as output:
            output.write(data)

    try:
        json_data = json.loads(data, object_pairs_hook=_handle_duplicates)
    except json.decoder.JSONDecodeError:
        # print('ERROR: Unable to parse {}'.format(file_name))
        # print('Dumping intermediate code into file: {}_{:.0f}.intermediate'.format(file_name, time.time()))

        with open('./output/{}_{:.0f}.intermediate'.format(file_name, time.time()), 'w') as output:
            output.write(data)

        return None

    with open('./output/' + file_name + '.json', 'w') as file:
        json.dump(json_data, file, indent=2)

    return data


def _handle_duplicates(ordered_pairs):
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            if isinstance(d[k], list):
                d[k].append(v)
            else:
                d[k] = [d[k], v]
        else:
           d[k] = v
    return d


if __name__ == "__main__":
    main()
