from yaml import dump


def write_json(dict_, yaml_file_path):

    with open(yaml_file_path, "w") as io:

        dump(dict_, io)
