# -*- coding: utf-8 -*-
import copy
import http.client
import json
import time
import requests
itamheaders = {
    'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InYyIiwidHlwIjoiSldUIn0.eyJleHAiOjE3NDI1NDYyMTcsImp0aSI6ImJKMk9hV0dkanU5QStMMXciLCJpYXQiOjE3NDEyNTAyMTcsImlzcyI6InRhbm5hIiwic3ViIjoiMzgzMDMxOUBieXRlZGFuY2UucGVvcGxlIiwidGVuYW50X2lkIjoiYnl0ZWRhbmNlLnBlb3BsZSIsInRlbmFudF9uYW1lIjoiIiwicHJvamVjdF9rZXkiOiJjcm1TZmdIVmU1dXhIMHJyIiwidW5pdCI6ImV1X25jIiwiYXV0aF9ieSI6Mn0.eHghtX4NOnD1uD65bzqv7n1J3mtnPPXJoVKIWDwl4PMZPkqc3FisH4RMXxDqeOyDCgRHYhmam7VEenl8T0UIKpzI8ad8yMiZytvAkNhclLjCdmokLB7DdwnbO1qeDLxdqjL-S3da0KHHkOT8j-rWR94XJ0N7T_snoko4Ovsp13w',
    'Content-Type': 'application/json'

}


class webapiClient():
    def __init__(self, clientin):
        """
       初始化 Client 实例,tenant_access_token 会在 Client 初始化时自动获取
        """
        headers = {
            'cookie': clientin['cookie'],
            'x-kunlun-token': clientin['x-kunlun-token'],
            'Content-Type': "application/json"}
        self.headers = headers
        self.itamheaders = headers
        self.conn = http.client.HTTPSConnection("apaas.feishu.cn")

    def get_intent_detail_list(self, startAt, pageSize):
        """
        outdata:
            对话ID 技能分发 用户输入
           res_ = {
          'intentID': 7485259579248705537,
          'userInput': "我要申请一个鼠标",
          'skillLabels': ["GUI 设备/配件申请"],
           'apply_day':"",
          'apply_num':"",
          'asset_name':"",
          'device_type':""
           }
        """
        # 输入参数类型和范围检查
        if not isinstance(startAt, int) or startAt < 0:
            raise ValueError("startAt 必须是一个非负整数")
        if not isinstance(pageSize, int) or pageSize < 0:
            raise ValueError("pageSize 必须是一个非负整数")

        endAt = int(time.time())
        payload = json.dumps({
            "startAt": startAt,
            "endAt": endAt,
            "matchIntentID": "",
            "matchStatus": [],
            "pageSize": pageSize + 10
        })
        try:
            self.conn.request("POST",
                              "/ai/api/v1/conversational_runtime/namespaces/spring_f17d05d924__c/stats/intent_detail_list",
                              payload, self.headers)
            res = self.conn.getresponse()

            # 检查响应状态码
            if res.status != 200:
                raise http.client.HTTPException(f"请求失败，状态码: {res.status}, 原因: {res.reason}")

            data = res.read()
            try:
                data = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                raise ValueError("无法将响应数据解析为 JSON 格式")

            # 检查响应数据结构
            if 'data' not in data or 'intentDetailList' not in data['data']:
                raise ValueError("响应数据缺少必要的字段 'data' 或 'intentDetailList'")

            res_list = []
            for i in data['data']['intentDetailList']:
                if i['channelType'] in ["LARK_OPEN_API", "LARK_BOT", "ANONYMOUS_CUI_SDK", "AILY_CUI_SDK"]:
                    res_list.append({
                        '对话日志/intentID': i['intentID'],
                        '用户输入/userInput': i['userInput'],
                        '数据是否有效/isdatavalid': "是",
                        '语言/language': "zh",
                        '是否 IT 问题/isITproblem': "是",
                        '业务场景/businessscenario': "NULL",
                        '分发技能/skill': i['skillLabels'],
                        '型号关键字词/asset_name': "NULL",
                        '型号类型/device_type': "NULL",
                        '匹配型号/AssetNamelist': "NULL",
                    })
            return res_list
        except http.client.HTTPException as http_err:
            print(f"HTTP 请求错误: {http_err}")
            return []
        except ValueError as value_err:
            print(f"值错误: {value_err}")
            return []
        except Exception as general_err:
            print(f"发生未知错误: {general_err}")
            return []

    def get_intent_detail_llm(self, res_list):
        """
        提取关键词：
        槽位提取：'apply_day': "",'apply_num': "",'asset_name': "",'device_type': ""
        表头字段：
        '对话日志/intentID': 7485264011232886786,
        '用户输入/userInput': "我要申请一个鼠标",
        '数据是否有效/isdatavalid': "是",
        '语言/language': "zh",
        '是否 IT 问题/isITproblem': "是",
        '业务场景/businessscenario': "NULL",
        '分发技能/skill': "NULL",
        '型号关键字词/asset_name': "NULL", #显示器
        '型号类型/device_type': "NULL",    # 设备 配件 软件
        '匹配型号/AssetNamelist': "NULL",
        """
        ii0 = []
        ii = {
            '对话日志/intentID': "7485264011232886786",
            '用户输入/userInput': "我要申请一个鼠标",
            '数据是否有效/isdatavalid': "是",
            '语言/language': "zh",
            '是否 IT 问题/isITproblem': "是",
            '业务场景/businessscenario': "NULL",
            '分发技能/skill': "NULL",
            '型号关键字词/asset_name': "NULL",  # 显示器
            '型号类型/device_type': "NULL",  # 设备 配件 软件
            '匹配型号/AssetNamelist': "NULL",
        }
        try:
            # 检查 res_list 是否为空
            if not res_list:
                print("输入的 res_list 为空")
                return []

            payload = ''
            for i in res_list:
                # intentID = i['对话日志/intentID']
                print("urlintentID_1:" + str(i))
                ii['对话日志/intentID'] = i
                intentID = str(i)
                urlintentID = f'https://apaas.feishu.cn/ai/api/v1/conversational_runtime/namespaces/spring_f17d05d924__c/intent/{intentID}?pageSize=20&statusFilter=%5B%5D&fieldFilter=_node_id&fieldFilter=status&fieldFilter=usages&fieldFilter=_node_name&fieldFilter=_node_type&fieldFilter=title_for_maker&fieldFilter=associate_id'
                response = requests.request("GET", urlintentID, headers=self.headers, data=payload)
                # sleep 3s
                # 检查响应状态码
                response.raise_for_status()

                try:
                    response = response.json()
                except json.JSONDecodeError:
                    print(f"无法解析来自 {urlintentID} 的响应为 JSON 格式")
                    continue

                # 检查响应数据结构
                if 'data' not in response or 'steps' not in response['data']:
                    print(f"来自 {urlintentID} 的响应缺少必要的字段 'data' 或 'steps'")
                    continue

                for j in response['data']['steps']:
                    if j['titleForMaker'] in ["槽位抽取", "LLM 2", "LLM"]:
                        nodeid = j['nodeID']
                        urlnodeid = f'https://apaas.feishu.cn/ai/api/v1/conversational_runtime/namespaces/spring_f17d05d924__c/association/{intentID}/node/{nodeid}?intentID={intentID}'
                        response_nodeid = requests.request("GET", urlnodeid, headers=self.headers, data=payload)
                        time.sleep(1)
                        # 检查响应状态码
                        response_nodeid.raise_for_status()
                        try:
                            data_nodeid = response_nodeid.json()
                        except json.JSONDecodeError:
                            print(f"无法解析来自 {urlnodeid} 的响应为 JSON 格式")
                            continue

                        # 检查响应数据结构
                        if 'data' not in data_nodeid or 'step' not in data_nodeid['data'] or 'output' not in \
                                data_nodeid['data']['step']:
                            print(f"来自 {urlnodeid} 的响应缺少必要的字段 'data'、'step' 或 'output'")
                            continue

                        if not data_nodeid['data']['step']['output']:
                            ii['型号关键字词/asset_name'] = 'NULL'
                            ii['型号类型/device_type'] = 'NULL'
                        else:
                            nodeid_output = json.loads(data_nodeid['data']['step']['output'])
                            if nodeid_output is not None and nodeid_output.get('response') is not None:
                                # 判断是否为 json 格式
                                if not isinstance(nodeid_output['response'], dict):
                                    try:
                                        nodeid_output['response'] = json.loads(nodeid_output['response'])
                                    except json.JSONDecodeError:
                                        print(f"无法解析 {urlnodeid} 响应中的 'response' 字段为 JSON 格式")
                                        continue
                                ii['型号关键字词/asset_name'] = nodeid_output['response'].get('asset_name', 'NULL')
                                ii['型号类型/device_type'] = nodeid_output['response'].get('device_type', 'NULL')
                            else:
                                ii['型号关键字词/asset_name'] = 'NULL'
                                ii['型号类型/device_type'] = 'NULL'

                        ii0.append(copy.deepcopy(ii))
            # 对res_list中的用户输入/userInput去重

            return ii0
        except requests.RequestException as req_err:
            print(f"请求错误: {req_err}")
            return []
        except Exception as general_err:
            print(f"发生未知错误: {general_err}")
            return []

    def get_bestmatchitemforreturn(self, keyword):
        """
        mock数据，获取最佳匹配的sku/spu
        mock数据：公用配件列表、设备列表、软件列表
        todo：mock数据表格为飞书文档或者其他？
        """
        _urlGetBestMatchItemForReturn = "https://asset-mig-pre.bytedance.net/aily/api/itservice/ai/GetBestMatchItemForReturn"

        payload = json.dumps({
            "SearchKey": keyword,
            "AiUseType": 1,
            "ListReturnableAccessoryRequest": {
                "IsAll": True,
                "Page": {
                    "PageNum": 1,
                    "PageSize": 30
                },
                "OwnerUserID": "",
                "AccessoryApplyTypeList": []
            },
            "GetAssetListRequest": {
                "Status": 6,
                "Search": "",
                "IsAll": True,
                "SubStatusList": [
                    12,
                    18,
                    19
                ],
                "Page": {
                    "PageNum": 1,
                    "PageSize": 30
                },
                "OrganizationalUnitID": 1
            }
        })
        response = requests.request("GET", _urlGetBestMatchItemForReturn, headers=self.headers, data=payload)
        response = json.loads(response.text)

    def get_segsearchcandidates(self, res_list):
        # 获取分数值
        ### 读取设备&配件的信息并拼接到text里面
        ### 遍历res_list中的device_name
        ###判断是否在asset.json里面
        ###调用算法接口获取设备&配件的分数值
        pass



