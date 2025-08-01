/// Class generated on 2025-08-01 19:45:05
Class Demo.CSV.Store Extends (%Persistent) [ GeneratedBy = pyobjectscript_gen ]
{

Property Id As %Integer [ Required ];

Property Name As %String(MAXLEN=100);

Property Address As %String(MAXLEN=1024);

Property Latitude As %Numeric;

Property Longitude As %Numeric;

}
