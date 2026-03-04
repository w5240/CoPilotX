#!/usr/bin/env python3
"""智能同步联系人 - 自动过滤广告邮件发件人"""
import json
import os
import imaplib
import email
import argparse
import re
from collections import defaultdict
from datetime import datetime, timedelta

CONFIG_PATH = "~/.openclaw/email-config.json"
CONTACTS_PATH = "~/.openclaw/contacts.json"

# 广告发件人关键词（自动过滤）- 需要更精准
AD_KEYWORDS = [
    'noreply', 'no-reply', 'newsletter', 'marketing', 'advertising',
    'support@', 'help@', 'billing@', 'orders@', 'team@',
    'linkedin', 'twitter', 'facebook', 'instagram',
    'zhihu', 'toutiao', 'sina',
    '广告', '推送', '订阅', 'promotion',
    # 完整域名匹配
    'amazon.com', 'github.com', 'microsoft.com', 'google.com',
]

# 已知可信域名（不过滤）
TRUSTED_DOMAINS = [
    'company.com', 'business.com',  # 添加用户域名
    'gmail.com', 'qq.com', '163.com', '126.com', 'outlook.com'
]

def load_config():
    path = os.path.expanduser(CONFIG_PATH)
    with open(path, 'r') as f:
        return json.load(f)

def load_contacts():
    path = os.path.expanduser(CONTACTS_PATH)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "contacts": [],
        "blocked_senders": [],
        "last_sync": None
    }

def save_contacts(contacts):
    path = os.path.expanduser(CONTACTS_PATH)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)

def is_ad_sender(email_addr, name=None):
    """判断是否是广告发件人"""
    email_lower = email_addr.lower()
    name_lower = (name or '').lower()
    
    # 明确是广告的关键词
    ad_patterns = [
        'noreply', 'no-reply', 'newsletter', 'marketing', 'advertising',
        'support@', 'help@', 'billing@', 'orders@', 'team@',
        'linkedin', 'twitter', 'facebook', 'instagram',
        'zhihu', 'toutiao', 'sina',
        '广告', '推送', '订阅', 'promotion',
        'amazon.com', 'github.com', 'microsoft.com', 'google.com',
    ]
    
    # 只检查 @ 前的部分或完整匹配
    for kw in ad_patterns:
        if kw in email_lower or kw in name_lower:
            return True
    
    # 检查是否是纯数字域名（可疑）
    domain = email_lower.split('@')[-1] if '@' in email_lower else ''
    if domain and re.match(r'^[\d.]+$', domain):
        return True
    
    # 保留常见邮箱服务商
    trusted_domains = ['gmail.com', 'qq.com', '163.com', '126.com', 'outlook.com', 'hotmail.com']
    if domain in trusted_domains:
        return False
    
    return False

def parse_address(addr_str):
    """解析邮件地址"""
    if not addr_str:
        return None, None
    try:
        if '<' in addr_str and '>' in addr_str:
            name = addr_str.split('<')[0].strip().strip('"')
            email_addr = addr_str.split('<')[1].split('>')[0].strip()
        else:
            name = None
            email_addr = addr_str.strip()
        return name, email_addr.lower()
    except:
        return None, addr_str.lower()

def sync_gmail(config, days=180):
    """从 Gmail 同步联系人"""
    gmail = config.get('gmail', {})
    email_addr = gmail.get('email')
    password = gmail.get('app_password')
    
    if not email_addr or not password:
        print("⚠️ 未配置 Gmail")
        return None
    
    contacts = load_contacts()
    email_to_info = defaultdict(lambda: {'names': set(), 'count': 0})
    
    print(f"📧 连接 Gmail: {email_addr}")
    
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(email_addr, password)
        mail.select('INBOX')
        
        since = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
        typ, msg_ids = mail.search(None, f'SINCE {since}')
        
        if typ != 'OK':
            print("❌ 搜索邮件失败")
            return None
        
        msg_ids = msg_ids[0].split()
        total = len(msg_ids)
        print(f"📬 扫描最近 {days} 天的 {total} 封邮件...")
        
        max_emails = min(1000, total)
        
        for i, msg_id in enumerate(msg_ids[:max_emails]):
            if i % 200 == 0:
                print(f"  进度: {i}/{max_emails}")
            
            try:
                # 使用 RFC822 获取完整邮件数据
                typ, msg_data = mail.fetch(msg_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # 提取发件人
                        from_header = msg.get('From', '')
                        name, addr = parse_address(from_header)
                        if addr and addr != email_addr.lower():
                            email_to_info[addr]['names'].add(name or addr.split('@')[0])
                            email_to_info[addr]['count'] += 1
                        
                        # 提取收件人和抄送
                        for header in ['To', 'Cc']:
                            for addr_header in msg.get(header, '').split(','):
                                name, addr = parse_address(addr_header.strip())
                                if addr and addr != email_addr.lower():
                                    email_to_info[addr]['names'].add(name or addr.split('@')[0])
            except:
                continue
        
        mail.logout()
        
    except Exception as e:
        print(f"❌ Gmail 连接失败: {e}")
        return None
    
    return process_contacts(contacts, email_to_info, 'gmail')

def sync_qq(config, days=180):
    """从 QQ 邮箱同步联系人"""
    qq = config.get('qq', {})
    email_addr = qq.get('email')
    password = qq.get('授权码')
    
    if not email_addr or not password:
        print("⚠️ 未配置 QQ 邮箱")
        return None
    
    contacts = load_contacts()
    email_to_info = defaultdict(lambda: {'names': set(), 'count': 0})
    
    print(f"📧 连接 QQ 邮箱: {email_addr}")
    
    try:
        mail = imaplib.IMAP4_SSL('imap.qq.com', 993)
        mail.login(email_addr, password)
        mail.select('INBOX')
        
        since = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
        typ, msg_ids = mail.search(None, f'SINCE {since}')
        
        if typ != 'OK':
            print("❌ 搜索邮件失败")
            return None
        
        msg_ids = msg_ids[0].split()
        total = len(msg_ids)
        print(f"📬 扫描最近 {days} 天的 {total} 封邮件...")
        
        max_emails = min(1000, total)
        
        for i, msg_id in enumerate(msg_ids[:max_emails]):
            if i % 200 == 0:
                print(f"  进度: {i}/{max_emails}")
            
            try:
                # 使用 RFC822 获取完整邮件数据
                typ, msg_data = mail.fetch(msg_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        from_header = msg.get('From', '')
                        name, addr = parse_address(from_header)
                        if addr and addr != email_addr.lower():
                            email_to_info[addr]['names'].add(name or addr.split('@')[0])
                            email_to_info[addr]['count'] += 1
                        
                        for header in ['To', 'Cc']:
                            for addr_header in msg.get(header, '').split(','):
                                name, addr = parse_address(addr_header.strip())
                                if addr and addr != email_addr.lower():
                                    email_to_info[addr]['names'].add(name or addr.split('@')[0])
            except:
                continue
        
        mail.logout()
        
    except Exception as e:
        print(f"❌ QQ 邮箱连接失败: {e}")
        return None
    
    return process_contacts(contacts, email_to_info, 'qq')

def process_contacts(contacts, email_to_info, source):
    """处理并保存联系人"""
    existing = {c['email']: c for c in contacts.get('contacts', [])}
    blocked = set(contacts.get('blocked_senders', []))
    new_blocked = []
    
    all_contacts = list(existing.values())
    new_count = 0
    
    for email_addr, info in email_to_info.items():
        # 跳过广告发件人
        name = list(info['names'])[0]
        if is_ad_sender(email_addr, name):
            if email_addr not in blocked:
                blocked.add(email_addr)
                new_blocked.append(email_addr)
            continue
        
        if email_addr in existing:
            # 更新
            existing[email_addr]['name'] = name
            existing[email_addr]['last_seen'] = datetime.now().isoformat()
            existing[email_addr]['email_count'] = info['count']
        else:
            # 新增
            all_contacts.append({
                'email': email_addr,
                'name': name,
                'source': source,
                'added': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'email_count': info['count']
            })
            new_count += 1
    
    contacts['contacts'] = all_contacts
    contacts['blocked_senders'] = list(blocked)
    contacts['last_sync'] = datetime.now().isoformat()
    
    save_contacts(contacts)
    
    print(f"🎉 同步完成!")
    print(f"   联系人: {len(all_contacts)} (新增 {new_count})")
    print(f"   拦截广告: {len(new_blocked)}")
    
    return contacts

def main():
    parser = argparse.ArgumentParser(description='智能同步联系人')
    parser.add_argument('--provider', choices=['gmail', 'qq', 'all'], default='all',
                        help='选择邮箱提供商')
    parser.add_argument('--days', type=int, default=180,
                        help='扫描过去多少天的邮件')
    args = parser.parse_args()
    
    config = load_config()
    
    if args.provider in ['gmail', 'all']:
        if 'gmail' in config:
            sync_gmail(config, args.days)
    
    if args.provider in ['qq', 'all']:
        if 'qq' in config:
            sync_qq(config, args.days)

if __name__ == '__main__':
    main()
