# -*- coding: utf-8 -*-
import time
from it_assistant.ailyapp_client import AilyLarkClient
from it_assistant.lark_client import LarkdocsClient
from it_assistant.intent_detail import *
from it_assistant.openapi import *
import datetime
import copy
import os
import csv

import sys
# Add the directory containing config.py to the Python path
config_dir = os.path.dirname(os.path.abspath(__file__))  # Assume config.py is in the same directory
sys.path.insert(0, config_dir)

import config


def info_from(Clientinfox):
    """
    初始化 配置单例数据
    """
    config.Clientassign(Clientinfox)


# 定义一个全局变量Client
# Testsuitelink = "https://bytedance.larkoffice.com/sheets/ZVzfsw4rMhkMF6tjtxmc4BdSnMb"


def do_ai_auto(Testk_data):
    """
    自动化执行AI测试用例
    """
    startAt = 0
    try:
        # 获取租户访问令牌
        tenant_access_token = AilyLarkClient().get_tenant_access_token()
        if not tenant_access_token:
            raise ValueError("未能获取到有效的租户访问令牌")
        # 判断Testsuitelink中是否包含https://
        if "https://" in Testk_data:

            # 通过文档链接获取spreadsheet_token
            spreadsheet_token = Testk_data.split("/")[-1]
            if not spreadsheet_token:
                raise ValueError("未能从文档链接中提取到有效的spreadsheet_token")
            # 读取表格用户输入
            spreadsheet = LarkdocsClient().get_the_worksheet(spreadsheet_token)
            if not spreadsheet:
                raise ValueError("未能获取到有效的工作表数据")
            for i in spreadsheet.sheets:
                column_count = i.grid_properties.column_count
                row_count = i.grid_properties.row_count
                sheet_id = i.sheet_id
                title = i.title
                if title == "测试集":
                    # 构建JSON字符串
                    json_str = {"ranges": [sheet_id + "!A1:A" + str(row_count)]}
                    # 获取纯文本内容
                    test = LarkdocsClient().get_plaintextcontent(json_str, spreadsheet_token, sheet_id)
                    test = json.loads(test)
                    userinput = test['data']['value_ranges'][0]['values']
                    print(f"表头为{userinput[0]}")
                    for i in range(1, row_count):
                        if userinput[i][0]:
                            if startAt == 0:
                                startAt = int(time.time())
                            # 创建会话
                            seseion_id = AilyLarkClient().create_ailysession(tenant_access_token)
                            if not seseion_id:
                                raise ValueError("未能成功创建会话")
                            # 创建消息
                            message_id = AilyLarkClient().create_ailysessionaily_message(tenant_access_token,
                                                                                         seseion_id,
                                                                                         userinput[i][0])
                            if not message_id:
                                raise ValueError("未能成功创建消息")
                            # 创建运行实例
                            runs = AilyLarkClient().create_ailysession_run(tenant_access_token, seseion_id)
                            # 可不需等待运行实例创建完成
                            # if not runs:
                            #    raise ValueError("未能成功创建运行实例")
                            time.sleep(1)
                        else:
                            return startAt, i
                            break
                    return startAt, row_count
                    break
        elif Testk_data[0].get('ext'):
            num = 0
            for i in Testk_data:
                aa = i['ext']['input']
                if startAt == 0:
                    startAt = int(time.time())
                # 创建会话
                seseion_id = AilyLarkClient().create_ailysession(tenant_access_token)
                if not seseion_id:
                    raise ValueError("未能成功创建会话")
                # 创建消息
                message_id = AilyLarkClient().create_ailysessionaily_message(tenant_access_token, seseion_id, aa)
                if not message_id:
                    raise ValueError("未能成功创建消息")
                # 创建运行实例
                runs = AilyLarkClient().create_ailysession_run(tenant_access_token, seseion_id)
                num = num + 1
            return startAt, num
    except KeyError as ke:
        print(f"KeyError 发生: 数据中缺少必要的键，错误详情: {ke}")
        return None, None
    except json.JSONDecodeError as jde:
        print(f"JSON 解析错误: {jde}")
        return None, None
    except ValueError as ve:
        print(f"值错误: {ve}")
        return None, None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None, None


def get_conversationlogs1(startAt):
    """
    对话ID 技能分发 用户输入
    res_data = {
            'intentID': 7485259579248705537,
            'skillLabels': ["GUI 设备/配件申请"],
            'userInput': "我要申请一个鼠标",

         }
         """
    data = webapiClient().get_intent_detail_list(startAt)


def get_conversationlogs(startAt, pageSize=10):
    """
    对话ID 技能分发 用户输入
    res_data = {
            'intentID': 7485259579248705537,
            'skillLabels': ["GUI 设备/配件申请"],
            'userInput': "我要申请一个鼠标",

         }
    """
    try:
        # 之前提到形参 'pageSize' 未填，这里假设默认值为 10，你可按需修改
        data = webapiClient().get_intent_detail_list(startAt, pageSize=10)
        return data
    except KeyError as ke:
        print(f"KeyError 发生: 数据中缺少必要的键，错误详情: {ke}")
        return None
    except IndexError as ie:
        print(f"IndexError 发生: 索引超出范围，错误详情: {ie}")
        return None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None


def write_reslut(data, Testsuitelink, title):
    """
    写入表格
    """
    try:
        # 解析 spreadsheet_token
        spreadsheet_token = Testsuitelink.split("/")[-1]

        # 生成新工作表名称
        new_sheet_title = f"{title}{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        sheetinfo = {"index": 0, "title": new_sheet_title}

        # 创建新工作表
        spreadsheet0 = LarkdocsClient().createsheets(spreadsheet_token, sheetinfo)
        sheet_id = spreadsheet0['sheet_id']

        # 准备表头数据
        headers = list(data[0].keys())
        header_data = [
            {
                "range": f"{sheet_id}!{chr(ord('A') + col)}1:{chr(ord('A') + col)}1",
                "values": [[[{"text": {"text": header}, "type": "text"}]]]
            }
            for col, header in enumerate(headers)
        ]

        # 写入表头
        LarkdocsClient().writesheets(spreadsheet_token, sheet_id, {"value_ranges": header_data})

        # 写入数据
        for row, row_data in enumerate(data, start=1):
            row_values = [
                {
                    "range": f"{sheet_id}!{chr(ord('A') + col)}{row + 1}:{chr(ord('A') + col)}{row + 1}",
                    "values": [[[{"text": {"text": str(row_data[header])}, "type": "text"}]]]
                }
                for col, header in enumerate(headers)
            ]
            LarkdocsClient().writesheets(spreadsheet_token, sheet_id, {"value_ranges": row_values})

        return True
    except KeyError as ke:
        print(f"KeyError 发生: 数据中缺少必要的键，错误详情: {ke}")
        return False
    except IndexError as ie:
        print(f"IndexError 发生: 索引超出范围，错误详情: {ie}")
        return False
    except Exception as e:
        print(f"发生未知错误: {e}")
        return False


def write_excletolist(data_name):
    """
    1. 读取本地表格
    2. 将表格内容拼接为text
    """
    try:
        # 查看当前工作目录
        print(f"当前工作目录: {os.getcwd()}")
        # /Users/bytedance/it_assistant/it_assistant/accessory.csv
        # 构建文件路径
        file_path = f'data/{data_name}.csv'
        Candidates = []
        Candidate = {
            "Score": 0,
            "Text": "IOS手机",
            "Attrs": {"id": "", "type": ""}}
        text = ""
        with open(file_path, 'r', encoding='utf-8', newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)  # 读取表头
            for header in headers:
                text += f"{header}: "
            text = text.rstrip(': ') + '\n'

            for row in reader:
                textout = ""
                textout += ', '.join(row)
                Candidate['Text'] = textout
                Candidates.append(copy.deepcopy(Candidate))
        return Candidates
    except FileNotFoundError:
        print(f"未找到文件: {file_path}")
        return None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None


if __name__ == '__main__':
    cases = ""

    res, num = do_ai_auto(cases)
    print(res)
    print(num)
    get_query_vector
