from dataclasses import dataclass, field
from typing import Any, TextIO
from datetime import datetime
from pathlib import Path
import jinja2
import sys

@dataclass
class Component:
    """
    Base class for Objectscript class components.
    """

    name: str
    """
    Name of the Objectscript component.
    """

    doc_string: str | list[str] = field(default_factory=list, kw_only=True)
    """
    Optional documentation string, using the form of a 3 slashes comment above the Objectscript component.

    Can be a string or list of string for multilines comments.
    """
    
    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    Compiler keywords
    
    see: [Introduction to Compiler Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=GOBJ_classes#GOBJ_classes_keywords)
    
    Optional dict used to specify keywords for this component.

    Use `{"Keyword": None}` for keywords that do not have a value.
    """
    
    def format_name(self) -> str:
        """
        Enclose `name` with quotes if `name` contains spaces or underscores.
        """
        
        if "_" in self.name or " " in self.name:
            return f'"{self.name}"'
        return self.name
    
    def on_generate(self):
        """
        Function called before class generation, can be overriden by subclasses for specific purposes.
        """
        pass

    def get_template(self) -> str:
        """
        Returns the name of the Jinja2 template used by component
        """
        pass


@dataclass
class Expression:
    """
    Wrapper class for Objectscript expressions.

    Expressions will be interpreted as Objectscript expressions instead of value strings by the generator.

    ### Example usage
    ```
    Parameter(
        name="COMPILETIME",
        value=Expression("{$zdatetime($h)}")
    )
    ```
    
    Will output:
    ```
    Parameter COMPILETIME = {$zdatetime($h)};
    ```
    """    

    expr: str

    def __str__(self):
        return self.expr


@dataclass
class XData(Component):
    """
    [Defining and Using XData Blocks](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=GOBJ_xdata)

    ```
    XData Name [ Keywords ]
    {
        Content
    }
    ```
    """

    content: str | list[str]
    """
    Content of XData, can be data of any arbitrary format, as string or list of string.
    
    Specify Mime type with `keywords={"MimeType": type}`.
    """

    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    [XData Syntax and Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_xdata)

    Optional dict used to specify keywords for this component.
    
    Use `{"Keyword": None}` for keywords that do not have a value.

    ### Valid XData keywords
    - SchemaSpec — Optionally specifies an XML schema against which the XData can be validated.
    - XMLNamespace — Optionally specifies the XML namespace to which the XData block belongs. You can also, of course, include namespace declarations within the XData block itself.
    - MimeType — The MIME type (more formally, the Internet media typeOpens in a new tab) of the contents of the XData block. The default is text/xml.
    """

    def get_template(self) -> str:
        return "xdata.cls.jinja"


@dataclass
class Storage(Component):
    """
    [Storage Definitions](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=GOBJ_storage)

    ```
    Storage Name [ Keywords ]
    {
        Definition
    }
    ```
    
    Should usually not be used unless a custom storage definition is needed.
    """

    name: str = "Default"
    """
    Name of the Objectscript component

    "Default" for Storage components by default
    """

    definition: str | list[str] = ""
    """
    XML storage definition as string or list of string.

    XML storage definition syntax is not supported by this library and should be used in conjunction with a XML library.
    """

    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    [Storage Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_storage)

    Optional dict used to specify keywords for this component.
    
    Use `{"Keyword": None}` for keywords that do not have a value

    ### Valid Storage keywords
    - DataLocation – Specifies where data is stored for this class.
    - DefaultData – Specifies the default data storage definition.
    - Final – Specifies that the storage definition cannot be modified by subclasses.
    - IdFunction – Specifies the system function to be used to assign new ID values for a persistent class using default storage.
    - IdLocation – Specifies location of the ID counter.
    - IndexLocation – Specifies the default storage location for indexes.
    - SqlRowIdName – Specifies the name used for the row ID within SQL.
    - SqlRowIdProperty – Specifies the SQL RowId property.
    - SqlTableNumber – Specifies the internal SQL table number.
    - State – Specifies the data definition used for a serial object.
    - StreamLocation – Specifies the default storage location for stream properties.
    - Type – Storage class used to provide persistence.
    """

    def get_template(self) -> str:
        return "storage.cls.jinja"


@dataclass
class Trigger(Component):
    """
    [Syntax of Triggers in Class Definitions](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_trigger_syntax)

    ```
    Trigger Name [ Keywords ]  
    { 
        Implementation
    }
    ```
    """

    impl: str | list[str] = field(default_factory=list)
    """
    Trigger implementation
    
    Can be a simple string for already indented and newline delimited code, or for use with `CodeMode = expression`
    or a list of strings for multiline code, in which case will be indented automatically by the generator.

    Objectscript routine code generation and syntax validation is not supported by this library.
    """

    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    [Trigger Syntax and Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_trigger)

    Optional dict used to specify keywords for this component.
    
    Use `{"Keyword": None}` for keywords that do not have a value.

    ### Valid Trigger keywords
    - CodeMode – Specifies how this trigger is implemented.
    - Event – Specifies the SQL events that will fire this trigger. Required (no default).
    - Final – Specifies whether this trigger is final (cannot be overridden in subclasses).
    - Foreach – Controls when the trigger is fired.
    - Internal – Specifies whether this trigger definition is internal (not displayed in the class documentation).
    - Language – Specifies the language in which the trigger is written.
    - NewTable – Specifies the name of the transition table that stores the new values of the row or statement affected by the event for this trigger.
    - OldTable – Specifies the name of the transition table that stores the old values of the row or statement affected by the event for this trigger.
    - Order – In the case of multiple triggers for the same EVENT and TIME, specifies the order in which the triggers should be fired.
    - SqlName – Specifies the SQL name to use for this trigger.
    - Time – Specifies whether the trigger is fired before or after the event.
    - UpdateColumnList – Specifies one or more columns whose modification causes the trigger to be fired by SQL. Available only for TSQL.
    """

    def get_template(self) -> str:
        return "trigger.cls.jinja"
    

@dataclass
class Parameter(Component):
    """
    [Defining Class Parameters](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=GOBJ_parameters#GOBJ_parameters_def)

    ```
    Parameter NAME as Type [ Keywords ] = value;
    ```
    """

    type: str | None = None
    """
    Optional type of the Parameter

    [Allowed Types for Parameters](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=ROBJ_parameter_syntax)
    """
    
    value: Any | None = None
    """
    Optional default value or expression of the Parameter
    """

    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    [Parameter Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_parameter)

    Optional dict used to specify keywords for this component.
    
    Use `{"Keyword": None}` for keywords that do not have a value

    ### Valid Parameter keywords
    - Abstract – Specifies whether this is an abstract parameter.
    - Constraint – Specifies a user interface constraint in IDEs for this parameter.
    - Deprecated – Specifies that this parameter is deprecated. This keyword is ignored by the class compiler and merely provides a human-readable indicator that the parameter is deprecated.
    - Final – Specifies whether this parameter is final (cannot be overridden in subclasses)
    - Flags – Modifies the user interface type (in IDEs) for this parameter.
    - Internal – Specifies whether this parameter definition is internal (not displayed in the class documentation).
    """

    def get_template(self) -> str:
        return "parameter.cls.jinja"


@dataclass
class Property(Component):
    """
    [Defining and Using Literal Properties](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GOBJ_proplit)

    ```
    Property Name as Type(PARAM1=value, PARAM2=value) [ Keywords ];
    ```
    """

    type: str | None = None
    """
    Optional type of the Property
    """

    collection: str | None = None
    """
    [Defining Collection Properties](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GOBJ_propcoll#GOBJ_propcoll_def)

    Optional parameter used to specify if this `Property` should be a List or Array of the specified `type`

    Must be `"list"`, `"array"` or `None`

    ### Example

    ```
    Property MyProp As list of Type;
    Property MyProp As array of Type;
    ```
    """

    params: dict[str, Any] = field(default_factory=dict)
    """
    [Property Parameters](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GOBJ_propparams)
    
    Optional dict used to specify Property Parameters

    ### Example

    ```
    Property(
        name="MyProp", 
        type="%String",
        params={
            "XMLNAME": "my_prop",
            "MAXLEN": 10,
        },
    ),
    ```
    """

    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    [Property Syntax and Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_property)

    Optional dict used to specify keywords for this component.
    
    Use `{"Keyword": None}` for keywords that do not have a value

    ### Valid Property keywords
    - Aliases – Specifies additional names for this property for use via object access.
    - Calculated – Specifies that this property has no in-memory storage allocated for it when the object containing it is instantiated.
    - Cardinality – Specifies the cardinality of this relationship property. Required for relationship properties. Not used for other properties.
    - ClientName – Specifies an alias used by client projections of this property.
    - Collection – Deprecated means of specifying the collection type of a collection property. Do not use.
    - ComputeLocalOnly – Controls whether a SqlComputed field is computed only on the local server for federated and shareded tables.
    - Deprecated – Specifies that this property is deprecated. This keyword is ignored by the class compiler and merely provides a human-readable indicator that the property is deprecated.
    - Final – Specifies whether this property is final (cannot be overridden in subclasses).
    - Identity – Specifies whether this property corresponds to the identity column in the corresponding SQL table. Applies to persistent classes.
    - InitialExpression – Specifies an initial value for this property.
    - Internal – Specifies whether this property definition is internal (not displayed in the class documentation). .
    - Inverse – Specifies the inverse side of this relationship. Required for relationship properties. Not used for other properties.
    - MultiDimensional – Specifies that this property has the characteristics of a multidimensional array.
    - OnDelete – Specifies the action to take in the current table when a related object is deleted. This keyword applies only to a relationship property that specifies Cardinality as Parent or One. Its use is invalid in all other contexts.
    - Private – Specifies whether the property is private (can be used only by methods of this class or its subclasses).
    - ReadOnly – Specifies that a property is read-only, which limits the number of ways its value can be set.
    - Required – For a persistent class, specifies that the property’s value must be given a value before it can be stored to disk. For an XML-enabled class, specifies that the element to which the property is mapped is required.
    - ServerOnly – Specifies whether this property is projected to a Java client.
    - SqlColumnNumber – Specifies the SQL column number for this property. Applies only to persistent classes.
    - SqlComputeCode – Specifies code that sets the value of this property.
    - SqlComputed – Specifies whether that this is a computed property.
    - SqlComputeOnChange – This keyword controls when the property is recomputed. Applies only to triggered computed properties.
    - SqlFieldName – Specifies the field name to use for this property in the SQL projection. Applies to persistent classes.
    - SqlListDelimiter – Specifies the delimiter character used within SQL for lists. Applies to list properties in persistent classes. For use only by legacy applications.
    - SqlListType – Specifies the values of this field are represented in memory in SQL and stored on disk. Applies only to list properties in persistent classes. For use only by legacy applications.
    - Transient – Specifies whether the property is stored in the database. Applies only to persistent classes.
    """

    def get_template(self) -> str:
        return "property.cls.jinja"


@dataclass
class Index(Component):
    """
    [Defining Indexes Using a Class Definition](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GSOD_indexes#GSOD_indexes_def_cls)
    
    ```
    INDEX Name ON Property AS Collation [ Keywords ];
    ```

    Note: Complex indexes using expressions or multiple properties are not implemented yet by this library.

    A workaround for this is to specify `property` with the full desired expression and leave `collation` empty, such as:

    ```
    index.property = Expression("(Name As SQLstring, Code As Exact)")
    ```
    """

    property: str
    """
    Name of the property to index
    """

    collation: str
    """
    [Collation Types](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GSQL_collation#GSQL_collation_types)
    """

    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    [Index Syntax and Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_index)

    Optional dict used to specify keywords for this component.

    Use `{"Keyword": None}` for keywords that do not have a value
    
    ### Valid Foreign Key keywords
    - Abstract – Specifies that an index is abstract.
    - Condition – Defines a conditional index and specifies the condition that must be met for a record to be included in the index.
    - CoshardWith – Adds an index that specifies the name of the class with which this class is cosharded.
    - Data – Specifies a list of properties whose values are to be stored within this index.
    - Deferred – Defines a deferred index.
    - Extent – Defines an extent index.
    - IdKey – Specifies whether this index defines the Object Identity values for the table.
    - Internal – Specifies whether this index definition is internal (not displayed in the class documentation).
    - PrimaryKey – Specifies whether this index defines the primary key for the table.
    - ShardKey – Defines an index that specifies the shard key for this class.
    - SqlName – Specifies an SQL alias for the index.
    - Type – Specifies the type of index.
    - Unique – Specifies whether the index should enforce uniqueness.
    """

    def get_template(self) -> str:
        return "index.cls.jinja"


@dataclass
class ForeignKey(Component):
    """
    [Syntax of Foreign Keys in Class Definitions](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=ROBJ_foreignkey_syntax)
    
    ```
    ForeignKey name(key_props) References referenced_class(ref_index) [ Keywords ];
     ```
    """

    referenced_class: str
    """
    Required property, specifies the foreign table (that is, the class to which the foreign key points).
    """

    key_props: list[str] = field(default_factory=list)
    """
    Specifies the property or properties that are constrained by this foreign key.

    Specifically this property or properties must match the referenced value in the foreign table.

    At least one property required.
    """

    ref_index: str = None
    """
    Optional property which specifies the unique index name within `referenced_class`.

    If you omit `ref_index`, then the system uses the `IDKEY` index in `referenced_class`.
    """

    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    [Foreign Key Syntax and Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_foreignkey)

    Optional dict used to specify keywords for this component.

    Use `{"Keyword": None}` for keywords that do not have a value

    ### Valid Foreign Key keywords
    - Internal – Specifies whether this foreign key definition is internal (not displayed in the class documentation).
    - NoCheck – Specifies whether InterSystems IRIS should check this foreign key constraint.
    - OnDelete – Specifies the action that this foreign key should cause in the current table when a record deleted in the foreign table is referenced by a record in the current table.
    - OnUpdate – Specifies the action that this foreign key should cause in the current table when the key value of a record in the foreign table is updated and that record is referenced by a record in the current table.
    - SqlName – Specifies an SQL alias for the foreign key.
    """ 

    def get_template(self) -> str:
        return "foreignkey.cls.jinja"
    

@dataclass
class Projection(Component):
    """
    [Defining Class Projections](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GOBJ_projections)
    
    ```
    Projection name As projection_class(PARAM1="value", ...) [ Keywords ];
     ```
    """

    projection_class: str
    """
    Required property, specifies the name of the projection class, which is a subclass of `%Projection.AbstractProjection`.
    """

    params: dict[str, Any] = field(default_factory=dict)
    """
    [Property Parameters](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GOBJ_propparams)
    
    Optional dict used to specify Property Parameters for the `projection_class`

    ### Example

    ```
    Projection(
        name="MyProj", 
        projection_class="%Projection.Java",
        params={
            "ROOTDIR": "c:\\java",
        },
    ),
    ```
    """

    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    [Projection Syntax and Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_projection)

    Optional dict used to specify keywords for this component.

    Use `{"Keyword": None}` for keywords that do not have a value

    ### Valid Projection keywords
    - Internal – Specifies whether this projection definition is internal (not displayed in the class documentation).
    Note that the class documentation does not currently display projections at all.
    """ 

    def get_template(self) -> str:
        return "projection.cls.jinja"


@dataclass
class MethodArgument:
    """
    [Specifying Method Arguments](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GOBJ_methods#GOBJ_methods_arguments)

    Used to specify method arguments in the `Method` or `Query` component.
    """

    name: str
    """
    Name of the method argument
    """

    type: str | None = None
    """
    Optional type of the method argument
    """
    
    value: Any | None = None
    """
    Optional default value or expression
    """

    prefix: str | None = None
    """
    [Passing ByRef or Output Arguments](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GCOS_invoking#GCOS_invoking_byref)
    
    Optional prefix `ByRef` or `Output`
    """


@dataclass
class Method(Component):
    """
    [Defining Methods](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GOBJ_methods)

    ```
    Method Name(Arguments...) as ReturnType [ Keywords ]
    {
        Implementation
    }
    ```
    """

    arguments: list[MethodArgument] = field(default_factory=list)
    """
    List of `MethodArgument`

    ### Usage example

    ```
    method.arguments = [
        MethodArgument(
            "foo",
            type="%String",
            value=""
        ),
        MethodArgument(
            "bar",
            type="%Integer",
            value=1
            prefix="ByRef",
        ),
    ]
    ```
    """
    
    return_type: str | None = None
    """
    Optional class name used as return type
    """


    is_classmethod: bool = False
    """
    Optional boolean if Method should be a ClassMethod.

    Usage of the `ClassMethod` class is prefered instead.
    """

    impl: str | list[str] = field(default_factory=list)
    """
    Method implementation
    
    Can be a simple string for already indented and newline delimited code, or for use with `CodeMode = expression`
    or a list of strings for multiline code, in which case will be indented automatically by the generator.

    Objectscript routine code generation and syntax validation is not supported by this library.
    """

    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    [Method Syntax and Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_method)

    Optional dict used to specify keywords for this component.

    Use `{"Keyword": None}` for keywords that do not have a value

    ### Valid Method keywords
    - Abstract – Specifies whether this is an abstract method.
    - ClientName – Overrides the default name for the method in client projections.
    - CodeMode – Specifies how this method is implemented.
    - Deprecated – Specifies that this method is deprecated. This keyword is ignored by the class compiler and merely provides a human-readable indicator that the method is deprecated.
    - ExternalProcName – Specifies the name of this method when it is used as a stored procedure in a foreign database. Applies only if the method is projected as a stored procedure.
    - Final – Specifies whether this method is final (cannot be overridden in subclasses).
    - ForceGenerate – Specifies whether the method should be compiled in every subclass. Applies only if the method is a method generator.
    - GenerateAfter – Specifies when to generate this method. Applies only if the method is a method generator.
    - Internal – Specifies whether this method definition is internal (not displayed in the class documentation).
    - Language – Specifies the language used to implement this method.
    - NotInheritable – Specifies whether this method can be inherited in subclasses.
    - PlaceAfter – Specifies the order of this method, relative to other methods, in the routine that is generated for the class.
    - Private – Specifies whether this method is private (can be invoked only by methods of this class or its subclasses).
    - ProcedureBlock – Specifies whether this method is a procedure block. Applies only if the method is written in ObjectScript.
    - PublicList – Specifies the public variables for this method. Applies only if the method is written in ObjectScript and is a procedure block.
    - Requires – Specifies a list of privileges a user or process must have to call this method.
    - ReturnResultsets – Specifies whether this method returns result sets (so that ODBC and JDBC clients can retrieve them).
    - ServerOnly – Specifies whether this method will be projected to a Java client.
    - SoapAction – Specifies the SOAP action to use in the HTTP header when invoking this method as a web method via HTTP. Applies only in a class that is defined as a web service or web client.
    - SoapBindingStyle – Specifies the binding style or SOAP invocation mechanism used by this method, when it is used as a web method. Applies only in a class that is defined as a web service or web client.
    - SoapBodyUse – Specifies the encoding used by the inputs and outputs of this method, when it is used as a web method. Applies only in a class that is defined as a web service or web client.
    - SoapMessageName – Specifies the name attribute of the <part> element of the response message for this web method. Applies only in a class that is defined as a web service or web client.
    - SoapNameSpace – Specifies the XML namespace used by a web method. Applies only in a class that is defined as a web service or web client.
    - SoapRequestMessage – Use this when multiple web methods have the same SoapAction. This keyword specifies the name of the top element in the SOAP body of the request message, in the default scenario. Applies only in a class that is defined as a web service or web client.
    - SoapTypeNameSpace – Specifies the XML namespace for the types used by this web method. Applies only in a class that is defined as a web service or web client.
    - SqlName – Overrides the default name of the projected SQL stored procedure. Applies only if this method is projected as an SQL stored procedure.
    - SqlProc – Specifies whether the method can be invoked as an SQL stored procedure. Only class methods (not instance methods) can be called as SQL stored procedures.
    - WebMethod – Specifies whether this method is a web method. Applies only in a class that is defined as a web service or web client.
    """

    def get_template(self) -> str:
        return "method.cls.jinja"


@dataclass
class ClassMethod(Method):
    """
    [Defining Methods](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GOBJ_methods)

    ```
    ClassMethod Name(Arguments...) as ReturnType [ Keywords ]
    {
        Implementation
    }
    ```
    """

    is_classmethod: bool = field(init=False, default=True)


@dataclass
class Query(Component):
    """
    [Defining and Using Class Queries](https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=GOBJ_queries)

    ```
    Query Name(Arguments...) as %SQLQuery [ Keywords ]
    {
        Implementation
    }
    ```
    """

    arguments: list[MethodArgument] = field(default_factory=list)
    """
    List of `MethodArgument`

    ### Usage example

    ```
    query.arguments = [
        MethodArgument(
            "foo",
            type="%String",
            value=""
        ),
        MethodArgument(
            "bar",
            type="%Integer",
            value=1
        ),
    ]
    ```
    """
    
    return_type: str = "%SQLQuery"
    """
    Class name used as return type

    Should be `%SQLQuery` in most cases
    """

    impl: str | list[str] = field(default_factory=list)
    """
    Query implementation
    
    Can be a simple string for already indented and newline delimited code, or for use with `CodeMode = expression`
    or a list of strings for multiline code, in which case will be indented automatically by the generator.

    Note:
        SQL query generation and syntax validation is not supported by this library.
    """

    keywords: dict[str, Any] = field(default_factory=lambda: {"SqlProc": None}, kw_only=True)
    """
    [Query Syntax and Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_query)

    Optional dict used to specify keywords for this component.

    `SqlProc` is enabled by default for Queries

    Use `{"Keyword": None}` for keywords that do not have a value

    ### Valid Query keywords
    - ClientName – An alias used by client projections of this query.
    - Final – Specifies whether this query is final (cannot be overridden in subclasses).
    - Internal – Specifies whether this query definition is internal (not displayed in the class documentation).
    - Private – Specifies whether the query is private.
    - Requires – Specifies a list of privileges a user or process must have to call this query.
    - SoapBindingStyle – Specifies the binding style or SOAP invocation mechanism used by this query, when it is used as a web method. Applies only in a class that is defined as a web service or web client.
    - SoapBodyUse – Specifies the encoding used by the inputs and outputs of this query, when it is used as a web method. Applies only in a class that is defined as a web service or web client.
    - SoapNameSpace – Specifies the namespace at the binding operation level in the WSDL for this query. Applies only in a class that is defined as a web service or web client.
    - SqlName – Overrides the default name of the projected SQL stored procedure. Applies only if this query is projected as an SQL stored procedure.
    - SqlProc – Specifies whether the query can be invoked as an SQL stored procedure.
    - SqlView – Specifies whether to project this query as an SQL view.
    - SqlViewName – Overrides the default name of the projected SQL view. Applies only if this query is projected as an SQL view.
    - WebMethod – Specifies whether this query is a web method. Applies only in a class that is defined as a web service or web client.
    """

    def get_template(self) -> str:
        return "query.cls.jinja"


@dataclass
class Class(Component):
    """
    [Defining Classes](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=GOBJ_classes)

    ### Example usage
    ```
    from pyobjectscript_gen.cls import *

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
    # generate on sys.stdout
    cls.generate()
    ```

    ### Example output

    ```
    Class Demo.MyExample.MyClass Extends %RegisteredObject
    {

    Property Property1 As %String;

    Property Property2 As %Numeric;

    Method MyMethod() As %String
    {
        set returnvalue=..Property1_..Property2
        quit returnvalue
    }

    }
    ```
    """

    extends: list[str] = field(default_factory=list)
    """
    List of class names that this class extends from, in ascending order from left to right
    """


    components: list[Component] = field(default_factory=list)
    """
    List of Objectscript components to be generated in ascending order from top to bottom inside this `Class`

    Components can be any of the following classes:

    - [Parameter][]
    - [Property][]
    - [Method][]
    - [ClassMethod][]
    - [Query][]
    - [Trigger][]
    - [Projection][]
    - [ForeignKey][]
    - [Index][]
    - [XData][]
    - [Storage][]

    Note:
        - [Class][] itself is also a [Component][] but cannot be generated inside another [Class][].
        - Base class [Component][] should not be used directly.
    """


    keywords: dict[str, Any] = field(default_factory=dict, kw_only=True)
    """
    [Top Level Class Syntax and Keywords](https://docs.intersystems.com/irislatest/csp/docbook/Doc.View.cls?KEY=ROBJ_parameter)
    
    Optional dict used to specify keywords for this component.

    Use `{"Keyword": None}` for keywords that do not have a value

    ### Valid Class keywords
    - Abstract – Specifies whether this is an abstract class.
    - ClassType – Specifies the type (or behavior) of this class.
    - ClientDataType – Specifies the client data type used when this data type is projected to client technologies. Applies only to data type classes.
    - ClientName – Enables you to override the default class name used in client projections of this class.
    - CompileAfter – Specifies that this class should be compiled after other (specified) classes. In contrast to DependsOn, this keyword does not require the other classes to be runnable.
    - DdlAllowed – Specifies whether DDL statements can be used to alter or delete the class definition. Applies only to persistent classes.
    - DependsOn – Specifies that this class should be compiled after the compiler has made other (specified) classes runnable.
    - Deprecated – Specifies that this class is deprecated. This keyword is ignored by the class compiler and merely provides a human-readable indicator that the class is deprecated.
    - Final – Specifies whether this class is final (cannot have subclasses).
    - GeneratedBy – Indicates that this class was generated by code in another class and thus should not be edited.
    - Hidden – Specifies whether this class is hidden (not listed in the class reference).
    - Inheritance – Specifies the inheritance order for the superclasses of this class.
    - Language – Specifies the default language used to implement methods for this class.
    - LegacyInstanceContext – Specifies whether instance methods in this class can use the now-obsolete %this variable.
    - NoExtent – Specifies whether the compiler is prevented from generating a storage definition and methods to save/load object from disk and to disk.
    - OdbcType – Specifies the type used when this data type is exposed via ODBC or JDBC. Every data type class must specify an ODBC type. This keyword applies only to data type classes.
    - Owner – Specifies the owner of this class and its corresponding table. Applies only to persistent classes.
    - ProcedureBlock – Specifies whether each ObjectScript method in this class is a procedure block by default.
    - PropertyClass – Adds property parameters to this class.
    - ServerOnly – Specifies whether this class is projected to Java clients.
    - Sharded – Specifies whether this class is sharded. Applies only to persistent classes in an environment containing a sharded cluster.
    - SoapBindingStyle – Specifies the binding style or SOAP invocation mechanism used by any web methods defined in this class. Applies only in a class that is defined as a web service or web client.
    - SoapBodyUse – Specifies the encoding for any web methods defined in this class. This keyword applies only to web service and web client classes.
    - SqlCategory – Specifies the type to use for calculations in SQL. Applies only to data type classes.
    - SqlRowIdName – Overrides the default SQL field name for the ID column for this class. Applies only to persistent classes.
    - SqlRowIdPrivate – Specifies whether the ID column for this class is a hidden field when projected to ODBC and JDBC. Applies only to persistent classes.
    - SqlTableName – Specifies the name of the SQL table to which this class is projected. Applies only to persistent classes.
    - StorageStrategy – Specifies which storage definition controls persistence for this class. Applies only to persistent and serial classes.
    - System – Influences the compilation order for this class.
    - ViewQuery – Specifies the SQL query for this class. Applies only to view definition classes.
    """

    _TEMPLATE_DIR = Path(__file__).parent / 'templates/'

    _JINJA_ENV = jinja2.Environment(
        loader=jinja2.FileSystemLoader(_TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    def on_generate(self):
        if not "GeneratedBy" in self.keywords:
            self.keywords["GeneratedBy"] = "pyobjectscript_gen"
        elif self.keywords["GeneratedBy"] is None:
            self.keywords.pop("GeneratedBy")
        if self.doc_string is not None and len(self.doc_string) == 0:
            self.doc_string = [f"Class generated on {datetime.now().isoformat(sep=" ", timespec="seconds")}"]
        return super().on_generate()

    def get_template(self) -> str:
        return "class.cls.jinja"
    
    def generate(self, output: TextIO = sys.stdout):
        """
        Generates the current class to the specified IO or file (defaults to standard output)

        Example usage:
        ```
        # generates class into a file, make sure to add "w" for write permissions
        with open("output.cls", "w") as file:
            cls.generate(file)
        ```
        """

        env = self._JINJA_ENV
        template = env.get_template("class.cls.jinja")
        for component in self.components:
            component.on_generate()
        self.on_generate()
        output.write(template.render(component=self))


__all__ = list(map(lambda e: e.__name__, [
    Class,
    Property,
    Parameter,
    Method,
    ClassMethod,
    Query,
    Index,
    ForeignKey,
    Projection,
    MethodArgument,
    Trigger,
    Storage,
    XData,
    Expression,
    Component
]))