# Generic API POC

> Language - Python 3.8

> Dependency - pandas, requests, jsonpath_ng

### About Generic api
Through this Generic API, basic parameters of API like URL, Payload, response, content type etc can be configured and processed dynamically.
	
### Function Exposed by Generic api
The method that is being exposed in this package is `invoke()`. This particular method will return an object or any specific type (ex string, bool) based on the configuration. The inputs for the API are given below
	
- Module (string) - Module name or type.
- Condition (string) - Condition of the rules.
- Attributes (object) - Required for substitution.

### API Configuration 
The module & condition is mandatory properties, which is completely responsible for the structure of request and response. This above configuration is generic, hence the configuration can be designed and implemented based on the module funcionality and its requirement.

Below is configuration used for poc:
```SH
[
  {
    "module": "documents",
    "url": "https://ksydbcpmq7.execute-api.eu-west-2.amazonaws.com/api/documents",
    "queries": [
      {
        "condition": "checkPatientMatch",
        "uri": "patientMatch",
        "requiredAttributes": [
          "name"
        ],
        "methodType": "post",
        "contentType": "application/json",
        "requestBody": {
          "name": "$name"
        },
        "response": {
          "code": 200,
          "jsonPath": "result"
        }
      }
    ]
  },
  {
    "module": "clint",
    "url": "https://ksydbcpmq7.execute-api.eu-west-2.amazonaws.com/api/clint",
    "queries": [
      {
        "condition": "queryName/Ern",
        "uri": "execute",
        "requiredAttributes": [
          "queryErn"
        ],
        "methodType": "post",
        "contentType": "application/json",
        "requestBody": {
          "queryErn": "$queryErn"
        },
        "response": {
          "code": 200,
          "jsonPath": "result"
        }
      }
    ]
  }
]
```

### Property details
- `module` - Name of the type or module.
- `url` - Base url (should not end with **/**)
- `queries` - Specific to endpoint config.
	- `condition` - Name of the condition.
	- `uri` - actual API route path for the condtion. should not start with **/**
	- `requiredAttributes` - Requierd properties for query config value substitution.
	- `methodType` - API action GET, POST, PUT, PATCH etc.
	- `contentType` - Request content-type.
	- `requestBody` - By giving the Json node value in response attribute. The response data from the api is segreagated from the json path based the Json node value. For reference check the below links.
	- `Response` - Consumer can get the specific data from the response by configuring the jsonPath
		 
### Substitution
The dynamic values are being used in the query configuration as "$property_Name". It takes the key value pair and matches the "$property_Name" with keys and substitutes the corresponding value to the json attribute. 
	
### Links 
JsonPath - https://github.com/h2non/jsonpath-ng

POC Idea reference -  https://docs.coveo.com/en/3131/cloud-v2-administrators/generic-rest-api-source-concepts
