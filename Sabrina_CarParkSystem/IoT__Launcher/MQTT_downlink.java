/** Encoder **/
 
var value = (msg.params.replace(/"/g,""));
var data = {value: value}
// Result object with encoded downlink payload
var result = {
 
    // downlink data content type: JSON, TEXT or BINARY (base64 format)
    contentType: "JSON",
 
    // downlink data
    data: JSON.stringify(data),
 
    // Optional metadata object presented in key/value format
    metadata: {
        topic: 'tb/mqtt-integration-guide/sensors/'+metadata['deviceName']+'/rx'
    }
 
};
 
return result;