# encoding: utf-8
# desc: 企业微信的工具函数，由于部分接口权限要求较高，需要域名、备案、域名和企业微信主题一致等要求，
# 所以部分接口暂未实现：包括发送消息给微信（外部联系人）等
# auth: Kasper Jiang
# date: 2024-10-09 14:10:39
import logging

import requests

from . import requests_util, logging_util, json_util, str_util

TOKEN_URL = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
EXTERNAL_CONTACT_LIST_URL = 'https://qyapi.weixin.qq.com/cgi-bin/externalcontact/list'
WEBHOOK_URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send'


def get_access_token(corpid, corpsecret):
    """
    获取企业微信的授权码
    :param corpid: 企业微信的企业id
    :param corpsecret: 企业微信的应用密钥
    :return:
    """
    get_params = {
        'corpid': corpid,
        'corpsecret': corpsecret,
    }
    response = requests.get(TOKEN_URL, get_params)
    access_token = response.json()['access_token']
    return access_token


def get_external_contact_list(token):
    """
    获取外部联系人列表;
    注意：需要域名且备案，无法调试接口，未完全实现
    :param token:
    :return:
    """
    pass
    # get_params = {
    #     'access_token': token,
    # }
    # response = requests.get(EXTERNAL_CONTACT_LIST_URL, get_params)
    # external_userids = [contact['external_userid'] for contact in response.json()['external_userlist']]
    # return external_userids


def send_robot_webhook_msg(webhook_key, text=None, markdown=None, custom=None):
    """
    发送群机器人消息到企业微信群；
    优先级 text > markdown > custom，如果多个参数不为空，只发送最高优先级内容
    内容超过最大长度将发送失败
    参考企业微信官方文档：https://developer.work.weixin.qq.com/document/path/99110
    :param webhook_key: 群机器人的key值，可在企业微信群的设置里查看
    :param text: 以文本形式发送消息,最多2048个字节，大概1000个字符，utf8编码
    :param markdown: markdown内容， 最长不超过4096个字节，大概2000个字符，utf8编码
    :param custom: 以自定义格式发送消息，格式参考企业微信官方文档
    :return: http返回的错误码response code
    """
    if text:
        msg = {
            "msgtype": "text",
            "text": {
                "content": text
            }
        }
    elif markdown:
        msg = {
            "msgtype": "markdown",
            "markdown": {
                "content": markdown
            }
        }
    elif custom:
        msg = custom
    else:
        return {
            'code': 400,
            'msg': '',
            'data': None,
        }
    webhook_key_url = f'{WEBHOOK_URL}?key={webhook_key}'
    response = requests.post(webhook_key_url, json=msg)
    logging.debug(requests_util.format_response(response))
    base_response = requests_util.parse_response(response)
    return base_response


def test_get_access_token(config):
    token = get_access_token(config['corpid'], config['corpsecret'])
    assert (token is not None)


def test_external_contact_list(config):
    pass
    # token = get_access_token(config['corpid'], config['corpsecret'])
    # external_contact_list = get_external_contact_list(token)
    # assert (external_contact_list is not None)


def test_send_robot_webhook_msg(config):
    base_response = send_robot_webhook_msg(config['group_robot_webhook_key'], text='测试文本\n测试2')
    if base_response['code'] == 200:
        print("消息1发送成功")
    else:
        print(f"消息1发送失败，状态码：{base_response['code']}")
    assert (base_response['code'] == 200)

    # 最大4k字节，大概2k字符
    text = ''
    for i in range(1, 40):
        text = text + f'{i}. 2024美国7.1分战争动作《盟军敢死队/绝密型战》BD1080p.国英双语中字  张钧甯，吴镇宇\n'
    text = str_util.truncate_str_to_size(text, 4096)
    print(f'企业微信发送内容大小：{str_util.get_size(text)}')
    base_response = send_robot_webhook_msg(config['group_robot_webhook_key'], markdown=text)
    if base_response['code'] == 200:
        print("消息2发送成功")
    else:
        print(f"消息2发送失败:\n")
        logging.error(json_util.dumps(base_response))
    assert (base_response['code'] == 200)


if __name__ == '__main__':
    logging_util.init(logging.INFO)
    # test_config = {
    #     'corpid': '替换为你的企业id',
    #     'corpsecret': '替换为你的应用密钥',
    #     'group_robot_webhook_key': '替换为你的群机器人的webhook的key'
    # }
    test_config = {
        'group_robot_webhook_key': 'ce57445a-ba75-4e6c-9200-41687b1cfae5'
    }

    # test_get_access_token(test_config)
    # test_external_contact_list(test_config)
    test_send_robot_webhook_msg(test_config)
