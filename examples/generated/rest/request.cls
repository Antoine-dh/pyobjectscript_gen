/// Class generated on 2025-07-26 17:54:43
Class REST.Messages.AddPetRequest Extends (%Persistent, Ens.Request, %JSON.Adaptor) [ GeneratedBy = pyobjectscript_gen ]
{

Parameter RESPONSECLASSNAME = "Ens.Response";

Property status As %String;

Property id As %Integer;

Property ApiKey As %String;

Method InitParams(ByRef pRequest As %Net.HttpRequest)
{
    Do pRequest.SetParam("status", ..status)
}

Method InitHeaders(ByRef pRequest As %Net.HttpRequest)
{
    Do pRequest.SetHeader("ApiKey", ..ApiKey)
    Do pRequest.SetHeader("Content-Type", "application/json")
}

}
