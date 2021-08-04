import os
import sys

abs_name = os.path.abspath(__file__)
print("ab", abs_name)
dir_name = os.path.dirname(__file__)
print("dir", dir_name)
print(os.getcwd())
print(os.path.dirname(os.path.realpath(__file__)))
print(sys.argv[0])