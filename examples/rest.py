from pyobjectscript_gen.cls import *
import xml.dom.minidom as DOM

class RequestClass(Class):
    extends = ["%Persistent", "Ens.Request"]
    properties: list[Property]
    body: Property | None
    mapping: dict[str, str]
    """
    Map property name to type of parameter.
    Can be any of:
    - query
    - path
    - body
    - header
    - cookie (not supported)
    """

    content_type: str | None

    def __init__(self,
                name: str,
                extends: list[str],
                *args,
                properties: list[Property] = [],
                mapping: dict[str, str] = {},
                content_type: str | None = None,
                **kwargs):
        super().__init__(name, self.extends + extends, *args, **kwargs)
        self.properties = properties
        self.mapping = mapping
        self.content_type = content_type
        self._generate()


    def _generate(self):
        init_params = Method("InitParams",
                                arguments=[
                                    MethodArgument("pRequest", "%Net.HttpRequest", prefix="ByRef"),
                                ],
                                impl=[
                                    f'Do pRequest.SetParam("{prop.name}", ..{prop.name})' 
                                    for prop in filter(lambda prop: self.mapping[prop.name] == "query", self.properties)
                                ],
                            )
        init_headers = Method("InitHeaders",
                                arguments=[
                                    MethodArgument("pRequest", "%Net.HttpRequest", prefix="ByRef"),
                                ],
                                impl=[
                                    f'Do pRequest.SetHeader("{prop.name}", ..{prop.name})' 
                                    for prop in filter(lambda prop: self.mapping[prop.name] == "header", self.properties)
                                ],
                            )
        if self.content_type:
            init_headers.impl.append(f'Do pRequest.SetHeader("Content-Type", "{self.content_type}")')
        self.components = [
            *self.components,
            *self.properties,
            init_params,
            init_headers,
        ]


class ResponseClass(Class):
    extends = ["%Persistent", "Ens.Response"]


class Route(Method):
    def __init__(self, name: str, request: str, response: str, http_method: str, url: str, **kwargs):
        super().__init__(
            name=name,
            arguments=[
                MethodArgument("pInput", request),
                MethodArgument("pOutput", response, prefix="Output"),
            ],
            return_type="%Status",
            impl=f'..{http_method.capitalize()}("{url}", pInput, .pOutput)',
            keywords={
                "CodeMode": "expression",
            },
            **kwargs
        )


class BusinessOperation(Class):
    extends = ["Ens.BusinessOperation"]

    def __init__(self, name: str, routes: list[Route], **kwargs):
        super().__init__(
            name=name,
            extends=self.extends,
            **kwargs
        )
        self.components = [*self.components, *routes]
        self.components.append(XData("MessageMap", content=self.get_message_map()))

    @staticmethod
    def create_message_map(mapping: dict[str, str]) -> DOM.Document:
        root = DOM.Document()
        map_items = root.createElement("MapItems")
        root.appendChild(map_items)
        for key, value in mapping.items():
            item = root.createElement("MapItem")
            item.setAttribute("MessageType", key)
            method = root.createElement("Method")
            method.appendChild(root.createTextNode(value))
            item.appendChild(method)
            map_items.appendChild(item)
        return root

    def get_message_map(self):
        methods = [*filter(lambda component: isinstance(component, Route), self.components)]
        message_map = self.create_message_map(dict([(method.arguments[0].type, method.name) for method in methods]))
        return message_map.documentElement.toprettyxml(indent="  ").rstrip()


if __name__ == "__main__":
    message_map_xml = BusinessOperation.create_message_map({
        "Test.Messages.AddPetRequest": "AddPet",
        "Test.Messages.TestRequest": "Test",
    })
    message_map = message_map_xml.documentElement.toprettyxml(indent="  ").rstrip()
    
    cls = Class(
        "Test.Test",
        extends=["%Persistent", "Ens.Request"],
        components=[
            Parameter("RESPONSECLASSNAME", type="STRING", value="Ens.Response"),
            Parameter("%JSONENABLED", value=1, keywords={"Deprecated": None}),
            Property("Id", "%Integer",
                doc_string="Required property",
                keywords={
                    'Required': None,
                    'InitialExpression': 0,
                }
            ),
            Property("TestAbc123", type="%String",
                params={
                    "XMLNAME": "test_abc 123",
                    "MAXLEN": 50,
                },
                keywords={"Deprecated": None}
            ),
            Property("Body", "Test.Object",
                collection="list",
                doc_string="List example",
            ),
            ClassMethod(
                "Test",
                arguments=[
                    MethodArgument("pInput"),
                    MethodArgument("pOutput", type="Ens.Response", prefix="Output"),
                    MethodArgument("test", type="%Boolean", value=0),
                ],
                return_type="%Status",
                impl=[
                    "set pOutput = ##class(Ens.Response).%New()",
                    "return $$$OK"
                ],
                doc_string=["Test method", "Multiline example"]
            ),
            Method(
                "AddPet",
                arguments=[
                    MethodArgument("pInput", type="Ens.Request"),
                    MethodArgument("pOutput", type="Ens.Response", prefix="Output"),
                ],
                return_type="%Status",
                impl='..Post("/pet", pInput, .pOutput)',
                keywords={'CodeMode': 'expression'}
            ),
            XData(
                "MessageMap",
                content=message_map,
                keywords={
                    "MimeType": "application/xml"
                }
            ),
        ],
        keywords={
            'Abstract': None
        },
        doc_string="Sample class generated by Jinja"
    )

    bo = BusinessOperation(
        "Test.BO",
        routes=[
            Route("AddPet", "Test.AddPetRequest", "Ens.Response", "POST", "/pet"),
            Route("DeletePet", "Test.DeletePetRequest", "Ens.Response", "DELETE", "/pet"),
        ]
    )

    req = RequestClass("Test.AddPetRequest",
        extends=["%JSON.Adaptor"],
        properties=[
            Property("status", "%String"),
            Property("id", "%Integer"),
            Property("ApiKey", "%String")
        ],
        mapping={
            "status": "query",
            "id": "path",
            "ApiKey": "header",
        },
        content_type="application/json",
        components=[
            Parameter("RESPONSECLASSNAME", value="Ens.Response"),
        ]
    )

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'w') as file:
            cls.generate(file)
    else:
        cls.generate()