/** Decoder **/
 
// decode payload to string
var payloadStr = decodeToString(payload);
var data = JSON.parse(payloadStr);
var topicPattern = 'tb/mqtt-integration-guide/sensors/(.+)/value';
 
var deviceName =  metadata.topic.match(topicPattern)[1];
// decode payload to JSON
var deviceType = 'sensor';
 
// Result object with device attributes/telemetry data
var result = {
   deviceName: deviceName,
   deviceType: deviceType,
   attributes: {
       integrationName: metadata['integrationName'],
   },
   telemetry: {
       value: data.value,
   }
};
 
/** Helper functions **/
 
function decodeToString(payload) {
   return String.fromCharCode.apply(String, payload);
}
 
function decodeToJson(payload) {
   // convert payload to string.
   var str = decodeToString(payload);
 
   // parse string to JSON
   var data = JSON.parse(str);
   return data;
}
 
return result;