# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-10-08 18:40:30
import logging
import os.path
import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def create_email(smtp_server, from_addr, auth_code, port=25, debug_level=0):
    """
    创建smtp服务
    :param smtp_server:
    :param from_addr: 发送的邮箱地址，字符串
    :param auth_code: 授权码；现在邮箱服务器一般使用授权码而不是邮箱密码了，字符串
    :param port:
    :param debug_level: 1=开启打印；0=关闭打印
    :return:
    """
    server = smtplib.SMTP(smtp_server, port)  # SMTP协议默认端口是25
    server.set_debuglevel(debug_level)
    server.login(from_addr, auth_code)
    return server


def send_email(smtp_server, to_addr_list, title, content, content_type='plain', payload=None, payload_name=None):
    """
    通过smtp_server发送邮件，支持文本正文、网页正文、附件
    :param smtp_server:
    :param to_addr_list:
    :param title:
    :param content:
    :param content_type:
    :param payload:
    :param payload_name:
    :return:
    """
    if not smtp_server:
        logging.error(f'smtp_server is None')
        return False
    msg = MIMEMultipart()
    try:
        # 添加标题
        msg['Subject'] = Header(title, 'utf-8').encode()
        # 添加内容
        if content_type == 'html':
            msg.attach(MIMEText(content, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
        # 添加附件
        if payload:
            mime = MIMEBase('', '', filename=payload_name)
            mime.add_header('Content-Disposition', 'attachment', filename=payload_name)
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            mime.set_payload(payload)
            encoders.encode_base64(mime)
            msg.attach(mime)
        smtp_server.sendmail(smtp_server.user, to_addr_list, msg.as_string())
    except Exception as e:
        logging.error(f'failed to send email to {to_addr_list}: ' + e)
        return False
    return True


def quit_email(smtp_server):
    """
    释放smtp_server服务
    :param smtp_server:
    :return:
    """
    if not smtp_server:
        logging.error(f'smtp_server is None')
        return False
    smtp_server.quit()


def test_email1(config):
    server = create_email(config['smtp_server'], config['from_addr'], config['auth_code'])
    send_email(server, config['to_addr'], '测试邮件-文本', '测试内容')
    quit_email(server)


def test_email2(config):
    server = create_email(config['smtp_server'], config['from_addr'], config['auth_code'])
    send_email(server, config['to_addr'], '测试邮件-网页', '<html><body><h1>Hello</h1>' +
               '<p>send by <a href="http://www.python.org">Python</a>...</p> </body></html>', content_type='html')
    quit_email(server)


def test_email3(config):
    payload_name = 'test_payload.zip'
    payload_path = os.path.join('../../test/test_resource', payload_name)
    print(payload_path)
    server = create_email(config['smtp_server'], config['from_addr'], config['auth_code'])
    with open(payload_path, 'rb') as f:
        send_email(server, config['to_addr'], '测试邮件-附件', '测试内容',
                   payload=f.read(), payload_name=payload_name)
    quit_email(server)


if __name__ == '__main__':
    test_config = {
        'smtp_server': 'smtp.163.com',
        'from_addr': 'jiangkaibo1987@163.com',
        'auth_code': '换成你的授权码',
        'to_addr': '723953397@qq.com',
    }
    test_email1(test_config)
    test_email2(test_config)
    test_email3(test_config)
