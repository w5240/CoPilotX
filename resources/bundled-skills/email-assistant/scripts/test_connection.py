#!/usr/bin/env python3
"""测试邮箱连接"""
import json
import sys
import imaplib
import smtplib
import argparse

CONFIG_PATH = "~/.openclaw/email-config.json"

def load_config():
    import os
    path = os.path.expanduser(CONFIG_PATH)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件未找到: {path}")
        print("请先创建配置文件: ~/.openclaw/email-config.json")
        sys.exit(1)

def test_gmail(config):
    gmail = config.get('gmail', {})
    email = gmail.get('email')
    password = gmail.get('app_password')
    
    if not email or not password:
        return None
    
    print(f"📧 测试 Gmail: {email}")
    
    # IMAP
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(email, password)
        mail.select('INBOX')
        print("  ✅ IMAP 连接成功")
        mail.logout()
    except Exception as e:
        print(f"  ❌ IMAP 连接失败: {e}")
        return False
    
    # SMTP
    try:
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(email, password)
        print("  ✅ SMTP 连接成功")
        smtp.quit()
    except Exception as e:
        print(f"  ❌ SMTP 连接失败: {e}")
        return False
    
    return True

def test_qq(config):
    qq = config.get('qq', {})
    email = qq.get('email')
    password = qq.get('授权码')
    
    if not email or not password:
        return None
    
    print(f"📧 测试 QQ 邮箱: {email}")
    
    # IMAP
    try:
        mail = imaplib.IMAP4_SSL('imap.qq.com', 993)
        mail.login(email, password)
        mail.select('INBOX')
        print("  ✅ IMAP 连接成功")
        mail.logout()
    except Exception as e:
        print(f"  ❌ IMAP 连接失败: {e}")
        return False
    
    # SMTP
    try:
        smtp = smtplib.SMTP('smtp.qq.com', 587)
        smtp.starttls()
        smtp.login(email, password)
        print("  ✅ SMTP 连接成功")
        smtp.quit()
    except Exception as e:
        print(f"  ❌ SMTP 连接失败: {e}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='测试邮箱连接')
    parser.add_argument('--provider', choices=['gmail', 'qq', 'auto'], default='auto',
                        help='选择邮箱提供商 (auto=自动检测已配置的)')
    args = parser.parse_args()
    
    config = load_config()
    
    results = {}
    
    if args.provider == 'auto':
        # 自动检测
        gmail_result = test_gmail(config)
        if gmail_result is not None:
            results['gmail'] = gmail_result
        
        qq_result = test_qq(config)
        if qq_result is not None:
            results['qq'] = qq_result
    elif args.provider == 'gmail':
        results['gmail'] = test_gmail(config)
    elif args.provider == 'qq':
        results['qq'] = test_qq(config)
    
    print("\n" + "="*40)
    if results:
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        if passed == total:
            print(f"🎉 {passed}/{total} 个邮箱连接成功!")
        else:
            print(f"⚠️ {passed}/{total} 个邮箱连接成功")
    else:
        print("ℹ️  未检测到已配置的邮箱")

if __name__ == '__main__':
    main()
