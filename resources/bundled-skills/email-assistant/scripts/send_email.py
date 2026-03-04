#!/usr/bin/env python3
"""发送邮件"""
import json
import os
import smtplib
import email
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CONFIG_PATH = "~/.openclaw/email-config.json"
CONTACTS_PATH = "~/.openclaw/contacts.json"

def load_config():
    path = os.path.expanduser(CONFIG_PATH)
    with open(path, 'r') as f:
        return json.load(f)

def load_contacts():
    path = os.path.expanduser(CONTACTS_PATH)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"contacts": []}

def search_contacts(query):
    """搜索联系人"""
    contacts = load_contacts()
    query_lower = query.lower()
    
    results = []
    for c in contacts.get('contacts', []):
        if query_lower in c.get('email', '').lower() or query_lower in c.get('name', '').lower():
            results.append(c)
    
    return results

def send_email_gmail(config, to_email, subject, body):
    """通过 Gmail 发送"""
    gmail = config.get('gmail', {})
    from_email = gmail.get('email')
    password = gmail.get('app_password')
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        return True, "邮件发送成功"
    except Exception as e:
        return False, str(e)

def send_email_qq(config, to_email, subject, body):
    """通过 QQ 邮箱发送"""
    qq = config.get('qq', {})
    from_email = qq.get('email')
    password = qq.get('授权码')
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.qq.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        return True, "邮件发送成功"
    except Exception as e:
        return False, str(e)

def send_email(provider, to_email, subject, body):
    """发送邮件"""
    config = load_config()
    
    if provider == 'gmail':
        return send_email_gmail(config, to_email, subject, body)
    elif provider == 'qq':
        return send_email_qq(config, to_email, subject, body)
    else:
        return False, f"未支持的邮箱提供商: {provider}"

def main():
    parser = argparse.ArgumentParser(description='发送邮件')
    parser.add_argument('--provider', choices=['gmail', 'qq'], required=True,
                        help='选择发送邮箱')
    parser.add_argument('--to', required=True,
                        help='收件人邮箱或姓名')
    parser.add_argument('--subject', required=True,
                        help='邮件主题')
    parser.add_argument('--body', required=True,
                        help='邮件正文')
    args = parser.parse_args()
    
    # 搜索联系人
    results = search_contacts(args.to)
    
    if not results:
        print(f"❌ 未找到联系人: {args.to}")
        print("请先运行 sync_contacts.py 同步联系人")
        exit(1)
    
    if len(results) > 1:
        print(f"找到多个匹配，请选择一个:")
        for i, c in enumerate(results):
            print(f"  {i+1}. {c['name']} <{c['email']}>")
        print("请使用精确邮箱地址再次调用")
        exit(1)
    
    to_email = results[0]['email']
    print(f"📧 发送给: {results[0]['name']} <{to_email}>")
    print(f"📝 主题: {args.subject}")
    
    success, message = send_email(args.provider, to_email, args.subject, args.body)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ 发送失败: {message}")

if __name__ == '__main__':
    main()
