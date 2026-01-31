"""
Alert & Notification System
============================

Send alerts via multiple channels:
- Telegram Bot
- Email (SMTP)
- SMS (future)
- WhatsApp (future)

Alert types:
- Price alerts (target reached)
- Signal alerts (BUY/SELL generated)
- News alerts (stock mentioned)
- Dividend alerts (ex-date approaching)
- Pattern alerts (technical patterns detected)
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
import requests
import json


class AlertSystem:
    """Manage alerts and notifications"""

    def __init__(self):
        """Initialize Alert System"""
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')

        self.email_sender = os.getenv('SMTP_EMAIL', '')
        self.email_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))

    def send_telegram_alert(
        self,
        message: str,
        parse_mode: str = 'Markdown'
    ) -> Dict:
        """
        Send alert via Telegram

        Args:
            message: Alert message
            parse_mode: 'Markdown' or 'HTML'

        Returns:
            Dict with send status
        """
        if not self.telegram_token or not self.telegram_chat_id:
            return {
                'success': False,
                'error': 'Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID'
            }

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"

        payload = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': parse_mode
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            return {
                'success': True,
                'channel': 'Telegram',
                'message_id': response.json().get('result', {}).get('message_id'),
                'timestamp': datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'channel': 'Telegram'
            }

    def send_email_alert(
        self,
        recipient: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> Dict:
        """
        Send alert via Email

        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body
            html: Whether body is HTML

        Returns:
            Dict with send status
        """
        if not self.email_sender or not self.email_password:
            return {
                'success': False,
                'error': 'Email not configured. Set SMTP_EMAIL and SMTP_PASSWORD'
            }

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_sender
            msg['To'] = recipient
            msg['Subject'] = subject

            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)

            return {
                'success': True,
                'channel': 'Email',
                'recipient': recipient,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'channel': 'Email'
            }

    def send_multi_channel_alert(
        self,
        alert_data: Dict,
        channels: List[str] = ['telegram', 'email']
    ) -> Dict:
        """
        Send alert to multiple channels

        Args:
            alert_data: Dict with alert information
            channels: List of channels ('telegram', 'email')

        Returns:
            Dict with results per channel
        """
        results = {}

        # Format messages for each channel
        telegram_msg = self._format_telegram_message(alert_data)
        email_subject = alert_data.get('subject', 'Stock Alert')
        email_body = self._format_email_message(alert_data)

        # Send to each channel
        if 'telegram' in channels:
            results['telegram'] = self.send_telegram_alert(telegram_msg)

        if 'email' in channels and alert_data.get('email_recipient'):
            results['email'] = self.send_email_alert(
                recipient=alert_data['email_recipient'],
                subject=email_subject,
                body=email_body
            )

        return results

    def create_price_alert(
        self,
        stock_code: str,
        current_price: float,
        target_price: float,
        alert_type: str = 'TARGET_REACHED'
    ) -> Dict:
        """
        Create price alert

        Args:
            stock_code: Stock ticker
            current_price: Current price
            target_price: Target price
            alert_type: 'TARGET_REACHED', 'STOP_LOSS_HIT', etc.

        Returns:
            Alert data dict
        """
        emoji_map = {
            'TARGET_REACHED': '🎯',
            'STOP_LOSS_HIT': '🛑',
            'PRICE_ABOVE': '📈',
            'PRICE_BELOW': '📉'
        }

        emoji = emoji_map.get(alert_type, '🔔')
        price_change = ((current_price - target_price) / target_price) * 100

        return {
            'type': 'PRICE_ALERT',
            'alert_type': alert_type,
            'stock_code': stock_code,
            'subject': f"{emoji} {stock_code} Price Alert: {alert_type.replace('_', ' ').title()}",
            'current_price': current_price,
            'target_price': target_price,
            'price_change_pct': price_change,
            'timestamp': datetime.now().isoformat(),
            'priority': 'HIGH'
        }

    def create_signal_alert(
        self,
        stock_code: str,
        signal: str,
        confidence: float,
        entry_price: Optional[float] = None,
        target_price: Optional[float] = None,
        stop_loss: Optional[float] = None
    ) -> Dict:
        """
        Create trading signal alert

        Args:
            stock_code: Stock ticker
            signal: 'STRONG_BUY', 'BUY', 'SELL', etc.
            confidence: Signal confidence (0-100)
            entry_price: Recommended entry
            target_price: Recommended target
            stop_loss: Recommended stop loss

        Returns:
            Alert data dict
        """
        emoji_map = {
            'STRONG_BUY': '🟢🟢',
            'BUY': '🟢',
            'HOLD': '🟡',
            'SELL': '🔴',
            'STRONG_SELL': '🔴🔴'
        }

        emoji = emoji_map.get(signal, '🔔')

        return {
            'type': 'SIGNAL_ALERT',
            'stock_code': stock_code,
            'subject': f"{emoji} {stock_code} Trading Signal: {signal}",
            'signal': signal,
            'confidence': confidence,
            'entry_price': entry_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'timestamp': datetime.now().isoformat(),
            'priority': 'HIGH' if signal in ['STRONG_BUY', 'STRONG_SELL'] else 'MEDIUM'
        }

    def create_pattern_alert(
        self,
        stock_code: str,
        pattern_name: str,
        pattern_type: str,
        confidence: float
    ) -> Dict:
        """
        Create technical pattern alert

        Args:
            stock_code: Stock ticker
            pattern_name: Pattern name (e.g., 'Head and Shoulders')
            pattern_type: 'BULLISH' or 'BEARISH'
            confidence: Pattern confidence (0-100)

        Returns:
            Alert data dict
        """
        emoji = '🟢' if pattern_type == 'BULLISH' else '🔴'

        return {
            'type': 'PATTERN_ALERT',
            'stock_code': stock_code,
            'subject': f"{emoji} {stock_code} Pattern Detected: {pattern_name}",
            'pattern_name': pattern_name,
            'pattern_type': pattern_type,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'priority': 'MEDIUM'
        }

    def create_news_alert(
        self,
        stock_code: str,
        headline: str,
        sentiment: str,
        source: str
    ) -> Dict:
        """
        Create news alert

        Args:
            stock_code: Stock ticker
            headline: News headline
            sentiment: 'POSITIVE', 'NEGATIVE', 'NEUTRAL'
            source: News source

        Returns:
            Alert data dict
        """
        emoji_map = {
            'POSITIVE': '📰🟢',
            'NEGATIVE': '📰🔴',
            'NEUTRAL': '📰🟡'
        }

        emoji = emoji_map.get(sentiment, '📰')

        return {
            'type': 'NEWS_ALERT',
            'stock_code': stock_code,
            'subject': f"{emoji} {stock_code} News: {headline[:50]}...",
            'headline': headline,
            'sentiment': sentiment,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'priority': 'MEDIUM'
        }

    def create_dividend_alert(
        self,
        stock_code: str,
        ex_date: str,
        dividend_amount: float,
        days_until: int
    ) -> Dict:
        """
        Create dividend alert

        Args:
            stock_code: Stock ticker
            ex_date: Ex-dividend date
            dividend_amount: Dividend per share
            days_until: Days until ex-date

        Returns:
            Alert data dict
        """
        return {
            'type': 'DIVIDEND_ALERT',
            'stock_code': stock_code,
            'subject': f"💰 {stock_code} Dividend Alert: {days_until} days until ex-date",
            'ex_date': ex_date,
            'dividend_amount': dividend_amount,
            'days_until': days_until,
            'timestamp': datetime.now().isoformat(),
            'priority': 'HIGH' if days_until <= 3 else 'MEDIUM'
        }

    def _format_telegram_message(self, alert_data: Dict) -> str:
        """Format alert for Telegram (Markdown)"""
        alert_type = alert_data['type']
        stock = alert_data['stock_code']

        lines = [f"*{alert_data['subject']}*", ""]

        if alert_type == 'PRICE_ALERT':
            lines.extend([
                f"📊 Stock: `{stock}`",
                f"💵 Current Price: Rp {alert_data['current_price']:,.0f}",
                f"🎯 Target Price: Rp {alert_data['target_price']:,.0f}",
                f"📈 Change: {alert_data['price_change_pct']:+.2f}%"
            ])

        elif alert_type == 'SIGNAL_ALERT':
            lines.extend([
                f"📊 Stock: `{stock}`",
                f"🎯 Signal: *{alert_data['signal']}*",
                f"📊 Confidence: {alert_data['confidence']:.0f}%"
            ])

            if alert_data.get('entry_price'):
                lines.append(f"💵 Entry: Rp {alert_data['entry_price']:,.0f}")
            if alert_data.get('target_price'):
                lines.append(f"🎯 Target: Rp {alert_data['target_price']:,.0f}")
            if alert_data.get('stop_loss'):
                lines.append(f"🛑 Stop Loss: Rp {alert_data['stop_loss']:,.0f}")

        elif alert_type == 'PATTERN_ALERT':
            lines.extend([
                f"📊 Stock: `{stock}`",
                f"📐 Pattern: *{alert_data['pattern_name']}*",
                f"🎯 Type: {alert_data['pattern_type']}",
                f"📊 Confidence: {alert_data['confidence']:.0f}%"
            ])

        elif alert_type == 'NEWS_ALERT':
            lines.extend([
                f"📊 Stock: `{stock}`",
                f"📰 Headline: _{alert_data['headline']}_",
                f"📊 Sentiment: {alert_data['sentiment']}",
                f"📡 Source: {alert_data['source']}"
            ])

        elif alert_type == 'DIVIDEND_ALERT':
            lines.extend([
                f"📊 Stock: `{stock}`",
                f"📅 Ex-Date: {alert_data['ex_date']}",
                f"💰 Amount: Rp {alert_data['dividend_amount']:,.0f}",
                f"⏰ Days Until: {alert_data['days_until']}"
            ])

        lines.extend(["", f"🕐 {alert_data['timestamp']}"])

        return "\n".join(lines)

    def _format_email_message(self, alert_data: Dict) -> str:
        """Format alert for Email (plain text)"""
        lines = [
            f"{alert_data['subject']}",
            "=" * 60,
            "",
            f"Stock: {alert_data['stock_code']}",
            f"Type: {alert_data['type'].replace('_', ' ').title()}",
            f"Time: {alert_data['timestamp']}",
            ""
        ]

        # Add type-specific details
        if alert_data['type'] == 'PRICE_ALERT':
            lines.extend([
                f"Current Price: Rp {alert_data['current_price']:,.0f}",
                f"Target Price: Rp {alert_data['target_price']:,.0f}",
                f"Price Change: {alert_data['price_change_pct']:+.2f}%"
            ])

        elif alert_data['type'] == 'SIGNAL_ALERT':
            lines.extend([
                f"Signal: {alert_data['signal']}",
                f"Confidence: {alert_data['confidence']:.0f}%"
            ])

            if alert_data.get('entry_price'):
                lines.append(f"Recommended Entry: Rp {alert_data['entry_price']:,.0f}")
            if alert_data.get('target_price'):
                lines.append(f"Target Price: Rp {alert_data['target_price']:,.0f}")
            if alert_data.get('stop_loss'):
                lines.append(f"Stop Loss: Rp {alert_data['stop_loss']:,.0f}")

        lines.extend([
            "",
            "=" * 60,
            "This is an automated alert from Indonesian Stock Prediction System",
            "Please do not reply to this email."
        ])

        return "\n".join(lines)


# Helper functions for easy alert creation
def send_price_alert(
    stock_code: str,
    current_price: float,
    target_price: float,
    telegram: bool = True,
    email: Optional[str] = None
) -> Dict:
    """Quick function to send price alert"""
    alert_system = AlertSystem()
    alert_data = alert_system.create_price_alert(stock_code, current_price, target_price)

    if email:
        alert_data['email_recipient'] = email

    channels = []
    if telegram:
        channels.append('telegram')
    if email:
        channels.append('email')

    return alert_system.send_multi_channel_alert(alert_data, channels)


def send_signal_alert(
    stock_code: str,
    signal: str,
    confidence: float,
    entry_price: Optional[float] = None,
    telegram: bool = True,
    email: Optional[str] = None
) -> Dict:
    """Quick function to send signal alert"""
    alert_system = AlertSystem()
    alert_data = alert_system.create_signal_alert(
        stock_code, signal, confidence, entry_price
    )

    if email:
        alert_data['email_recipient'] = email

    channels = []
    if telegram:
        channels.append('telegram')
    if email:
        channels.append('email')

    return alert_system.send_multi_channel_alert(alert_data, channels)
