from pyobjectscript_gen.cls import *
import sys

if __name__=="__main__":
    cls = Class("Demo.MyExample.MyClass")
    cls.extends = ["%RegisteredObject"]

    # example of declaratively creating properties
    cls.components = [
        Property(
            name="Property1",
            type="%String",
        ),
        Property(
            name="Property2",
            type="%Numeric",
        ),
    ]

    # example of iteratively creating a method
    method = Method("MyMethod")
    method.return_type = "%String"
    method.impl = [
        "set returnvalue=..Property1_..Property2",
        "quit returnvalue"
    ]
    cls.components.append(method)

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'w') as file:
            cls.generate(file)
    else:
        # generate on sys.stdout
        cls.generate()
