from shutil import copy, copytree
import sys
import yaml

def main():
  with open('files.yml', 'r') as stream:
    file_names = yaml.safe_load(stream)

  copy(file_names[0], './input/')
  for index in range(1, len(file_names)):
    copytree(file_names[index], './input/', dirs_exist_ok=True)

if __name__ == "__main__":
  main()
