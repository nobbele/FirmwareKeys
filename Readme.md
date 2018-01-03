type start('dl') to download new .db files
type start('anything other than dl') to load the .db file
start function will use a method above and spit out keys.json containing all the keys in the following format
>> {
>>     "iPhone3,1 13A45": {
>>         "rootfs": {
>>             "key": "da key",
>>             "iv": "da iv"
>>         }, etc
>>     }, etc
>> }
function returns a dictionary in the format above