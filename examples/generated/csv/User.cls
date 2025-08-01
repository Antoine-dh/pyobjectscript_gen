/// Class generated on 2025-08-01 20:16:10
Class Demo.CSV.User Extends (%Persistent) [ GeneratedBy = pyobjectscript_gen ]
{

Property Id As %Integer [ Required ];

Property Username As %String(MAXLEN=100);

Property FirstName As %String(MAXLEN=100);

Property LastName As %String(MAXLEN=100);

Property Email As %String(MAXLEN=320) [ Required ];

Property Phone As %String(MAXLEN=16);

Property PetId As %Integer;

}
