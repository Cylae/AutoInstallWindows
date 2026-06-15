
$json = '{"pinnedList":[]}';
if( [System.Environment]::OSVersion.Version.Build -lt 20000 ) {
	return;
}
$key = 'Registry::HKLM\SOFTWARE\Microsoft\PolicyManager\current\device\Start';

Set-RegistryKey -Path 'HKLM\SOFTWARE\Microsoft\PolicyManager\current\device\Start' -Name 'ConfigureStartPins' -Value $json -Type 'String'

