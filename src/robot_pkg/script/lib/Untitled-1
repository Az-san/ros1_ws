import pickle
import sys

def read_pkl(file_path):
    try:
        with open(file_path, "rb") as f:
            data = pickle.load(f)
            print(data)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_pkl.py <path_to_pkl_file>")
    else:
        for file in sys.argv[1:]:
            print(f"Reading {file}:")
            read_pkl(file)
