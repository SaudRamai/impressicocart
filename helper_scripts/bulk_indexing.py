import subprocess
import glob
import os

def split_file(input_file, lines_per_file, output_prefix):
    split_command = f"split -l {lines_per_file} {input_file} {output_prefix}"
    subprocess.run(split_command, shell=True, check=True)
    print(f"File {input_file} split into chunks with prefix {output_prefix}.")

def upload_files(prefix, url):
    files = sorted(glob.glob(f"{prefix}*"))
    headers = {'Content-Type': 'application/x-ndjson'}

    for file in files:
        command = f"curl -H 'Content-Type: application/x-ndjson' -XPOST '{url}' --data-binary @{file}"
        subprocess.run(command, shell=True, check=True)
        print(f"Uploaded {file} to {url}.")

def main():
    input_file = "clean_data_xab_output.json"
    lines_per_file = 100000
    output_prefix = "clean_data_xab_output"
    es_url = "localhost:9200/amazon_data/_bulk?pretty"

    split_file(input_file, lines_per_file, output_prefix)
    upload_files(output_prefix, es_url)

if __name__ == "__main__":
    main()
