from pyobjectscript_gen.cls import *
import csv
import sys

OUTPUT_DIR = "examples/generated/csv/"

PACKAGE = "Demo.CSV"

# ORM type name map to Objectscript specialized types for example
TYPE_MAP = {
    "integer": "%Integer",
    "text": "%String",
    "decimal": "%Numeric",
    "boolean": "%Boolean"
}

if __name__=="__main__":
    if len(sys.argv[1]) < 2:
        print("A CSV file as argument is required")
        exit(1)

    classes: dict[str, Class] = {}

    with open(sys.argv[1], newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            class_name, prop_name, prop_type, maxlen, required = row.values()
            if class_name not in classes:
               classes[class_name] = Class(f"{PACKAGE}.{class_name}", extends=["%Persistent"])
            prop = Property(
                name=prop_name,
                type=TYPE_MAP[prop_type]
            )
            if maxlen:
                prop.params["MAXLEN"] = int(maxlen)
            if required.upper() == "TRUE":
                prop.keywords["Required"] = None
            classes[class_name].components.append(prop)

        for name, cls in classes.items():
            path = f"{OUTPUT_DIR}{name}.cls"
            print(f"generating file {path} ...")
            with open(path, 'w') as file:
                cls.generate(file)
