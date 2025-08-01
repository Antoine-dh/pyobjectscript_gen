/// Class generated on 2025-08-01 18:45:28
Class REST.BusinessOperation Extends (Ens.BusinessOperation) [ GeneratedBy = pyobjectscript_gen ]
{

Method Get(pRequest, Output pResponse) As %Status
{
    $$$TRACE("Sending GET request...")
    Quit $$$OK
}

Method Post(pRequest, Output pResponse) As %Status
{
    $$$TRACE("Sending POST request...")
    Quit $$$OK
}

Method Delete(pRequest, Output pResponse) As %Status
{
    $$$TRACE("Sending DELETE request...")
    Quit $$$OK
}

Method Patch(pRequest, Output pResponse) As %Status
{
    $$$TRACE("Sending PATCH request...")
    Quit $$$OK
}

Method AddPet(pInput As REST.Messages.AddPetRequest, Output pOutput As REST.Messages.AddPetResponse) As %Status [ CodeMode = expression ]
{
..Post("/pet", pInput, .pOutput)
}

XData MessageMap
{
<MapItems>
  <MapItem MessageType="REST.Messages.AddPetRequest">
    <Method>AddPet</Method>
  </MapItem>
</MapItems>
}

}
