import csv
import json

input_csv_files = ['clean_data_xaa.csv','clean_data_xab.csv','clean_data_xac.csv']
output_json_file = 'clean_data_xab_output.json'


for input_csv_file in input_csv_files:
    with open(input_csv_file, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        data = list(csvreader)

    with open(output_json_file, 'a') as jsonfile:
        for record in data:
            create_record = {
                "create": {
                    "_index": "amazon_data",
                    "_id": record['id']
                }
            }
            json.dump(create_record, jsonfile)
            jsonfile.write('\n')
            
            data_record = {
                "name": record['name'],
                "main_category": record['main_category'],
                "sub_category": record['sub_category'],
                "link": record['link'],
                "ratings": record['ratings'],
                "no_of_ratings": record['no_of_ratings'],
                "discount_price": record['discount_price'],
                "actual_price": record['actual_price'],
                "id": record['id']
            }
            json.dump(data_record, jsonfile)
            jsonfile.write('\n')
