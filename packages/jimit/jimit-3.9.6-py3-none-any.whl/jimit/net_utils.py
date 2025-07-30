#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Reference: [
    https://docs.python.org/2/library/email.html,
    http://www.cnblogs.com/xiaowuyi/archive/2012/03/17/2404015.html,
    http://www.tutorialspoint.com/python/python_sending_email.htm
]
"""


import socket
from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr


__author__ = 'James Iter'
__date__ = '15/6/26'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2015 by James Iter.'


class NetUtils(object):

    @staticmethod
    def smtp_init(host='', port=None, login_name='', password='', sp=''):
        """
        :param host:
        :param port:
        :param login_name:
        :param password:
        :param sp: tls or ssl
        The SP means Security Protocol.
        :return:
        """

        if port is None:
            if sp == 'tls':
                port = 587
            elif sp == 'ssl':
                port = 465
            else:
                port = 25

        if sp == 'tls':
            _smtp_server = SMTP(host, port)
            _smtp_server.starttls()

        elif sp == 'ssl':
            _smtp_server = SMTP_SSL(host, port)

        else:
            _smtp_server = SMTP(host, port)

        _smtp_server.login(login_name, password)
        return _smtp_server

    @staticmethod
    def attachment(title='', path=None):
        part = MIMEApplication(open(path, 'rb').read())
        part.add_header('Content-Disposition', 'attachment', filename=Header(title, 'utf-8').encode())
        return part

    @staticmethod
    def send_mail(_smtp_server=None, sender=None, receivers=None, title='', message='', html=False, attachments=None):
        assert isinstance(sender, (tuple, list))
        assert isinstance(receivers, list)
        """
        :rtype : dict
        :param smtp_server: 一个已建立好连接的smtp实例
        :param sender: 发送者邮件地址('sender@jimit.cc')
        :param receivers: 收件者们的地址(['user1@jimit.cc', 'user2@jimit.cc'])
        :param title: 邮件标题('这是一个测试邮件')
        :param message: 邮件内容('Hello!')
        :param html: 邮件内容类型是否为html格式
        :param attachments: 附件列表，类型为MIMEImage
        :return: 返回发送结果
        """
        if attachments is None:
            attachments = []

        if _smtp_server is None:
            raise ValueError('smtp_server must is not None.')

        sender_title = sender[0]
        sender_address = sender[1]
        mail = MIMEMultipart()
        mail['Subject'] = Header(title, 'utf-8').encode()
        mail['From'] = formataddr((Header(sender_title, 'utf-8').encode(), sender_address))

        receivers_list = list()
        receivers_address = list()
        for receiver in receivers:
            receivers_list.append(formataddr((Header(receiver[0], 'utf-8').encode(), receiver[1])))
            receivers_address.append(receiver[1])

        mail['To'] = ','.join(receivers_list)

        if html:
            message = MIMEText(message, "html", 'utf8')
        else:
            message = MIMEText(message, "plain", 'utf8')

        mail.attach(message)
        for attachment in attachments:
            mail.attach(attachment)

        return _smtp_server.sendmail(sender_address, receivers_address, mail.as_string())

    @staticmethod
    def port_is_opened(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(('0.0.0.0', port))
        if result == 0:
            return True
        else:
            return False

    @staticmethod
    def tcp_check(host, port=80, timeout=3):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = -1

        try:

            result = s.connect_ex((host, int(port)))
            s.shutdown(socket.SHUT_RD)

        except Exception as e:
            print(e)

        finally:
            s.close()

        return result == 0

# Example:
# smtp_server = NetUtils.smtp_init(host='mail.your-domain.com', port=465, login_name='username',
#                                  password='pswd', sp='ssl')
# msg = """
# 山川异域
# 风月同天
# """
# ret = NetUtils.send_mail(_smtp_server=smtp_server, sender=('发件人名称', 'username@your-domain.com'),
#                          receivers=[('收件人名称', 'receiver@recivier-domain.com')], title='标题',
#                          message=msg)
