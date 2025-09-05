def json_save(json, output_dir):
    with open(output_dir, "w") as file:
        json.dump(json, file)

