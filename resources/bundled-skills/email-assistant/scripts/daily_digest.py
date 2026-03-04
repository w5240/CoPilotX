#!/usr/bin/env python3
"""智能每日邮件摘要 - AI 分类 + 推送到飞书"""
import json
import os
import imaplib
import email
import requests
import argparse
import re
from datetime import datetime, timedelta
from collections import Counter
from email.header import decode_header

CONFIG_PATH = "~/.openclaw/email-config.json"
CONTACTS_PATH = "~/.openclaw/contacts.json"
MAIL_CACHE_PATH = "~/.openclaw/mail_cache.json"

# 需要的模型来分类邮件
MODEL = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-20250514')

def decode_subject(subject):
    """解码邮件主题"""
    if not subject:
        return ""
    decoded = decode_header(subject)
    if decoded:
        parts = []
        for part, encoding in decoded:
            if isinstance(part, bytes):
                if encoding:
                    parts.append(part.decode(encoding))
                else:
                    parts.append(part.decode('utf-8', errors='ignore'))
            else:
                parts.append(part)
        return ''.join(parts)
    return subject

# 关键词规则
ACTION_KEYWORDS = [
    '请确认', '请回复', '需签字', '需决策', '需要您', '请查收',
    'please confirm', 'please reply', 'need your', 'action required',
    '需审核', '待审批', 'approv', 'review', 'feedback'
]

EXPIRE_KEYWORDS = [
    '到期', 'expire', 'renewal', '续费', 'expired',
    '域名', 'domain', 'asic', 'annual review', '年审',
    '续租', '服务到期', 'subscription'
]

def parse_email_date(date_str):
    """解析邮件 Date 头，返回配置时区的 datetime 对象"""
    if not date_str:
        return None
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        # 转换到配置的时区
        user_tz = get_timezone()
        return dt.astimezone(user_tz)
    except:
        pass
    return None

def is_same_day(email_date, target_date):
    """判断邮件日期（上海时区）是否在目标日期"""
    if not email_date:
        return True  # 无法解析时保留
    return email_date.date() == target_date.date()

IGNORE_KEYWORDS = [
    'newsletter', 'marketing', 'promotion', '广告',
    'no-reply', 'noreply', 'linkedin', 'aws 账单',
    '内部员工', '周会', '聚餐投票',
    'qq邮箱', '异地登录', '团队', 'app', '安全', '高效',
    '富途證券', '月結單', '月结单', '證券', '证券', '提醒', '账单', 'statement',
    '前程无忧', '51job', '招聘', '简历', '薪资', '面试'
]

IGNORE_SENDERS = [
    'qq.com', '163.com', '126.com', 'gmail.com',
    'noreply', 'no-reply', 'newsletter',
    'marketing', 'support@', 'help@', 'billing@',
    '51job', 'zhaopin', 'liepin'
]

# 合并显示的发件人简称
SENDER_ALIASES = {
    'qq邮箱': 'QQ邮箱',
    'qq邮箱团队': 'QQ邮箱',
    'noreply@qq.com': 'QQ邮箱',
    'noreply@gitcdn.github.com': 'GitHub',
}

def load_config():
    path = os.path.expanduser(CONFIG_PATH)
    with open(path, 'r') as f:
        return json.load(f)

def get_timezone():
    """获取配置的时区，默认上海"""
    config = load_config()
    tz_name = config.get('timezone', 'Asia/Shanghai')
    import zoneinfo
    return zoneinfo.ZoneInfo(tz_name)

def load_contacts():
    path = os.path.expanduser(CONTACTS_PATH)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"contacts": [], "blocked_senders": []}

def load_mail_cache():
    path = os.path.expanduser(MAIL_CACHE_PATH)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_mail_cache(cache):
    path = os.path.expanduser(MAIL_CACHE_PATH)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_feishu_webhook(config):
    return config.get('feishu', {}).get('webhook')

def send_to_feishu(webhook, message):
    if not webhook:
        print("❌ 未配置飞书 webhook")
        return False
    
    payload = {
        "msg_type": "text",
        "content": {"text": message}
    }
    
    try:
        resp = requests.post(webhook, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ 推送失败: {e}")
        return False

def parse_address(addr_str):
    if not addr_str:
        return None, None
    try:
        if '<' in addr_str and '>' in addr_str:
            name = addr_str.split('<')[0].strip().strip('"')
            email_addr = addr_str.split('<')[1].split('>')[0].strip()
            # 解码名字
            if name:
                decoded = decode_header(name)
                if decoded:
                    parts = []
                    for part, encoding in decoded:
                        if isinstance(part, bytes):
                            if encoding:
                                parts.append(part.decode(encoding))
                            else:
                                parts.append(part.decode('utf-8', errors='ignore'))
                        else:
                            parts.append(part)
                    name = ''.join(parts)
        else:
            name = None
            email_addr = addr_str.strip()
        return name, email_addr.lower()
    except:
        return None, addr_str.lower()

def classify_email(subject, from_email, from_name, body_preview, contacts, blocked):
    """智能分类邮件"""
    
    # 1. 检查是否在黑名单
    if from_email in blocked:
        return 'ignore'
    
    # 1.5 检查发件人是否在黑名单关键词
    from_lower = (from_email or '').lower()
    from_name_lower = (from_name or '').lower()
    for kw in IGNORE_SENDERS:
        if kw in from_lower or kw in from_name_lower:
            return 'ignore'
    
    # 2. 检查是否是 CC
    # (由调用方处理)
    
    # 3. 到期提醒检查
    subject_lower = (subject or '').lower()
    for kw in EXPIRE_KEYWORDS:
        if kw.lower() in subject_lower:
            return 'expire'
    
    # 4. 需要处理检查
    for kw in ACTION_KEYWORDS:
        if kw.lower() in subject_lower:
            return 'action'
    
    # 5. 广告/不需要处理
    for kw in IGNORE_KEYWORDS:
        if kw.lower() in subject_lower:
            return 'ignore'
    
    # 6. 检查是否是已知联系人
    is_known = from_email in [c['email'] for c in contacts.get('contacts', [])]
    
    if is_known:
        # 已知联系人，默认需要处理
        return 'action'
    else:
        # 陌生发件人 + 营销关键词 = 广告
        marketing_patterns = ['sales@', 'hello@', 'contact@', 'info@']
        for pat in marketing_patterns:
            if pat in from_email:
                return 'ignore'
        
        # 陌生发件人可能是冷邮件，标记为 action 让用户决定
        return 'action'

def fetch_emails(provider, config, target_date=None):
    """获取邮件"""
    
    if provider == 'gmail':
        return fetch_gmail(config, target_date)
    elif provider == 'qq':
        return fetch_qq(config, target_date)
    return []

def fetch_gmail(config, target_date=None):
    gmail = config.get('gmail', {})
    email_addr = gmail.get('email')
    password = gmail.get('app_password')
    
    if not email_addr or not password:
        return []
    
    # 确定日期范围
    if target_date:
        since = target_date.strftime('%d-%b-%Y')
        until = (target_date + timedelta(days=1)).strftime('%d-%b-%Y')
    else:
        since = datetime.now().strftime('%d-%b-%Y')
        until = (datetime.now() + timedelta(days=1)).strftime('%d-%b-%Y')
    
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(email_addr, password)
        mail.select('INBOX')
        
        # 搜索当天邮件
        typ, msg_ids = mail.search(None, f'SINCE {since} BEFORE {until}')
        
        if typ != 'OK':
            return []
        
        msg_ids = msg_ids[0].split()
        emails = []
        
        for msg_id in msg_ids:
            try:
                # 使用 RFC822 获取完整数据
                typ, msg_data = mail.fetch(msg_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        from_header = msg.get('From', '')
                        to_header = msg.get('To', '')
                        cc_header = msg.get('Cc', '')
                        subject = decode_subject(msg.get('Subject', '(无主题)'))
                        date_header = msg.get('Date', '')
                        
                        # 解析邮件日期并过滤
                        email_date = parse_email_date(date_header)
                        if target_date and not is_same_day(email_date, target_date):
                            continue
                        
                        from_name, from_email = parse_address(from_header)
                        
                        # 获取正文预览
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == 'text/plain':
                                    body = part.get_payload(decode=True)
                                    try:
                                        body = body.decode('utf-8')
                                    except:
                                        body = body.decode('gbk', errors='ignore')
                                    break
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                try:
                                    body = payload.decode('utf-8')
                                except:
                                    body = payload.decode('gbk', errors='ignore')
                        
                        emails.append({
                            'id': msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                            'from_email': from_email,
                            'from_name': from_name,
                            'to': to_header,
                            'cc': cc_header,
                            'subject': subject,
                            'date': date_header,
                            'body_preview': body[:500] if body else '',
                            'provider': 'gmail'
                        })
            except:
                continue
        
        mail.logout()
        return emails
        
    except Exception as e:
        print(f"❌ Gmail 获取失败: {e}")
        return []

def fetch_qq(config, target_date=None):
    qq = config.get('qq', {})
    email_addr = qq.get('email')
    password = qq.get('授权码')
    
    if not email_addr or not password:
        return []
    
    # 确定日期范围
    if target_date:
        since = target_date.strftime('%d-%b-%Y')
    else:
        since = datetime.now().strftime('%d-%b-%Y')
    
    try:
        mail = imaplib.IMAP4_SSL('imap.qq.com', 993)
        mail.login(email_addr, password)
        mail.select('INBOX')
        
        # 只用 SINCE，BEFORE 可能不支持
        typ, msg_ids = mail.search(None, f'SINCE {since}')
        
        if typ != 'OK':
            return []
        
        msg_ids = msg_ids[0].split()
        emails = []
        
        for msg_id in msg_ids:
            try:
                # 使用 RFC822 获取完整数据
                typ, msg_data = mail.fetch(msg_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        from_header = msg.get('From', '')
                        to_header = msg.get('To', '')
                        cc_header = msg.get('Cc', '')
                        subject = decode_subject(msg.get('Subject', '(无主题)'))
                        date_header = msg.get('Date', '')
                        
                        # 解析邮件日期并过滤
                        email_date = parse_email_date(date_header)
                        if target_date and not is_same_day(email_date, target_date):
                            continue
                        
                        from_name, from_email = parse_address(from_header)
                        
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == 'text/plain':
                                    body = part.get_payload(decode=True)
                                    try:
                                        body = body.decode('utf-8')
                                    except:
                                        body = body.decode('gbk', errors='ignore')
                                    break
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                try:
                                    body = payload.decode('utf-8')
                                except:
                                    body = payload.decode('gbk', errors='ignore')
                        
                        emails.append({
                            'id': msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                            'from_email': from_email,
                            'from_name': from_name,
                            'to': to_header,
                            'cc': cc_header,
                            'subject': subject,
                            'date': date_header,
                            'body_preview': body[:500] if body else '',
                            'provider': 'qq'
                        })
            except:
                continue
        
        mail.logout()
        return emails
        
    except Exception as e:
        print(f"❌ QQ 邮箱获取失败: {e}")
        return []

def get_sender_alias(name, email):
    """获取显示用的发件人简称"""
    if not name:
        name = email.split('@')[0] if '@' in email else email
    
    name_lower = name.lower()
    for pattern, alias in SENDER_ALIASES.items():
        if pattern in name_lower:
            return alias
    return name

def generate_digest(emails, contacts, blocked):
    """生成邮件摘要"""
    
    action_emails = []
    expire_emails = []
    ignore_emails = []
    
    for i, mail in enumerate(emails):
        # 检查是否是 CC
        is_cc = bool(mail.get('cc'))
        
        classification = classify_email(
            mail['subject'],
            mail['from_email'],
            mail['from_name'],
            mail['body_preview'],
            contacts,
            blocked
        )
        
        # CC 的放到不需要处理
        if is_cc:
            classification = 'ignore'
        
        mail['classification'] = classification
        
        if classification == 'action':
            action_emails.append(mail)
        elif classification == 'expire':
            expire_emails.append(mail)
        else:
            ignore_emails.append(mail)
    
    # 重新编号（按显示顺序）
    idx = 1
    for mail in action_emails:
        mail['index'] = idx
        idx += 1
    for mail in expire_emails:
        mail['index'] = idx
        idx += 1
    for mail in ignore_emails:
        mail['index'] = idx
        idx += 1
    
    return {
        'total': len(emails),
        'action': action_emails,
        'expire': expire_emails,
        'ignore': ignore_emails
    }

def format_digest(digest, date_str):
    """格式化摘要"""
    total = digest['total']
    action_count = len(digest['action'])
    expire_count = len(digest['expire'])
    ignore_count = len(digest['ignore'])
    
    lines = [
        f"📧 {date_str} 邮件摘要 ({total}封新邮件，{action_count}封需要你处理)",
        ""
    ]
    
    # 需要处理的邮件
    if digest['action']:
        lines.append("🟡 需要你处理:")
        for mail in digest['action']:
            sender = get_sender_alias(mail['from_name'], mail['from_email'])
            subject = mail['subject'][:35] if len(mail['subject']) > 35 else mail['subject']
            preview = (mail.get('body_preview') or '')[:30].replace('\n', ' ')
            if preview:
                lines.append(f"{mail['index']}. {sender} — {subject}")
                lines.append(f"   📝 {preview}...")
            else:
                lines.append(f"{mail['index']}. {sender} — {subject}")
        lines.append("")
    
    # 到期提醒
    if digest['expire']:
        lines.append("⚠️ 到期提醒:")
        for mail in digest['expire']:
            sender = get_sender_alias(mail['from_name'], mail['from_email'])
            lines.append(f"• {sender} — {mail['subject']}")
        lines.append("")
    
    # 不需要处理的邮件
    if digest['ignore']:
        lines.append(f"⚪ 不需要你处理 ({ignore_count}封):")
        # 按发件人分组显示
        senders = {}
        for mail in digest['ignore']:
            key = get_sender_alias(mail['from_name'], mail['from_email'])
            if key not in senders:
                senders[key] = {'count': 0, 'sample_subject': mail['subject']}
            senders[key]['count'] += 1
        
        for sender, info in list(senders.items())[:10]:
            count = info['count']
            sample = info['sample_subject'][:25] if len(info['sample_subject']) > 25 else info['sample_subject']
            if count == 1:
                lines.append(f"• {sender}: {sample}")
            else:
                lines.append(f"• {sender} ({count}封): {sample}")
        lines.append("")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='智能邮件摘要')
    parser.add_argument('--provider', choices=['gmail', 'qq', 'all'], default='all',
                        help='选择邮箱')
    parser.add_argument('--date', type=str, default=None,
                        help='查询日期，如 2026-03-02')
    parser.add_argument('--no-push', action='store_true',
                        help='不推送到飞书')
    parser.add_argument('--output', action='store_true',
                        help='输出 JSON 到缓存文件')
    args = parser.parse_args()
    
    config = load_config()
    contacts = load_contacts()
    blocked = set(contacts.get('blocked_senders', []))
    
    # 解析日期
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
        except:
            try:
                # 支持 2026.3.2 格式
                target_date = datetime.strptime(args.date, '%Y.%m.%d')
            except:
                print(f"❌ 日期格式错误: {args.date}")
                print("支持格式: 2026-03-02 或 2026.3.2")
                exit(1)
    
    date_str = target_date.strftime('%Y-%m-%d') if target_date else datetime.now().strftime('%Y-%m-%d')
    
    # 获取各邮箱邮件
    all_emails = []
    
    if args.provider in ['gmail', 'all']:
        if 'gmail' in config:
            emails = fetch_gmail(config, target_date)
            print(f"📬 Gmail: {len(emails)} 封")
            all_emails.extend(emails)
    
    if args.provider in ['qq', 'all']:
        if 'qq' in config:
            emails = fetch_qq(config, target_date)
            print(f"📬 QQ邮箱: {len(emails)} 封")
            all_emails.extend(emails)
    
    # 生成摘要
    digest = generate_digest(all_emails, contacts, blocked)
    
    # 格式化输出
    message = format_digest(digest, date_str)
    print("\n" + message)
    
    # 保存到缓存（用于快速回复）
    if args.output:
        cache = load_mail_cache()
        cache[date_str] = {
            'digest': digest,
            'emails': all_emails,
            'generated_at': datetime.now().isoformat()
        }
        save_mail_cache(cache)
        print(f"\n✅ 已缓存到: ~/.openclaw/mail_cache.json")
    
    # 推送到飞书
    if not args.no_push:
        webhook = get_feishu_webhook(config)
        if webhook:
            send_to_feishu(webhook, message)

if __name__ == '__main__':
    main()
