from pyobjectscript_gen.cls import *
from dataclasses import dataclass, field
import xml.dom.minidom as DOM

@dataclass
class RequestClass(Class):
    extends = ["%Persistent", "Ens.Request"]
    body: Property | None = None
    properties: list[Property] = field(default_factory=list)
    content_type: str | None = None
    mapping: dict[str, str] = field(default_factory=dict)
    """
    Map property name to type of parameter.
    Can be any of:
    - query
    - path
    - body
    - header
    - cookie (not supported)
    """

    def __init__(self,
                name: str,
                extends: list[str],
                *args,
                properties: list[Property] = [],
                mapping: dict[str, str] = {},
                content_type: str | None = None,
                **kwargs):
        super().__init__(name, extends=self.extends + extends, *args, **kwargs)
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


@dataclass
class ResponseClass(Class):
    extends = ["%Persistent", "Ens.Response"]


@dataclass
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


@dataclass
class RestBusinessOperation(Class):
    """
    Custom REST BusinessOperation using custom extends
    """
    extends = ["Ens.BusinessOperation", "REST.HttpMethods"]

    def __init__(self, name: str, routes: list[Route], extends: list[str] = None, **kwargs):
        super().__init__(
            name=name,
            extends=self.extends + (extends if extends else []),
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
    import sys

    req = RequestClass("REST.Messages.AddPetRequest",
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

    resp = ResponseClass("REST.Messages.AddPetResponse",
        extends=["%JSON.Adaptor"],
        components=[
            Property("status", "%String"),
        ]
    )

    bo = RestBusinessOperation(
        "REST.BusinessOperation",
        [
            Route("AddPet", req.name, resp.name, "POST", "/pet"),
            # Route("DeletePet", "Test.DeletePetRequest", "Ens.Response", "DELETE", "/pet"),
        ]
    )

    if len(sys.argv) > 1:
        dir = sys.argv[1]
        with open(f"{dir}/bo.cls", 'w') as file:
            bo.generate(file)
        with open(f"{dir}/request.cls", 'w') as file:
            req.generate(file)
        with open(f"{dir}/response.cls", 'w') as file:
            resp.generate(file)
    else:
        print("error: specify output folder as argument")