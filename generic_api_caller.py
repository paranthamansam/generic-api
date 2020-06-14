import json
import pandas as pd
import logging
import requests
from jsonpath_ng import jsonpath, parse
import os


class generic_api:
    
    #private properties
    __config = ""

    #constructor
    def __init__(self, config):
        self.__config = config

    #Invoker call the api based on the configuration
    def invoke(self, module, condition, attirbutes):
        try:
            base_url = ""
            response = None

            # filter the specific config from collection
            # Module level filter
            df = pd.DataFrame.from_dict(self.__config)
            filtered_df = df[df.module == module].head(1)
            if len(filtered_df) > 0 :
                filtered_dict = filtered_df.to_dict(orient="records")

                base_url = filtered_dict[0]['url']
                
                # condition filter
                query_config_json = filtered_dict[0]['queries']
                q_df = pd.DataFrame.from_dict(query_config_json)
                query_df = q_df[q_df.condition == condition].head(1)
                if len(query_df) >0 :
                    query_dict = query_df.to_dict(orient="records")

                    # send out the query_config and attribute to subsitution
                    config = self.__substituter(query_dict[0], attirbutes)

                    #TODO: Make http call and return return required response
                    response = self.__http_call(base_url, config)

            return response
        except Exception as e:
            logging.error("Error from genericAPIinvoke (module - {} , condition - {} ): {}".format(module, condition, str(e)))
            raise e
    
    #required_validator return bool
    def __required_validator(self, required_fileds, attribute):
     try:
        for field in required_fileds:
            if field not in attribute.keys():
                return False
        return True
     except Exception as e:
         raise e

    #subsituter will replace the string with attirbute values
    def __substituter(self, config, attributes):
        try:
            #check the attribute is not empty
            if attributes is None or len(attributes) == 0:
                raise Exception('attribute is empty')

            #Valdiate reuired fields self.__required_validator()
            if not (self.__required_validator(config['requiredAttributes'], attributes)):
                raise Exception('required attribute is missing')
            
            # json to string
            json_string = json.dumps(config) 
            #loop over the attributes
            for key in attributes.keys():
                #replace the string '${}'.format(att.key), '"{}"'.format(att.value) &var
                json_string = json_string.replace('${}'.format(key),attributes[key])
            
            #convert to json
            config_json = json.loads(json_string)

            #return json
            return config_json
        except Exception as e:
            raise e

    def __http_call(self, base_url, query_config):
        try:
            
            if query_config['methodType'] is None or len(query_config['methodType']) == 0:
                raise Exception('method Type is missing')
            
            # setup url
            api_url =  "{}/{}".format(base_url,query_config['uri'])

            # setup headder
            content_type = "application/json"
            if len(query_config['contentType']) > 0 :
                content_type = query_config['contentType']

            headers = {}
            headers['content-type'] = content_type 

            # request body based on the methodType POST PUT PATCH make a call
            method_type = query_config['methodType']
            response = {}
            if method_type.casefold() == "POST".casefold():
                body = json.dumps(query_config['requestBody'])
                response = requests.post(api_url, data=body, headers = headers)
            elif method_type.casefold() == "PUT".casefold():
                body = json.dumps(query_config['requestBody'])
                response = requests.put(api_url, data=body, headers = headers)
            elif method_type.casefold() == "PATCH".casefold():
                body = json.dumps(query_config['requestBody'])
                response = requests.patch(api_url, data=body, headers = headers)
            elif method_type.casefold() == "GET".casefold():
                response = requests.get(api_url, headers = headers)
            
            # return error for 200 to 400 
            response.raise_for_status()

            # check the response is not None and check the expected status code
            response_data = None
            if len(response.content) > 0:
                if response.status_code == query_config['response']['code']:
                    if query_config['response']['jsonPath'] is not None and \
                            len(query_config['response']['jsonPath']):

                        jsonpath_expr = parse(query_config['response']['jsonPath'])
                        for match in jsonpath_expr.find(response.json()):
                            response_data = match.value

                    else:
                        response_data = response.json()

            return response_data
        except Exception as e:
            raise e

if __name__ == "__main__":
    module = "documents"
    condition = "checkPatientMatch"
    attributes1 = {
        "name" : "john"
    }
    attributes2 = {
        "name" : "sam"
    }
    
    module2 = "clint"
    condition2 = "queryName/Ern"
    attributes21 = {
        "queryErn":"test001"
    }


    with open("utils/config.json") as file:
        data = file.read()
        configJson = json.loads(data)    
        client = generic_api(configJson)
        out1 = client.invoke(module, condition, attributes1)
        out2 = client.invoke(module, condition, attributes2)
        print("Document trigger - check patient match api")
        print(f"Patient Name (john) : {out1}")
        print(f"Patient Name (sam) : {out2}")
        print("")
        out3 = client.invoke(module2, condition2, attributes21)
        print("Execute clint query api")
        print(f"QueryErn ({attributes21['queryErn']}) : {out3}")
