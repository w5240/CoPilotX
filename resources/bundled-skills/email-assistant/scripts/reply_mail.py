#!/usr/bin/env python3
"""快速回复指定邮件"""
import json
import os
import smtplib
import email
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

CONFIG_PATH = "~/.openclaw/email-config.json"
MAIL_CACHE_PATH = "~/.openclaw/mail_cache.json"

def load_config():
    path = os.path.expanduser(CONFIG_PATH)
    with open(path, 'r') as f:
        return json.load(f)

def load_mail_cache():
    path = os.path.expanduser(MAIL_CACHE_PATH)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def find_email_by_index(cache, index, date=None):
    """根据编号查找邮件"""
    if date:
        if date in cache:
            digest = cache[date]['digest']
            for mail in digest.get('action', []) + digest.get('expire', []):
                if mail.get('index') == index:
                    return mail
        return None
    
    for date_key, data in sorted(cache.items(), reverse=True):
        digest = data.get('digest', {})
        for mail in digest.get('action', []) + digest.get('expire', []):
            if mail.get('index') == index:
                return mail
    
    return None

def get_email_full_content(provider, config, msg_id):
    """获取邮件完整内容"""
    if provider == 'gmail':
        return get_gmail_full(config, msg_id)
    elif provider == 'qq':
        return get_qq_full(config, msg_id)
    return None

def get_gmail_full(config, msg_id):
    gmail = config.get('gmail', {})
    email_addr = gmail.get('email')
    password = gmail.get('app_password')
    
    try:
        import imaplib
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(email_addr, password)
        mail.select('INBOX')
        
        typ, msg_data = mail.fetch(msg_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                mail.logout()
                return msg
        
        mail.logout()
    except Exception as e:
        print(f"❌ 获取邮件失败: {e}")
    return None

def get_qq_full(config, msg_id):
    qq = config.get('qq', {})
    email_addr = qq.get('email')
    password = qq.get('授权码')
    
    try:
        import imaplib
        mail = imaplib.IMAP4_SSL('imap.qq.com', 993)
        mail.login(email_addr, password)
        mail.select('INBOX')
        
        typ, msg_data = mail.fetch(msg_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                mail.logout()
                return msg
        
        mail.logout()
    except Exception as e:
        print(f"❌ 获取邮件失败: {e}")
    return None

def send_reply(provider, config, to_email, subject, body, original_msg=None):
    """发送回复邮件"""
    
    if provider == 'gmail':
        return send_gmail(config, to_email, subject, body, original_msg)
    elif provider == 'qq':
        return send_qq(config, to_email, subject, body, original_msg)
    return False, "未支持的邮箱"

def send_gmail(config, to_email, subject, body, original_msg=None):
    gmail = config.get('gmail', {})
    from_email = gmail.get('email')
    password = gmail.get('app_password')
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    
    if not subject.startswith('Re:') and not subject.startswith('RE:'):
        subject = f"Re: {subject}"
    msg['Subject'] = subject
    
    full_body = body
    if original_msg:
        full_body = f"\n\n--- 原始邮件 ---\n{original_msg}\n\n{full_body}"
    
    msg.attach(MIMEText(full_body, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        return True, "邮件发送成功"
    except Exception as e:
        return False, str(e)

def send_qq(config, to_email, subject, body, original_msg=None):
    qq = config.get('qq', {})
    from_email = qq.get('email')
    password = qq.get('授权码')
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    
    if not subject.startswith('Re:') and not subject.startswith('RE:'):
        subject = f"Re: {subject}"
    msg['Subject'] = subject
    
    full_body = body
    if original_msg:
        full_body = f"\n\n--- 原始邮件 ---\n{original_msg}\n\n{full_body}"
    
    msg.attach(MIMEText(full_body, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.qq.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        return True, "邮件发送成功"
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description='快速回复邮件')
    parser.add_argument('--index', type=int, required=True,
                        help='邮件编号')
    parser.add_argument('--date', type=str, default=None,
                        help='邮件日期，如 2026-03-02')
    parser.add_argument('--provider', choices=['gmail', 'qq'], default='qq',
                        help='使用哪个邮箱发送')
    parser.add_argument('--body', type=str, required=True,
                        help='回复内容')
    parser.add_argument('--confirm', action='store_true',
                        help='确认发送（默认只预览，需加此参数才真正发送）')
    parser.add_argument('--dry-run', action='store_true',
                        help='只显示邮件信息，不发送')
    args = parser.parse_args()
    
    config = load_config()
    cache = load_mail_cache()
    
    if not cache:
        print("❌ 没有缓存的邮件数据")
        print("请先运行: python daily_digest.py --output")
        exit(1)
    
    # 查找邮件
    mail = find_email_by_index(cache, args.index, args.date)
    
    if not mail:
        print(f"❌ 未找到编号 {args.index} 的邮件")
        if args.date:
            print(f"   日期 {args.date} 的邮件缓存中未找到")
        else:
            print("   请尝试指定日期: --date 2026-03-02")
        exit(1)
    
    # 显示邮件信息
    print(f"📧 找到邮件:")
    print(f"   发件人: {mail.get('from_name')} <{mail.get('from_email')}>")
    print(f"   主题: {mail.get('subject')}")
    print(f"   分类: {mail.get('classification')}")
    print(f"   提供商: {mail.get('provider')}")
    print()
    
    if args.dry_run:
        print("ℹ️  dry-run 模式，不发送")
        exit(0)
    
    to_email = mail.get('from_email')
    subject = mail.get('subject', '')
    
    # 预览回复内容
    print(f"📤 将要发送:")
    print(f"   给: {to_email}")
    print(f"   主题: Re: {subject}")
    print(f"   内容: {args.body}")
    print()
    
    # 确认模式
    if args.confirm:
        print("⏳ 确认发送中...")
        success, message = send_reply(args.provider, config, to_email, subject, args.body)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ 发送失败: {message}")
    else:
        print("ℹ️  预览模式 - 如需发送，请加 --confirm 参数")
        print("   示例: reply_mail.py --index 1 --body '好的' --confirm")

if __name__ == '__main__':
    main()
