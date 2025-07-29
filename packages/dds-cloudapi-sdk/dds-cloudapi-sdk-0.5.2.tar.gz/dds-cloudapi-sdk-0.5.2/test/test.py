import base64

from flask import Flask

import dds_cloudapi_sdk

app = Flask(__name__)

from dds_cloudapi_sdk import Client
from dds_cloudapi_sdk import Config
from dds_cloudapi_sdk.tasks.v2_task import V2Task

token = "Your API Token Here"
config = Config("d7a64888e7c569a706a638ba8a8e7b09")
config.endpoint = "apitest.deepdataspace.com"
infer_image = "/Users/lizhiqiang/project/dds-cloudapi-sdk/04_b.jpg"
infer_image = "data:image/jpeg;base64," + base64.b64encode(open(infer_image, "rb").read()).decode("utf-8")
prompt_image = "/Users/lizhiqiang/project/dds-cloudapi-sdk/04_b.jpg"
prompt_image = "data:image/jpeg;base64," + base64.b64encode(open(prompt_image, "rb").read()).decode("utf-8")

body = {
    "image": infer_image,
    "prompt": {
        "type": "visual_images",
        "embedding":"W3siY2F0ZWdvcnlfaWQiOiAwLCAiZW1iZWRkaW5nIjogIjBQTzh2UW5aT0w2OVcvby93Z3dsUGhobUJiNWozNWM5am9hY1B2SGNFNzZaN2xxK1JFZTZ2VDliNWI3cXhvWThkTG80UGJXSHZUMFI2MFcrMXhuZ1BXL3c5cng2N1JtKzJQRk92UjFhQno5N1RNYzlNMkVldlhlTjg3MTNCTWkrU1Z1VFBpaWJZcjVrZDRVK21xV052WGlITGI0SWZ0YzlkVVFydnVJS2hiMzdDWUkrY2tReXZyQTRoNzNUSzRlK0pOcWFQUlhXd3oxWm9Pcy93Ym5XUEZXaXlqMGd1aWkrWHI0b3ZpcjE1cjRJNG1ROVFXdFB2dDA2d2p4bW1qNi9STGhRUHFwM0RMNHlURkcrdFJvQXZuTVByRDNTb0dtK0tIV2JQVGN4NkQyRGdhbSswYVdEdmc2U0FyNzRFQ3UrT3JvWlA2RVlNejQxK3FTOGk2V1J2ckJleEwyUzFYcytBbEdtdllLNXo3NG1rRlUrNHBRbVBxbDNBci9EM1Z5K0o4SEVQZWNkTDc0ZDNpNitqUHgxUHZ6NGV6MGI2KzQrdXVnWVBqcjd4cjJBaVNVK1d1cVVQaUw0Uzcyb3FuazdKT1NwUEFQelc3MURidWk5bzNLNVBobHdpNzB6NXFBOW9ZekF2bWF0Z2p5eVBWbTlYbUlzUHpRSXJqeFFQTGk5WFE3RXZLUDduajczUjYrOTBjODFQaWZJbUw3eG1sTStKVENXdlhDY0FEOGF4Q2s5dm1yS080ek1ZejdaTDlFK0N1cUZ2aFVoT1Q0NStFKytSMnZGdnJFUXliMjl5MEcrbVpkSFByWGRyajcrQ1hHOVdBTGVQT1Z1aHo1d2JqYStzYnNEUGYrTkViNEpoM0srTzd1S3ZnVUc5ajN0VmpJK0xsVEJ2WG5Yb2owc0FMbSs0NVVmdlFOcmxiMDFNUUcrMEdMTnZqSU42anBRWFlJL090Q0pQdW92TTc1QUtBKy9HTkFEUGsrL1pEK3U1RHU3OXphbHZzaytETDY3dnYrOFVXdEtQWjFoNzBDQXFrWEJqM3FndldQRElUMmxUdVU5RExrd1BWMVNoVDA0QVo2OEk3RXJQMmNJUmI0U2hLSStMTXQzUHJPMnlUelJQMlc5STdLbFB1aWxuRDFLQ1h1OHowMXp2Ung4anI3ei93dytnS3RhdXBBUC9yemJxb3krUHJ2bnZCNmlGNzdzNnBJK3g4Q01QS3BuZ0QweUFnQytVK25EdTNLejh6MWlkT0c5UG41NU9rdkVhejRtV1I0N1lCZFNQb2padWI1VU8ySzhab2tqdmplbnpqNExNMjYrZS9MWnZuM0FTajRVMDF3K0dlcFV2d2JtM3I0WUVSUzkySUQzUG43S2o3MzFJVGkrc1NzUXZsSEppcjdVeTQrK1NUcC9QWjY3NEQxaW10dTk2c0lmdmdYeGdUejBmNTI5MjFDSFBtdFlMNzUzeVJHOU4wSFZQWUZHSlQ0R1F3aStYZW40dWlDQ0pUNzJDSksvVS9acnZUV2VQNzFNTnJPOGNocDRQTEw1ZHozMlFOUytvWnNsUHEwZE9qM2JSd2c5MitMT3ZTaXNaTDVyZm55OXBBc0JQa1lrMEw1ZWNKZzlYY2pVdkF0aTV6dWFkeGUrbU1vaFB1eExGNzRuL2FxOTNDMGl2b0IvcVQySHRxRzkwbmNEdnVaQlA3NHF4Y2c4Qkhwd1BxNU4rVDNoTVU2OW9jTi92dkJjMmIyeTFucSs3ZlQ4dlhQa2pMMXJlTzIrZ2c5TFBydXY4NzM4cU80K21oSUl2dkd1SnI0cWkwVStBZ25RdkE9PSJ9XQ==",
        "visual_images": [
            {   
                "image": prompt_image,
                "interactions": [
                    {
                        "category_id":0,
                        "type": "rect",
                        "rect":[475.18413597733706, 550.1983002832861, 548.1019830028329, 599.915014164306]
                    }
                ]
            }
        ]
    },
    "targets":["bbox" ],
    "model":"T-Rex-1.0"
}
@app.route("/test1", methods=["GET", "POST"])
def test():
    raise Exception("test")
    task = V2Task("/v2/task/trex/detection", body)
    client = Client(config)
    client.run_task(task)
    return task.result

app.run(debug=True)
input("Press Enter to continue...")