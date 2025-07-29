# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-10-10 10:00:12
import binascii
import json


def parse_content_type(content_type):
    """
    解析内容类型，例如：main_type/sub_type; parameter1=value1; parameter2=value2; ...
    文本类型：
        text/html：表示 HTML 网页文档。浏览器在接收到这种类型的内容后，会将其解析为网页进行显示。
        text/css：层叠样式表文件，用于定义网页的样式。
        text/javascript：JavaScript 脚本文件，可在浏览器中执行以实现交互和动态效果。
        text/plain：纯文本内容，没有特定的格式或标记。
    应用程序类型：
        application/json：以 JSON 格式表示的数据，常用于 Web API 返回数据或在前后端分离的架构中进行数据交换。
        application/xml：XML 格式的数据，在一些传统的系统或特定场景下仍有使用。
        application/pdf：PDF 文档，可被 PDF 阅读器打开。
        application/zip：压缩文件格式，通常用于传输多个文件或减少文件大小。
    图像类型：
        image/jpeg：JPEG 格式的图像，广泛用于照片和图像的存储和传输。
        image/png：PNG 格式图像，支持透明背景和更高质量的图像显示。
        image/gif：GIF 图像，可以包含动画效果。
    音频类型：
        audio/mpeg：MP3 音频格式，是一种常见的数字音频压缩格式。
        audio/wav：WAV 格式音频，通常用于高质量的音频录制和播放。
    视频类型：
        video/mp4：MP4 视频格式，广泛用于在线视频播放和存储。
        video/webm：WebM 格式视频，是一种开放的视频格式，适用于网络播放。
    :param content_type:
    :return:
    """
    result = {}
    if content_type is None:
        return result
    strs = content_type.split(';')
    try:
        result['maintype'] = strs[0].split('/')[0]
        result['subtype'] = strs[0].split('/')[1]
    except TypeError as e:
        pass
    if len(strs) > 1:
        params = strs[1].split(';')
        for param in params:
            try:
                param_parse = param.split('=')
                result[param_parse[0]] = param_parse[1]
            except TypeError as e:
                pass
    return result


def parse_response(response):
    base_response = {
        'code': -1,
        'msg': '',
        'data': None,
    }
    if response is None:
        return base_response
    if response.status_code != 200:
        # http 错误码
        base_response['code'] = response.status_code
        return base_response
    else:
        # 企业微信 错误码：0为成功
        # 为了和http统一错误码，转换为200
        try:
            if response.json()['errcode'] == 0:
                base_response['code'] = 200
            else:
                base_response['code'] = response.json()['errcode']
            base_response['msg'] = response.json()['errmsg']
            # base_response['data'] =
        except (KeyError, TypeError) as e:
            pass
        return base_response


def format_response(response):
    if response is None:
        return ''
    response_str = f"response:\n"
    response_str += f"Status Code: {response.status_code}\n"
    response_str += f"Headers:\n"
    for key, value in response.headers.items():
        response_str += f"\t{key}: {value}\n"

    response_str += f"Body:\n"
    content_type = parse_content_type(response.headers.get('Content-Type'))
    main_type = content_type.get('maintype', 'text')
    sub_type = content_type.get('subtype', 'plain')
    if sub_type == 'json':
        # json较为常用，输出json格式字符串方便查看
        response_str += f"{json.dumps(response.json(), ensure_ascii=False, indent=4)}\n"
    elif sub_type == 'html' or sub_type == 'css' or sub_type == 'javascript' or sub_type == 'plain' or sub_type == 'xml':
        # 文本
        response_str += f"{response.text()}\n"
    else:
        # 二进制，输出前几个字节的16进制字符，以便识别特征
        response_str += binascii.hexlify(response.content[:5]).decode()

    return response_str
