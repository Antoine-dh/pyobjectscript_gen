/// Class generated on 2025-07-26 17:54:43
Class REST.BusinessOperation Extends (Ens.BusinessOperation, REST.HttpMethods) [ GeneratedBy = pyobjectscript_gen ]
{

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
