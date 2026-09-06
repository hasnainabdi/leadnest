import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, date, timedelta
import os, hashlib, io, json
from fpdf import FPDF

st.set_page_config(page_title="LeadNest", page_icon="🪺", layout="wide", initial_sidebar_state="expanded")

DB_PATH = "crm_data.db"
ATTACH_DIR = "attachments"
os.makedirs(ATTACH_DIR, exist_ok=True)

# ===================== CURRENCIES =====================
CURRENCIES = {
    "USD": {"symbol": "$", "name": "US Dollar", "rate": 1.0},
    "EUR": {"symbol": "€", "name": "Euro", "rate": 0.92},
    "GBP": {"symbol": "£", "name": "British Pound", "rate": 0.79},
    "PKR": {"symbol": "Rs", "name": "Pakistani Rupee", "rate": 278.50},
    "INR": {"symbol": "₹", "name": "Indian Rupee", "rate": 83.50},
    "AED": {"symbol": "د.إ", "name": "UAE Dirham", "rate": 3.67},
    "SAR": {"symbol": "﷼", "name": "Saudi Riyal", "rate": 3.75},
    "CAD": {"symbol": "C$", "name": "Canadian Dollar", "rate": 1.36},
    "AUD": {"symbol": "A$", "name": "Australian Dollar", "rate": 1.53},
    "JPY": {"symbol": "¥", "name": "Japanese Yen", "rate": 149.50},
    "CNY": {"symbol": "¥", "name": "Chinese Yuan", "rate": 7.24},
    "CHF": {"symbol": "CHF", "name": "Swiss Franc", "rate": 0.88},
    "SGD": {"symbol": "S$", "name": "Singapore Dollar", "rate": 1.34},
    "MYR": {"symbol": "RM", "name": "Malaysian Ringgit", "rate": 4.72},
    "THB": {"symbol": "฿", "name": "Thai Baht", "rate": 35.80},
    "TRY": {"symbol": "₺", "name": "Turkish Lira", "rate": 32.50},
    "BRL": {"symbol": "R$", "name": "Brazilian Real", "rate": 5.05},
    "MXN": {"symbol": "MX$", "name": "Mexican Peso", "rate": 17.20},
    "ZAR": {"symbol": "R", "name": "South African Rand", "rate": 18.50},
    "EGP": {"symbol": "E£", "name": "Egyptian Pound", "rate": 48.50},
    "BDT": {"symbol": "৳", "name": "Bangladeshi Taka", "rate": 117.0},
    "IDR": {"symbol": "Rp", "name": "Indonesian Rupiah", "rate": 15800.0},
    "PHP": {"symbol": "₱", "name": "Philippine Peso", "rate": 56.50},
    "VND": {"symbol": "₫", "name": "Vietnamese Dong", "rate": 24500.0},
    "KRW": {"symbol": "₩", "name": "South Korean Won", "rate": 1330.0},
    "RUB": {"symbol": "₽", "name": "Russian Ruble", "rate": 92.0},
    "PLN": {"symbol": "zł", "name": "Polish Zloty", "rate": 4.0},
    "SEK": {"symbol": "kr", "name": "Swedish Krona", "rate": 10.50},
    "NOK": {"symbol": "kr", "name": "Norwegian Krone", "rate": 10.70},
    "DKK": {"symbol": "kr", "name": "Danish Krone", "rate": 6.90},
    "NZD": {"symbol": "NZ$", "name": "New Zealand Dollar", "rate": 1.65},
    "HKD": {"symbol": "HK$", "name": "Hong Kong Dollar", "rate": 7.82},
    "TWD": {"symbol": "NT$", "name": "Taiwan Dollar", "rate": 32.0},
    "ILS": {"symbol": "₪", "name": "Israeli Shekel", "rate": 3.70},
    "QAR": {"symbol": "QR", "name": "Qatari Riyal", "rate": 3.64},
    "KWD": {"symbol": "KD", "name": "Kuwaiti Dinar", "rate": 0.31},
    "BHD": {"symbol": "BD", "name": "Bahraini Dinar", "rate": 0.38},
    "OMR": {"symbol": "OMR", "name": "Omani Rial", "rate": 0.38},
    "NGN": {"symbol": "₦", "name": "Nigerian Naira", "rate": 1550.0},
    "KES": {"symbol": "KSh", "name": "Kenyan Shilling", "rate": 153.0},
}

# ===================== LANGUAGES =====================
LANGS = {
    "en": {"name": "English", "app_name": "LeadNest", "dashboard": "Dashboard", "clients": "Clients", "leads": "Leads",
           "projects": "Projects", "payments": "Payments", "expenses": "Expenses", "time": "Time Tracker",
           "tasks": "Tasks", "reminders": "Reminders", "reports": "Reports", "calendar": "Calendar",
           "settings": "Settings", "logout": "Logout", "login": "Login", "create_account": "Create Account",
           "client_portal": "Client Portal", "search": "Search", "add": "Add", "save": "Save", "delete": "Delete",
           "welcome": "Welcome", "total_clients": "Total Clients", "active_clients": "Active Clients",
           "total_leads": "Total Leads", "hot_leads": "Hot Leads", "active_projects": "Active Projects",
           "avg_rating": "Avg Rating", "earned": "Earned", "pending": "Pending", "expenses_label": "Expenses",
           "net_profit": "Net Profit", "overdue": "Overdue Follow-ups", "no_overdue": "No overdue items",
           "dark_mode": "Dark Mode", "language": "Language", "notifications": "Notifications",
           "activity_log": "Activity Log", "tax_report": "Tax Report", "profit_analysis": "Profit Analysis",
           "recurring": "Recurring Invoices", "schema": "Database Schema", "currency": "Currency",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "de": {"name": "Deutsch", "app_name": "LeadNest", "dashboard": "Dashboard", "clients": "Kunden", "leads": "Leads",
           "projects": "Projekte", "payments": "Zahlungen", "expenses": "Ausgaben", "time": "Zeiterfassung",
           "tasks": "Aufgaben", "reminders": "Erinnerungen", "reports": "Berichte", "calendar": "Kalender",
           "settings": "Einstellungen", "logout": "Abmelden", "login": "Anmelden", "create_account": "Konto erstellen",
           "client_portal": "Kundenportal", "search": "Suchen", "add": "Hinzufügen", "save": "Speichern", "delete": "Löschen",
           "welcome": "Willkommen", "total_clients": "Kunden gesamt", "active_clients": "Aktive Kunden",
           "total_leads": "Leads gesamt", "hot_leads": "Heiße Leads", "active_projects": "Aktive Projekte",
           "avg_rating": "Ø Bewertung", "earned": "Einnahmen", "pending": "Ausstehend", "expenses_label": "Ausgaben",
           "net_profit": "Nettogewinn", "overdue": "Überfällige Follow-ups", "no_overdue": "Keine überfälligen",
           "dark_mode": "Dunkelmodus", "language": "Sprache", "notifications": "Benachrichtigungen",
           "activity_log": "Aktivitätsprotokoll", "tax_report": "Steuerbericht", "profit_analysis": "Gewinnanalyse",
           "recurring": "Wiederkehrende Rechnungen", "schema": "Datenbankschema", "currency": "Währung",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "ur": {"name": "اردو", "app_name": "LeadNest", "dashboard": "ڈیش بورڈ", "clients": "کلائنٹس", "leads": "لیڈز",
           "projects": "پروجیکٹس", "payments": "ادائیگیاں", "expenses": "اخراجات", "time": "وقت ٹریکر",
           "tasks": "ٹاسکس", "reminders": "یاد دہانیاں", "reports": "رپورٹس", "calendar": "کیلنڈر",
           "settings": "ترتیبات", "logout": "لاگ آؤٹ", "login": "لاگ اِن", "create_account": "اکاؤنٹ بنائیں",
           "client_portal": "کلائنٹ پورٹل", "search": "تلاش", "add": "شامل", "save": "محفوظ", "delete": "حذف",
           "welcome": "خوش آمدید", "total_clients": "کل کلائنٹس", "active_clients": "فعال کلائنٹس",
           "total_leads": "کل لیڈز", "hot_leads": "ہاٹ لیڈز", "active_projects": "فعال پروجیکٹس",
           "avg_rating": "اوسط ریٹنگ", "earned": "کمائی", "pending": "زیر التوا", "expenses_label": "اخراجات",
           "net_profit": "خالص منافع", "overdue": "واجب الادا", "no_overdue": "کوئی واجب الادا نہیں",
           "dark_mode": "ڈارک موڈ", "language": "زبان", "notifications": "اطلاعات",
           "activity_log": "سرگرمی لاگ", "tax_report": "ٹیکس رپورٹ", "profit_analysis": "منافع تجزیہ",
           "recurring": "بار بار رسیدیں", "schema": "ڈیٹا بیس", "currency": "کرنسی",
           "copyright": "کاپی رائٹ LeadNest v2.3 • Orbit Galax"},
    "hi": {"name": "हिन्दी", "app_name": "LeadNest", "dashboard": "डैशबोर्ड", "clients": "क्लाइंट", "leads": "लीड्स",
           "projects": "प्रोजेक्ट", "payments": "भुगतान", "expenses": "खर्च", "time": "टाइम ट्रैकर",
           "tasks": "कार्य", "reminders": "रिमाइंडर", "reports": "रिपोर्ट", "calendar": "कैलेंडर",
           "settings": "सेटिंग्स", "logout": "लॉग आउट", "login": "लॉग इन", "create_account": "खाता बनाएं",
           "client_portal": "क्लाइंट पोर्टल", "search": "खोज", "add": "जोड़ें", "save": "सहेजें", "delete": "हटाएं",
           "welcome": "स्वागत", "total_clients": "कुल क्लाइंट", "active_clients": "सक्रिय क्लाइंट",
           "total_leads": "कुल लीड्स", "hot_leads": "हॉट लीड्स", "active_projects": "सक्रिय प्रोजेक्ट",
           "avg_rating": "औसत रेटिंग", "earned": "कमाई", "pending": "लंबित", "expenses_label": "खर्च",
           "net_profit": "शुद्ध लाभ", "overdue": "अतिदेय", "no_overdue": "कोई अतिदेय नहीं",
           "dark_mode": "डार्क मोड", "language": "भाषा", "notifications": "सूचनाएं",
           "activity_log": "गतिविधि लॉग", "tax_report": "टैक्स रिपोर्ट", "profit_analysis": "लाभ विश्लेषण",
           "recurring": "आवर्ती चालान", "schema": "डेटाबेस", "currency": "मुद्रा",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "he": {"name": "עברית", "app_name": "LeadNest", "dashboard": "לוח בקרה", "clients": "לקוחות", "leads": "לידים",
           "projects": "פרויקטים", "payments": "תשלומים", "expenses": "הוצאות", "time": "מעקב זמן",
           "tasks": "משימות", "reminders": "תזכורות", "reports": "דוחות", "calendar": "יומן",
           "settings": "הגדרות", "logout": "התנתק", "login": "התחבר", "create_account": "צור חשבון",
           "client_portal": "פורטל לקוחות", "search": "חיפוש", "add": "הוסף", "save": "שמור", "delete": "מחק",
           "welcome": "ברוך הבא", "total_clients": "סך לקוחות", "active_clients": "לקוחות פעילים",
           "total_leads": "סך לידים", "hot_leads": "לידים חמים", "active_projects": "פרויקטים פעילים",
           "avg_rating": "דירוג ממוצע", "earned": "הכנסות", "pending": "ממתין", "expenses_label": "הוצאות",
           "net_profit": "רווח נקי", "overdue": "באיחור", "no_overdue": "אין פריטים באיחור",
           "dark_mode": "מצב כהה", "language": "שפה", "notifications": "התראות",
           "activity_log": "יומן פעילות", "tax_report": "דוח מס", "profit_analysis": "ניתוח רווח",
           "recurring": "חשבוניות חוזרות", "schema": "סכמת מסד נתונים", "currency": "מטבע",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "ar": {"name": "العربية", "app_name": "LeadNest", "dashboard": "لوحة التحكم", "clients": "العملاء", "leads": "العملاء المحتملون",
           "projects": "المشاريع", "payments": "المدفوعات", "expenses": "المصروفات", "time": "تتبع الوقت",
           "tasks": "المهام", "reminders": "التذكيرات", "reports": "التقارير", "calendar": "التقويم",
           "settings": "الإعدادات", "logout": "تسجيل الخروج", "login": "تسجيل الدخول", "create_account": "إنشاء حساب",
           "client_portal": "بوابة العميل", "search": "بحث", "add": "إضافة", "save": "حفظ", "delete": "حذف",
           "welcome": "مرحباً", "total_clients": "إجمالي العملاء", "active_clients": "العملاء النشطون",
           "total_leads": "إجمالي العملاء المحتملين", "hot_leads": "عملاء محتملون ساخنون", "active_projects": "مشاريع نشطة",
           "avg_rating": "متوسط التقييم", "earned": "الأرباح", "pending": "قيد الانتظار", "expenses_label": "المصروفات",
           "net_profit": "صافي الربح", "overdue": "متأخر", "no_overdue": "لا يوجد متأخر",
           "dark_mode": "الوضع الداكن", "language": "اللغة", "notifications": "الإشعارات",
           "activity_log": "سجل النشاط", "tax_report": "تقرير الضرائب", "profit_analysis": "تحليل الأرباح",
           "recurring": "فواتير متكررة", "schema": "مخطط قاعدة البيانات", "currency": "العملة",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "fr": {"name": "Français", "app_name": "LeadNest", "dashboard": "Tableau de bord", "clients": "Clients", "leads": "Prospects",
           "projects": "Projets", "payments": "Paiements", "expenses": "Dépenses", "time": "Suivi du temps",
           "tasks": "Tâches", "reminders": "Rappels", "reports": "Rapports", "calendar": "Calendrier",
           "settings": "Paramètres", "logout": "Déconnexion", "login": "Connexion", "create_account": "Créer un compte",
           "client_portal": "Portail client", "search": "Rechercher", "add": "Ajouter", "save": "Enregistrer", "delete": "Supprimer",
           "welcome": "Bienvenue", "total_clients": "Total clients", "active_clients": "Clients actifs",
           "total_leads": "Total prospects", "hot_leads": "Prospects chauds", "active_projects": "Projets actifs",
           "avg_rating": "Note moyenne", "earned": "Gagné", "pending": "En attente", "expenses_label": "Dépenses",
           "net_profit": "Bénéfice net", "overdue": "En retard", "no_overdue": "Aucun en retard",
           "dark_mode": "Mode sombre", "language": "Langue", "notifications": "Notifications",
           "activity_log": "Journal d'activité", "tax_report": "Rapport fiscal", "profit_analysis": "Analyse des profits",
           "recurring": "Factures récurrentes", "schema": "Schéma BDD", "currency": "Devise",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "es": {"name": "Español", "app_name": "LeadNest", "dashboard": "Panel", "clients": "Clientes", "leads": "Leads",
           "projects": "Proyectos", "payments": "Pagos", "expenses": "Gastos", "time": "Control de tiempo",
           "tasks": "Tareas", "reminders": "Recordatorios", "reports": "Informes", "calendar": "Calendario",
           "settings": "Ajustes", "logout": "Cerrar sesión", "login": "Iniciar sesión", "create_account": "Crear cuenta",
           "client_portal": "Portal del cliente", "search": "Buscar", "add": "Añadir", "save": "Guardar", "delete": "Eliminar",
           "welcome": "Bienvenido", "total_clients": "Total clientes", "active_clients": "Clientes activos",
           "total_leads": "Total leads", "hot_leads": "Leads calientes", "active_projects": "Proyectos activos",
           "avg_rating": "Valoración media", "earned": "Ganado", "pending": "Pendiente", "expenses_label": "Gastos",
           "net_profit": "Beneficio neto", "overdue": "Vencidos", "no_overdue": "Ninguno vencido",
           "dark_mode": "Modo oscuro", "language": "Idioma", "notifications": "Notificaciones",
           "activity_log": "Registro de actividad", "tax_report": "Informe fiscal", "profit_analysis": "Análisis de beneficios",
           "recurring": "Facturas recurrentes", "schema": "Esquema BD", "currency": "Moneda",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "pt": {"name": "Português", "app_name": "LeadNest", "dashboard": "Painel", "clients": "Clientes", "leads": "Leads",
           "projects": "Projetos", "payments": "Pagamentos", "expenses": "Despesas", "time": "Controle de tempo",
           "tasks": "Tarefas", "reminders": "Lembretes", "reports": "Relatórios", "calendar": "Calendário",
           "settings": "Configurações", "logout": "Sair", "login": "Entrar", "create_account": "Criar conta",
           "client_portal": "Portal do cliente", "search": "Pesquisar", "add": "Adicionar", "save": "Salvar", "delete": "Excluir",
           "welcome": "Bem-vindo", "total_clients": "Total de clientes", "active_clients": "Clientes ativos",
           "total_leads": "Total de leads", "hot_leads": "Leads quentes", "active_projects": "Projetos ativos",
           "avg_rating": "Avaliação média", "earned": "Ganho", "pending": "Pendente", "expenses_label": "Despesas",
           "net_profit": "Lucro líquido", "overdue": "Atrasados", "no_overdue": "Nenhum atrasado",
           "dark_mode": "Modo escuro", "language": "Idioma", "notifications": "Notificações",
           "activity_log": "Log de atividades", "tax_report": "Relatório fiscal", "profit_analysis": "Análise de lucro",
           "recurring": "Faturas recorrentes", "schema": "Esquema BD", "currency": "Moeda",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "tr": {"name": "Türkçe", "app_name": "LeadNest", "dashboard": "Panel", "clients": "Müşteriler", "leads": "Potansiyel",
           "projects": "Projeler", "payments": "Ödemeler", "expenses": "Giderler", "time": "Zaman Takibi",
           "tasks": "Görevler", "reminders": "Hatırlatıcılar", "reports": "Raporlar", "calendar": "Takvim",
           "settings": "Ayarlar", "logout": "Çıkış", "login": "Giriş", "create_account": "Hesap Oluştur",
           "client_portal": "Müşteri Portalı", "search": "Ara", "add": "Ekle", "save": "Kaydet", "delete": "Sil",
           "welcome": "Hoş geldiniz", "total_clients": "Toplam Müşteri", "active_clients": "Aktif Müşteriler",
           "total_leads": "Toplam Potansiyel", "hot_leads": "Sıcak Potansiyeller", "active_projects": "Aktif Projeler",
           "avg_rating": "Ort. Puan", "earned": "Kazanılan", "pending": "Bekleyen", "expenses_label": "Giderler",
           "net_profit": "Net Kâr", "overdue": "Gecikmiş", "no_overdue": "Gecikmiş yok",
           "dark_mode": "Karanlık Mod", "language": "Dil", "notifications": "Bildirimler",
           "activity_log": "Aktivite Günlüğü", "tax_report": "Vergi Raporu", "profit_analysis": "Kâr Analizi",
           "recurring": "Tekrarlayan Faturalar", "schema": "Veritabanı Şeması", "currency": "Para Birimi",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "zh": {"name": "中文", "app_name": "LeadNest", "dashboard": "仪表板", "clients": "客户", "leads": "潜在客户",
           "projects": "项目", "payments": "付款", "expenses": "支出", "time": "时间跟踪",
           "tasks": "任务", "reminders": "提醒", "reports": "报告", "calendar": "日历",
           "settings": "设置", "logout": "登出", "login": "登录", "create_account": "创建账户",
           "client_portal": "客户门户", "search": "搜索", "add": "添加", "save": "保存", "delete": "删除",
           "welcome": "欢迎", "total_clients": "客户总数", "active_clients": "活跃客户",
           "total_leads": "潜在客户总数", "hot_leads": "热门潜在客户", "active_projects": "进行中项目",
           "avg_rating": "平均评分", "earned": "收入", "pending": "待处理", "expenses_label": "支出",
           "net_profit": "净利润", "overdue": "逾期", "no_overdue": "无逾期",
           "dark_mode": "深色模式", "language": "语言", "notifications": "通知",
           "activity_log": "活动日志", "tax_report": "税务报告", "profit_analysis": "利润分析",
           "recurring": "定期发票", "schema": "数据库架构", "currency": "货币",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "ja": {"name": "日本語", "app_name": "LeadNest", "dashboard": "ダッシュボード", "clients": "クライアント", "leads": "リード",
           "projects": "プロジェクト", "payments": "支払い", "expenses": "経費", "time": "時間管理",
           "tasks": "タスク", "reminders": "リマインダー", "reports": "レポート", "calendar": "カレンダー",
           "settings": "設定", "logout": "ログアウト", "login": "ログイン", "create_account": "アカウント作成",
           "client_portal": "クライアントポータル", "search": "検索", "add": "追加", "save": "保存", "delete": "削除",
           "welcome": "ようこそ", "total_clients": "クライアント総数", "active_clients": "アクティブ",
           "total_leads": "リード総数", "hot_leads": "ホットリード", "active_projects": "進行中プロジェクト",
           "avg_rating": "平均評価", "earned": "収益", "pending": "保留中", "expenses_label": "経費",
           "net_profit": "純利益", "overdue": "期限切れ", "no_overdue": "期限切れなし",
           "dark_mode": "ダークモード", "language": "言語", "notifications": "通知",
           "activity_log": "アクティビティログ", "tax_report": "税務レポート", "profit_analysis": "利益分析",
           "recurring": "定期請求書", "schema": "データベーススキーマ", "currency": "通貨",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "ko": {"name": "한국어", "app_name": "LeadNest", "dashboard": "대시보드", "clients": "고객", "leads": "리드",
           "projects": "프로젝트", "payments": "결제", "expenses": "비용", "time": "시간 추적",
           "tasks": "작업", "reminders": "알림", "reports": "보고서", "calendar": "캘린더",
           "settings": "설정", "logout": "로그아웃", "login": "로그인", "create_account": "계정 만들기",
           "client_portal": "고객 포털", "search": "검색", "add": "추가", "save": "저장", "delete": "삭제",
           "welcome": "환영합니다", "total_clients": "총 고객", "active_clients": "활성 고객",
           "total_leads": "총 리드", "hot_leads": "핫 리드", "active_projects": "진행 중 프로젝트",
           "avg_rating": "평균 평점", "earned": "수익", "pending": "대기 중", "expenses_label": "비용",
           "net_profit": "순이익", "overdue": "연체", "no_overdue": "연체 없음",
           "dark_mode": "다크 모드", "language": "언어", "notifications": "알림",
           "activity_log": "활동 로그", "tax_report": "세금 보고서", "profit_analysis": "수익 분석",
           "recurring": "정기 청구서", "schema": "데이터베이스 스키마", "currency": "통화",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
    "ru": {"name": "Русский", "app_name": "LeadNest", "dashboard": "Панель", "clients": "Клиенты", "leads": "Лиды",
           "projects": "Проекты", "payments": "Платежи", "expenses": "Расходы", "time": "Учёт времени",
           "tasks": "Задачи", "reminders": "Напоминания", "reports": "Отчёты", "calendar": "Календарь",
           "settings": "Настройки", "logout": "Выход", "login": "Вход", "create_account": "Создать аккаунт",
           "client_portal": "Клиентский портал", "search": "Поиск", "add": "Добавить", "save": "Сохранить", "delete": "Удалить",
           "welcome": "Добро пожаловать", "total_clients": "Всего клиентов", "active_clients": "Активные",
           "total_leads": "Всего лидов", "hot_leads": "Горячие лиды", "active_projects": "Активные проекты",
           "avg_rating": "Средний рейтинг", "earned": "Заработано", "pending": "Ожидает", "expenses_label": "Расходы",
           "net_profit": "Чистая прибыль", "overdue": "Просрочено", "no_overdue": "Нет просроченных",
           "dark_mode": "Тёмный режим", "language": "Язык", "notifications": "Уведомления",
           "activity_log": "Журнал действий", "tax_report": "Налоговый отчёт", "profit_analysis": "Анализ прибыли",
           "recurring": "Повторяющиеся счета", "schema": "Схема БД", "currency": "Валюта",
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax"},
}

def t(key):
    lang = st.session_state.get("lang", "en")
    return LANGS.get(lang, LANGS["en"]).get(key, LANGS["en"].get(key, key))

def get_currency():
    code = st.session_state.get("currency", "USD")
    return CURRENCIES.get(code, CURRENCIES["USD"])

def fmt_money(usd_amount):
    cur = get_currency()
    val = float(usd_amount or 0) * cur["rate"]
    if cur["rate"] >= 100:
        return f"{cur['symbol']}{val:,.0f}"
    return f"{cur['symbol']}{val:,.2f}"

def fmt_usd(v):
    return f"${float(v or 0):,.2f}"

# ===================== DB =====================
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, email TEXT UNIQUE,
        password_hash TEXT, full_name TEXT, role TEXT DEFAULT 'admin', created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS clients (
        id TEXT PRIMARY KEY, name TEXT, company TEXT, email TEXT, phone TEXT, country TEXT,
        platform TEXT, service TEXT, start_date TEXT, status TEXT, lifetime_value REAL,
        payment_terms TEXT, source_lead TEXT, rating INTEGER, notes TEXT, portal_password TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS leads (
        id TEXT PRIMARY KEY, name TEXT, company TEXT, email TEXT, phone TEXT, country TEXT,
        platform TEXT, stage TEXT, priority TEXT, estimated_value REAL, next_followup TEXT,
        last_contact TEXT, notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY, name TEXT, client_id TEXT, client_name TEXT, platform TEXT,
        budget REAL, start_date TEXT, status TEXT, deadline TEXT, progress INTEGER, notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
        id TEXT PRIMARY KEY, project_id TEXT, client_name TEXT, description TEXT, invoice_date TEXT,
        amount REAL, due_date TEXT, status TEXT, payment_date TEXT, method TEXT, notes TEXT,
        is_recurring INTEGER DEFAULT 0, recurring_interval TEXT, next_invoice_date TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id TEXT PRIMARY KEY, date TEXT, category TEXT, description TEXT, amount REAL, method TEXT, notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS time_logs (
        id TEXT PRIMARY KEY, project_id TEXT, date TEXT, client_name TEXT, task TEXT, hours REAL, billable TEXT, notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, related_to TEXT, due_date TEXT,
        email_to TEXT, status TEXT DEFAULT 'Pending', created_at TEXT, notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, related_to TEXT, due_date TEXT,
        priority TEXT DEFAULT 'Medium', status TEXT DEFAULT 'Todo', assigned_to TEXT,
        created_at TEXT, notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, action TEXT, entity TEXT,
        entity_id TEXT, details TEXT, created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, entity_type TEXT, entity_id TEXT,
        filename TEXT, filepath TEXT, uploaded_by TEXT, uploaded_at TEXT)""")
    defaults = {"exchange_rate":"278.50","hourly_rate":"25","monthly_goal":"2500","hours_goal":"120",
                "company_name":"LeadNest","company_email":"","company_phone":"","lang":"en","currency":"USD"}
    for k,v in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings (key,value) VALUES (?,?)",(k,v))
    conn.commit(); conn.close()

def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()
def get_setting(k,d=""):
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT value FROM settings WHERE key=?",(k,))
    r=c.fetchone(); conn.close(); return r[0] if r else d
def set_setting(k,v):
    conn=get_conn(); c=conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)",(k,str(v)))
    conn.commit(); conn.close()
def load_table(t):
    conn=get_conn(); df=pd.read_sql(f"SELECT * FROM {t}",conn); conn.close(); return df
def save_row(table, data):
    conn=get_conn(); cols=", ".join(data.keys()); ph=", ".join(["?"]*len(data))
    c=conn.cursor(); c.execute(f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({ph})", list(data.values()))
    conn.commit(); conn.close()
def delete_row(table, idv, col="id"):
    conn=get_conn(); c=conn.cursor(); c.execute(f"DELETE FROM {table} WHERE {col}=?",(idv,))
    conn.commit(); conn.close()
def log_activity(user, action, entity, entity_id, details=""):
    conn=get_conn(); c=conn.cursor()
    c.execute("INSERT INTO activity_log (user,action,entity,entity_id,details,created_at) VALUES (?,?,?,?,?,?)",
              (user,action,entity,entity_id,details,datetime.now().isoformat()))
    conn.commit(); conn.close()
def next_id(table, prefix):
    df=load_table(table)
    if df.empty: return f"{prefix}-001"
    nums=[]
    for x in df["id"]:
        try: nums.append(int(str(x).split("-")[-1]))
        except: pass
    return f"{prefix}-{(max(nums)+1 if nums else 1):03d}"
def next_invoice_id():
    df=load_table("payments"); year=datetime.now().year
    if df.empty: return f"INV-{year}-001"
    nums=[]
    for x in df["id"]:
        try:
            p=str(x).split("-")
            if len(p)>=3 and p[1]==str(year): nums.append(int(p[2]))
        except: pass
    return f"INV-{year}-{(max(nums)+1 if nums else 1):03d}"
def user_exists():
    conn=get_conn(); c=conn.cursor(); c.execute("SELECT COUNT(*) FROM users")
    n=c.fetchone()[0]; conn.close(); return n>0
def create_user(username, email, password, full_name, role="admin"):
    conn=get_conn(); c=conn.cursor()
    try:
        c.execute("INSERT INTO users (username,email,password_hash,full_name,role,created_at) VALUES (?,?,?,?,?,?)",
                  (username,email,hash_pw(password),full_name,role,datetime.now().isoformat()))
        conn.commit(); conn.close(); return True
    except: conn.close(); return False
def authenticate(username, password):
    conn=get_conn(); c=conn.cursor()
    c.execute("SELECT id,username,full_name,role,email FROM users WHERE username=? AND password_hash=?",
              (username, hash_pw(password)))
    r=c.fetchone(); conn.close()
    return {"id":r[0],"username":r[1],"full_name":r[2],"role":r[3],"email":r[4]} if r else None

# ===================== PDF =====================
class InvoicePDF(FPDF):
    def header(self):
        self.set_font("Helvetica","B",16)
        self.cell(0,10, get_setting("company_name","LeadNest"), ln=True)
        self.set_font("Helvetica","",9)
        self.cell(0,5, get_setting("company_email",""), ln=True)
        self.ln(4)
    def footer(self):
        self.set_y(-12); self.set_font("Helvetica","I",8)
        self.cell(0,8,"Copyright by LeadNest v2.3 - Built with Orbit Galax", align="C")

def generate_invoice_pdf(row, client=None):
    pdf=InvoicePDF(); pdf.add_page()
    pdf.set_font("Helvetica","B",14); pdf.cell(0,10,"INVOICE",ln=True,align="R")
    pdf.set_font("Helvetica","",10)
    pdf.cell(0,6,f"Invoice #: {row.get('id','')}",ln=True,align="R")
    pdf.cell(0,6,f"Date: {row.get('invoice_date','')}",ln=True,align="R")
    pdf.cell(0,6,f"Due: {row.get('due_date','')}",ln=True,align="R"); pdf.ln(6)
    pdf.set_font("Helvetica","B",11); pdf.cell(0,7,"Bill To:",ln=True)
    pdf.set_font("Helvetica","",10); pdf.cell(0,5, str(row.get("client_name","")), ln=True)
    if client is not None:
        pdf.cell(0,5, str(client.get("company","")), ln=True)
        pdf.cell(0,5, str(client.get("email","")), ln=True)
    pdf.ln(8)
    pdf.set_fill_color(30,64,175); pdf.set_text_color(255,255,255); pdf.set_font("Helvetica","B",10)
    pdf.cell(100,8,"Description",border=1,fill=True); pdf.cell(40,8,"Project",border=1,fill=True)
    pdf.cell(40,8,"Amount",border=1,fill=True,align="R"); pdf.ln()
    pdf.set_text_color(0,0,0); pdf.set_font("Helvetica","",10)
    amt=float(row.get("amount",0) or 0)
    pdf.cell(100,8,str(row.get("description","")),border=1)
    pdf.cell(40,8,str(row.get("project_id","")),border=1)
    pdf.cell(40,8,f"${amt:,.2f}",border=1,align="R"); pdf.ln()
    pdf.set_font("Helvetica","B",11)
    pdf.cell(140,8,"Total",border=1,align="R"); pdf.cell(40,8,f"${amt:,.2f}",border=1,align="R")
    pdf.ln(12); pdf.set_font("Helvetica","",9)
    pdf.cell(0,5,f"Status: {row.get('status','')}  |  Method: {row.get('method','')}",ln=True)
    return bytes(pdf.output())

def si(s):
    m={"Active":"●","Completed":"●","On Hold":"●","Cancelled":"●","In Progress":"●","Not Started":"○",
       "Paid":"●","Pending":"●","Partial":"●","Overdue":"●","Hot":"▲","Warm":"■","Cold":"▼",
       "Won":"✓","Lost":"✗","New":"+","Contacted":"→","Proposal Sent":"▸","Negotiation":"⇔",
       "Todo":"○","Done":"●"}
    return m.get(s,"•")

def apply_css():
    dark = st.session_state.get("dark_mode", False)
    if dark:
        st.markdown("""<style>
        .stApp{background:#0f172a;color:#e2e8f0}
        section[data-testid="stSidebar"]{background:#1e293b!important}
        .stMetric{background:#1e293b;padding:14px;border-radius:12px;border:1px solid #334155}
        div[data-testid="stMetricValue"]{color:#38bdf8!important;font-size:1.35rem!important}
        h1,h2,h3{color:#f1f5f9!important}
        .stButton>button{border-radius:8px}
        .block-container{padding-top:1.2rem}
        </style>""", unsafe_allow_html=True)
    else:
        # FIXED light mode - soft gray, readable, not pure white
        st.markdown("""<style>
        .stApp{background:#f1f5f9;color:#0f172a}
        section[data-testid="stSidebar"]{background:#e2e8f0!important}
        .stMetric{background:#ffffff;padding:14px;border-radius:12px;border:1px solid #cbd5e1;
                  box-shadow:0 1px 3px rgba(0,0,0,0.06)}
        div[data-testid="stMetricValue"]{color:#1e40af!important;font-size:1.35rem!important}
        h1,h2,h3{color:#0f172a!important}
        .stButton>button{border-radius:8px}
        .block-container{padding-top:1.2rem;background:#f1f5f9}
        div[data-testid="stDataFrame"]{background:#ffffff;border-radius:8px}
        .stTextInput>div>div>input, .stSelectbox>div>div{background:#ffffff}
        </style>""", unsafe_allow_html=True)

# ===================== INIT =====================
init_db()
for k,v in [("logged_in",False),("user",None),("dark_mode",False),("client_portal",False),
            ("portal_client",None),("lang","en"),("currency","USD")]:
    if k not in st.session_state: st.session_state[k]=v
# load saved prefs
if "prefs_loaded" not in st.session_state:
    st.session_state.lang = get_setting("lang","en")
    st.session_state.currency = get_setting("currency","USD")
    st.session_state.prefs_loaded = True

apply_css()

# Seed minimal if empty
if load_table("clients").empty:
    for r in [
        ("CL-001","Ahmed Khan","TechNova","ahmed@technova.com","+92 300 1234567","Pakistan","Upwork","Web Development","2025-11-15","Active",2450,"50% Advance","",5,"",""),
        ("CL-002","Sarah Johnson","Bloom Digital","sarah@bloomdigital.co","+1 415 555 0198","USA","Fiverr","Branding","2025-10-05","Completed",890,"Full","",5,"",""),
        ("CL-003","Mohammed Al-Farsi","Gulf Traders","m.alfarsi@gulftraders.ae","+971 50 987 6543","UAE","Direct / Referral","E-commerce","2026-01-20","Active",4200,"Milestones","",4,"",""),
    ]:
        save_row("clients", dict(zip(["id","name","company","email","phone","country","platform","service","start_date","status","lifetime_value","payment_terms","source_lead","rating","notes","portal_password"], r)))
    for r in [
        ("LD-004","Lucas Meyer","Meyer Apps","lucas@meyerapps.de","+49 170 1234567","Germany","LinkedIn","Proposal Sent","Hot",3200,"2026-09-03","2026-09-02","React"),
        ("LD-008","Emily Chen","NovaStart AI","emily@novastart.ai","+1 650 555 8844","USA","Upwork","Contacted","Warm",5500,"2026-09-12","2026-09-05","AI"),
    ]:
        save_row("leads", dict(zip(["id","name","company","email","phone","country","platform","stage","priority","estimated_value","next_followup","last_contact","notes"], r)))
    for r in [
        ("PR-001","TechNova Website","CL-001","Ahmed Khan","Upwork",1450,"2025-11-20","Completed","2025-12-20",100,""),
        ("PR-004","Gulf Shopify","CL-003","Mohammed Al-Farsi","Direct / Referral",2800,"2026-01-25","In Progress","2026-03-20",45,""),
    ]:
        save_row("projects", dict(zip(["id","name","client_id","client_name","platform","budget","start_date","status","deadline","progress","notes"], r)))
    for r in [
        ("INV-2026-001","PR-004","Mohammed Al-Farsi","Shopify Advance","2026-01-25",840,"2026-02-05","Paid","2026-01-28","Wise","",0,"",""),
        ("INV-2026-002","PR-004","Mohammed Al-Farsi","Milestone 2","2026-02-20",980,"2026-03-01","Pending","","","",0,"",""),
    ]:
        save_row("payments", dict(zip(["id","project_id","client_name","description","invoice_date","amount","due_date","status","payment_date","method","notes","is_recurring","recurring_interval","next_invoice_date"], r)))

# ===================== AUTH =====================
def show_login():
    st.markdown("## LeadNest")
    st.caption("Built with Orbit Galax")
    tab1,tab2,tab3 = st.tabs([t("login"), t("create_account"), t("client_portal")])
    with tab1:
        if not user_exists(): st.info("Create an admin account first.")
        else:
            with st.form("lf"):
                u=st.text_input("Username"); p=st.text_input("Password",type="password")
                if st.form_submit_button(t("login"), type="primary", use_container_width=True):
                    user=authenticate(u,p)
                    if user:
                        st.session_state.logged_in=True; st.session_state.user=user
                        st.session_state.client_portal=False
                        log_activity(user["username"],"LOGIN","system","","")
                        st.rerun()
                    else: st.error("Invalid credentials")
    with tab2:
        with st.form("rf"):
            fn=st.text_input("Full Name"); u=st.text_input("Username")
            e=st.text_input("Email"); p=st.text_input("Password",type="password")
            p2=st.text_input("Confirm",type="password")
            role=st.selectbox("Role",["admin","manager","staff"])
            if st.form_submit_button(t("create_account"), type="primary", use_container_width=True):
                if not all([fn,u,e,p]): st.error("All required")
                elif p!=p2: st.error("Mismatch")
                elif create_user(u,e,p,fn,role): st.success("Created! Please login.")
                else: st.error("Username/email exists")
    with tab3:
        with st.form("pf"):
            em=st.text_input("Client Email"); pp=st.text_input("Portal Password",type="password")
            if st.form_submit_button("Enter Portal", type="primary", use_container_width=True):
                cl=load_table("clients")
                m=cl[(cl["email"]==em)&(cl["portal_password"]==pp)] if not cl.empty else pd.DataFrame()
                if not m.empty and pp:
                    st.session_state.client_portal=True; st.session_state.portal_client=m.iloc[0].to_dict()
                    st.session_state.logged_in=True; st.rerun()
                else: st.error("Invalid portal login")

def show_client_portal():
    client=st.session_state.portal_client
    st.title(f"Client Portal — {client['name']}")
    if st.sidebar.button(t("logout")):
        st.session_state.logged_in=False; st.session_state.client_portal=False; st.session_state.portal_client=None; st.rerun()
    st.subheader("Projects")
    projs=load_table("projects")
    mine=projs[projs["client_name"]==client["name"]] if not projs.empty else pd.DataFrame()
    if not mine.empty:
        for _,p in mine.iterrows():
            with st.expander(f"{si(p['status'])} {p['name']} — {p['status']} ({p['progress']}%)"):
                st.progress(int(p["progress"] or 0)/100)
                st.write(f"Budget: **{fmt_money(p['budget'])}** | Deadline: **{p['deadline']}**")
    st.subheader("Invoices")
    pays=load_table("payments")
    myp=pays[pays["client_name"]==client["name"]] if not pays.empty else pd.DataFrame()
    if not myp.empty:
        for _,inv in myp.iterrows():
            with st.expander(f"{si(inv['status'])} {inv['id']} — {fmt_money(inv['amount'])}"):
                st.write(inv["description"])
                if st.button("PDF", key=f"cp_{inv['id']}"):
                    cl=load_table("clients"); ci=cl[cl["name"]==client["name"]]
                    ci=ci.iloc[0] if not ci.empty else None
                    pdfb=generate_invoice_pdf(inv.to_dict(), ci)
                    st.download_button("Download", data=pdfb, file_name=f"{inv['id']}.pdf", mime="application/pdf")

if not st.session_state.logged_in:
    show_login(); st.stop()
if st.session_state.client_portal:
    show_client_portal(); st.stop()

user=st.session_state.user
role=user.get("role","admin")

# ===================== SIDEBAR =====================
st.sidebar.markdown("### LeadNest")
st.sidebar.caption(f"v2.3  |  {user['full_name']} ({role})")

# Language
lang_options = {v["name"]: k for k,v in LANGS.items()}
lang_names = list(lang_options.keys())
current_lang_name = LANGS.get(st.session_state.lang, LANGS["en"])["name"]
sel_lang = st.sidebar.selectbox(t("language"), lang_names, index=lang_names.index(current_lang_name) if current_lang_name in lang_names else 0)
new_lang = lang_options[sel_lang]
if new_lang != st.session_state.lang:
    st.session_state.lang = new_lang
    set_setting("lang", new_lang)
    st.rerun()

# Currency
cur_codes = list(CURRENCIES.keys())
cur_labels = [f"{c} — {CURRENCIES[c]['name']}" for c in cur_codes]
cur_idx = cur_codes.index(st.session_state.currency) if st.session_state.currency in cur_codes else 0
sel_cur = st.sidebar.selectbox(t("currency"), cur_labels, index=cur_idx)
new_cur = sel_cur.split(" — ")[0]
if new_cur != st.session_state.currency:
    st.session_state.currency = new_cur
    set_setting("currency", new_cur)
    st.rerun()

# Dark mode
dm = st.sidebar.toggle(t("dark_mode"), value=st.session_state.dark_mode)
if dm != st.session_state.dark_mode:
    st.session_state.dark_mode = dm; st.rerun()

# Notifications
leads_df=load_table("leads"); tasks_df=load_table("tasks"); rem_df=load_table("reminders")
notif=0
if not leads_df.empty:
    ld=leads_df.copy(); ld["nf"]=pd.to_datetime(ld["next_followup"],errors="coerce")
    notif += len(ld[(ld["nf"]<pd.Timestamp(date.today()))&(~ld["stage"].isin(["Won","Lost"]))])
if not tasks_df.empty: notif += len(tasks_df[tasks_df["status"]!="Done"])
if not rem_df.empty: notif += len(rem_df[rem_df["status"]=="Pending"])
st.sidebar.markdown(f"**{t('notifications')}**  `{notif}`")

pages = [t("dashboard"), t("clients"), t("leads"), t("projects"), t("payments"),
         t("expenses"), t("time"), t("tasks"), t("reminders"), t("calendar"),
         t("reports"), t("activity_log"), t("settings"), t("schema")]
if role == "staff":
    pages = [p for p in pages if p not in [t("settings"), t("schema")]]

page = st.sidebar.radio("Nav", pages, label_visibility="collapsed")
st.sidebar.markdown("---")
cur = get_currency()
st.sidebar.caption(f"Display: {cur['symbol']} {cur['name']}")
if st.sidebar.button(t("logout"), use_container_width=True):
    log_activity(user["username"],"LOGOUT","system","","")
    st.session_state.logged_in=False; st.session_state.user=None; st.rerun()
st.sidebar.caption(t("copyright"))
st.sidebar.caption("orbitgalax.space-z.ai")

# ===================== DASHBOARD =====================
if page == t("dashboard"):
    st.title(t("dashboard"))
    clients=load_table("clients"); leads=load_table("leads"); projects=load_table("projects")
    payments=load_table("payments"); expenses=load_table("expenses"); times=load_table("time_logs")
    te=payments[payments["status"]=="Paid"]["amount"].sum() if not payments.empty else 0
    pen=payments[payments["status"].isin(["Pending","Overdue"])]["amount"].sum() if not payments.empty else 0
    tex=expenses["amount"].sum() if not expenses.empty else 0
    profit=te-tex
    avg_r=clients["rating"].mean() if not clients.empty else 0
    c1,c2,c3,c4,c5,c6=st.columns(6)
    c1.metric(t("total_clients"), len(clients))
    c2.metric(t("active_clients"), len(clients[clients["status"]=="Active"]) if not clients.empty else 0)
    c3.metric(t("total_leads"), len(leads))
    c4.metric(t("hot_leads"), len(leads[leads["priority"]=="Hot"]) if not leads.empty else 0)
    c5.metric(t("active_projects"), len(projects[projects["status"]=="In Progress"]) if not projects.empty else 0)
    c6.metric(t("avg_rating"), f"{avg_r:.1f}" if avg_r else "-")
    st.markdown("---")
    f1,f2,f3,f4=st.columns(4)
    f1.metric(t("earned"), fmt_money(te), fmt_usd(te))
    f2.metric(t("pending"), fmt_money(pen), fmt_usd(pen))
    f3.metric(t("expenses_label"), fmt_money(tex), fmt_usd(tex))
    f4.metric(t("net_profit"), fmt_money(profit), fmt_usd(profit))
    # charts
    st.markdown("---")
    col1,col2,col3=st.columns(3)
    with col1:
        st.subheader("Client Status")
        if not clients.empty:
            fig=px.pie(clients,names="status",hole=0.45,color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(margin=dict(t=10,b=10,l=10,r=10),height=250)
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Lead Pipeline")
        if not leads.empty:
            fig=px.bar(leads.groupby("stage").size().reset_index(name="count"),x="stage",y="count",color="count",color_continuous_scale="Teal")
            fig.update_layout(margin=dict(t=10,b=10,l=10,r=10),height=250,showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    with col3:
        st.subheader("Revenue by Platform")
        if not projects.empty:
            rev=projects.groupby("platform")["budget"].sum().reset_index()
            fig=px.bar(rev,x="platform",y="budget",text_auto=".0f",color="budget",color_continuous_scale="Blues")
            fig.update_layout(margin=dict(t=10,b=10,l=10,r=10),height=250,showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    st.subheader(t("overdue"))
    if not leads.empty:
        ld=leads.copy(); ld["nf"]=pd.to_datetime(ld["next_followup"],errors="coerce")
        od=ld[(ld["nf"]<pd.Timestamp(date.today()))&(~ld["stage"].isin(["Won","Lost"]))]
        if not od.empty: st.dataframe(od[["id","name","company","stage","priority","next_followup"]], use_container_width=True, hide_index=True)
        else: st.success(t("no_overdue"))

# ===================== CLIENTS =====================
elif page == t("clients"):
    st.title(t("clients"))
    tab1,tab2=st.tabs(["All", f"{t('add')} / Edit"])
    with tab1:
        df=load_table("clients")
        if not df.empty:
            q=st.text_input(t("search"))
            f1,f2=st.columns(2)
            sf=f1.multiselect("Status", df["status"].unique().tolist())
            pf=f2.multiselect("Platform", df["platform"].unique().tolist())
            filtered=df.copy()
            if q: filtered=filtered[filtered.apply(lambda r: q.lower() in str(r.values).lower(), axis=1)]
            if sf: filtered=filtered[filtered["status"].isin(sf)]
            if pf: filtered=filtered[filtered["platform"].isin(pf)]
            filtered["S"]=filtered["status"].apply(lambda x: f"{si(x)} {x}")
            st.dataframe(filtered[["id","name","company","email","country","platform","S","lifetime_value","rating"]], use_container_width=True, hide_index=True)
            did=st.selectbox(t("delete"),[""]+df["id"].tolist())
            if did and st.button(t("delete"), type="secondary"):
                delete_row("clients",did); log_activity(user["username"],"DELETE","client",did,""); st.rerun()
        else: st.info("No data")
    with tab2:
        df=load_table("clients")
        eid=st.selectbox("Edit",[""]+(df["id"].tolist() if not df.empty else []))
        ex=df[df["id"]==eid].iloc[0].to_dict() if eid else {}
        with st.form("cf"):
            c1,c2=st.columns(2)
            with c1:
                cid=st.text_input("ID", value=ex.get("id") or next_id("clients","CL"))
                name=st.text_input("Name *", value=ex.get("name",""))
                company=st.text_input("Company", value=ex.get("company",""))
                email=st.text_input("Email", value=ex.get("email",""))
                phone=st.text_input("Phone", value=ex.get("phone",""))
                country=st.text_input("Country", value=ex.get("country",""))
            with c2:
                platform=st.selectbox("Platform",["Upwork","Fiverr","LinkedIn","Direct / Referral","Freelancer","Other"])
                service=st.selectbox("Service",["Web Development","UI/UX","Branding","Content","Mobile App","E-commerce","Other"])
                status=st.selectbox("Status",["Active","Completed","On Hold","Cancelled"])
                ltv=st.number_input("Lifetime Value USD", min_value=0.0, value=float(ex.get("lifetime_value") or 0))
                rating=st.slider("Rating",1,5,int(ex.get("rating") or 3))
                portal_pass=st.text_input("Portal Password", value=ex.get("portal_password") or "", type="password")
            notes=st.text_area("Notes", value=ex.get("notes",""))
            if st.form_submit_button(t("save"), type="primary"):
                if name:
                    save_row("clients",{"id":cid,"name":name,"company":company,"email":email,"phone":phone,"country":country,
                        "platform":platform,"service":service,"start_date":date.today().isoformat(),"status":status,
                        "lifetime_value":ltv,"payment_terms":"","source_lead":"","rating":rating,"notes":notes,"portal_password":portal_pass})
                    log_activity(user["username"],"SAVE","client",cid,name); st.success("Saved"); st.rerun()

# ===================== LEADS =====================
elif page == t("leads"):
    st.title(t("leads"))
    tab1,tab2=st.tabs(["Pipeline", f"{t('add')} / Edit"])
    with tab1:
        df=load_table("leads")
        if not df.empty:
            q=st.text_input(t("search"), key="lq")
            filtered=df.copy()
            if q: filtered=filtered[filtered.apply(lambda r: q.lower() in str(r.values).lower(), axis=1)]
            filtered["nf"]=pd.to_datetime(filtered["next_followup"],errors="coerce")
            filtered["OD"]=filtered.apply(lambda r: "OVERDUE" if pd.notna(r["nf"]) and r["nf"]<pd.Timestamp(date.today()) and r["stage"] not in ["Won","Lost"] else "", axis=1)
            filtered["St"]=filtered["stage"].apply(lambda x: f"{si(x)} {x}")
            st.dataframe(filtered[["id","name","company","St","priority","estimated_value","next_followup","OD"]], use_container_width=True, hide_index=True)
        else: st.info("No leads")
    with tab2:
        with st.form("lf2"):
            lid=st.text_input("ID", value=next_id("leads","LD"))
            name=st.text_input("Name *")
            company=st.text_input("Company")
            email=st.text_input("Email")
            stage=st.selectbox("Stage",["New","Contacted","Proposal Sent","Negotiation","Won","Lost"])
            priority=st.selectbox("Priority",["Hot","Warm","Cold"])
            est=st.number_input("Est. Value USD", min_value=0.0)
            nf=st.date_input("Next Follow-up", value=date.today()+timedelta(days=3))
            notes=st.text_area("Notes")
            if st.form_submit_button(t("save"), type="primary"):
                if name:
                    save_row("leads",{"id":lid,"name":name,"company":company,"email":email,"phone":"","country":"",
                        "platform":"","stage":stage,"priority":priority,"estimated_value":est,
                        "next_followup":nf.isoformat(),"last_contact":date.today().isoformat(),"notes":notes})
                    st.success("Saved"); st.rerun()

# ===================== PROJECTS =====================
elif page == t("projects"):
    st.title(t("projects"))
    tab1,tab2=st.tabs(["All", f"{t('add')} / Edit"])
    times=load_table("time_logs"); hourly=float(get_setting("hourly_rate",25))
    with tab1:
        df=load_table("projects")
        if not df.empty:
            hmap=times.groupby("project_id")["hours"].sum().to_dict() if not times.empty else {}
            df=df.copy(); df["Hours"]=df["id"].map(hmap).fillna(0)
            df["Cost"]=df["Hours"]*hourly; df["Profit"]=df["budget"]-df["Cost"]
            df["St"]=df["status"].apply(lambda x: f"{si(x)} {x}")
            st.dataframe(df[["id","name","client_name","budget","St","progress","Hours","Profit"]], use_container_width=True, hide_index=True)
        else: st.info("No projects")
    with tab2:
        clients=load_table("clients"); cnames=clients["name"].tolist() if not clients.empty else [""]
        with st.form("pf2"):
            pid=st.text_input("ID", value=next_id("projects","PR"))
            pname=st.text_input("Name *")
            cname=st.selectbox("Client", cnames)
            budget=st.number_input("Budget USD", min_value=0.0)
            status=st.selectbox("Status",["Not Started","In Progress","On Hold","Completed","Cancelled"])
            deadline=st.date_input("Deadline", value=date.today()+timedelta(days=30))
            progress=st.slider("Progress %",0,100,0)
            if st.form_submit_button(t("save"), type="primary"):
                if pname:
                    cid=""
                    if not clients.empty:
                        m=clients[clients["name"]==cname]
                        if not m.empty: cid=m.iloc[0]["id"]
                    save_row("projects",{"id":pid,"name":pname,"client_id":cid,"client_name":cname,"platform":"",
                        "budget":budget,"start_date":date.today().isoformat(),"status":status,
                        "deadline":deadline.isoformat(),"progress":progress,"notes":""})
                    st.success("Saved"); st.rerun()

# ===================== PAYMENTS =====================
elif page == t("payments"):
    st.title(t("payments"))
    tab1,tab2,tab3=st.tabs(["All", t("add"), "PDF"])
    with tab1:
        df=load_table("payments")
        if not df.empty:
            df=df.copy(); df["St"]=df["status"].apply(lambda x: f"{si(x)} {x}")
            st.dataframe(df[["id","client_name","description","amount","due_date","St"]], use_container_width=True, hide_index=True)
        else: st.info("No payments")
    with tab2:
        projs=load_table("projects")
        with st.form("payf"):
            iid=st.text_input("Invoice ID", value=next_invoice_id())
            pids=projs["id"].tolist() if not projs.empty else [""]
            pid=st.selectbox("Project", pids)
            cname=""
            if pid and not projs.empty:
                m=projs[projs["id"]==pid]
                if not m.empty: cname=m.iloc[0]["client_name"]
            desc=st.text_input("Description *")
            amount=st.number_input("Amount USD", min_value=0.0)
            due=st.date_input("Due", value=date.today()+timedelta(days=7))
            status=st.selectbox("Status",["Pending","Paid","Partial","Overdue"])
            method=st.selectbox("Method",["Bank Transfer","PayPal","Wise","Upwork","Other"])
            is_rec=st.checkbox("Recurring")
            if st.form_submit_button(t("save"), type="primary"):
                if desc and amount>0:
                    save_row("payments",{"id":iid,"project_id":pid,"client_name":cname,"description":desc,
                        "invoice_date":date.today().isoformat(),"amount":amount,"due_date":due.isoformat(),
                        "status":status,"payment_date":"","method":method,"notes":"",
                        "is_recurring":1 if is_rec else 0,"recurring_interval":"Monthly" if is_rec else "","next_invoice_date":""})
                    st.success("Saved"); st.rerun()
    with tab3:
        pays=load_table("payments")
        if not pays.empty:
            sel=st.selectbox("Invoice", pays["id"].tolist())
            if sel and st.button("Generate PDF", type="primary"):
                row=pays[pays["id"]==sel].iloc[0].to_dict()
                cl=load_table("clients"); ci=cl[cl["name"]==row["client_name"]]
                ci=ci.iloc[0] if not ci.empty else None
                pdfb=generate_invoice_pdf(row, ci)
                st.download_button("Download PDF", data=pdfb, file_name=f"{sel}.pdf", mime="application/pdf")

# ===================== EXPENSES / TIME / TASKS / REMINDERS (compact) =====================
elif page == t("expenses"):
    st.title(t("expenses"))
    tab1,tab2=st.tabs(["All", t("add")])
    with tab1:
        df=load_table("expenses")
        if not df.empty:
            st.metric("Total", fmt_money(df["amount"].sum()))
            st.dataframe(df, use_container_width=True, hide_index=True)
    with tab2:
        with st.form("exf"):
            eid=st.text_input("ID", value=next_id("expenses","EXP"))
            amt=st.number_input("Amount USD", min_value=0.0)
            cat=st.selectbox("Category",["Software","Internet","Marketing","Equipment","Other"])
            desc=st.text_input("Description *")
            if st.form_submit_button(t("save"), type="primary"):
                if desc and amt>0:
                    save_row("expenses",{"id":eid,"date":date.today().isoformat(),"category":cat,"description":desc,"amount":amt,"method":"","notes":""})
                    st.success("Saved"); st.rerun()

elif page == t("time"):
    st.title(t("time"))
    df=load_table("time_logs")
    if not df.empty:
        st.metric("Total Hours", f"{df['hours'].sum():.1f}h")
        st.dataframe(df, use_container_width=True, hide_index=True)
    with st.form("tf"):
        projs=load_table("projects")
        tid=st.text_input("ID", value=next_id("time_logs","TL"))
        pid=st.selectbox("Project", projs["id"].tolist() if not projs.empty else [""])
        hours=st.number_input("Hours", min_value=0.0, value=1.0, step=0.5)
        task=st.text_input("Task *")
        if st.form_submit_button(t("save"), type="primary"):
            cname=""
            if pid and not projs.empty:
                m=projs[projs["id"]==pid]
                if not m.empty: cname=m.iloc[0]["client_name"]
            if task:
                save_row("time_logs",{"id":tid,"project_id":pid,"date":date.today().isoformat(),"client_name":cname,"task":task,"hours":hours,"billable":"Yes","notes":""})
                st.success("Logged"); st.rerun()

elif page == t("tasks"):
    st.title(t("tasks"))
    tab1,tab2=st.tabs(["All", t("add")])
    with tab1:
        df=load_table("tasks")
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            pending=df[df["status"]!="Done"]
            if not pending.empty:
                sel=st.selectbox("Mark Done",[""]+pending["id"].astype(str).tolist())
                if sel and st.button("Done"):
                    conn=get_conn(); c=conn.cursor(); c.execute("UPDATE tasks SET status='Done' WHERE id=?",(sel,))
                    conn.commit(); conn.close(); st.rerun()
    with tab2:
        with st.form("taskf"):
            title=st.text_input("Title *")
            due=st.date_input("Due", value=date.today()+timedelta(days=3))
            priority=st.selectbox("Priority",["High","Medium","Low"])
            if st.form_submit_button(t("save"), type="primary"):
                if title:
                    conn=get_conn(); c=conn.cursor()
                    c.execute("INSERT INTO tasks (title,related_to,due_date,priority,status,assigned_to,created_at,notes) VALUES (?,?,?,?,?,?,?,?)",
                              (title,"",due.isoformat(),priority,"Todo",user["username"],datetime.now().isoformat(),""))
                    conn.commit(); conn.close(); st.success("Created"); st.rerun()

elif page == t("reminders"):
    st.title(t("reminders"))
    df=load_table("reminders")
    if not df.empty: st.dataframe(df, use_container_width=True, hide_index=True)
    with st.form("rf2"):
        title=st.text_input("Title *")
        due=st.date_input("Due", value=date.today()+timedelta(days=1))
        email_to=st.text_input("Email")
        if st.form_submit_button(t("save"), type="primary"):
            if title:
                conn=get_conn(); c=conn.cursor()
                c.execute("INSERT INTO reminders (title,related_to,due_date,email_to,status,created_at,notes) VALUES (?,?,?,?,?,?,?)",
                          (title,"",due.isoformat(),email_to,"Pending",datetime.now().isoformat(),""))
                conn.commit(); conn.close(); st.success("Created"); st.rerun()

elif page == t("calendar"):
    st.title(t("calendar"))
    events=[]
    for tbl, col, typ, namecol in [("leads","next_followup","Follow-up","name"),("projects","deadline","Deadline","name"),("tasks","due_date","Task","title"),("reminders","due_date","Reminder","title")]:
        df=load_table(tbl)
        if not df.empty and col in df.columns:
            for _,r in df.iterrows():
                if r.get(col):
                    events.append({"date":r[col],"type":typ,"title":str(r.get(namecol,r.get("title","")))})
    if events:
        edf=pd.DataFrame(events); edf["date"]=pd.to_datetime(edf["date"],errors="coerce")
        edf=edf.dropna(subset=["date"]).sort_values("date")
        for dt, grp in edf.groupby(edf["date"].dt.date):
            with st.expander(f"{'⚠ ' if dt < date.today() else ''}{dt.strftime('%a %d %b %Y')}", expanded=(dt<=date.today()+timedelta(days=2))):
                for _,ev in grp.iterrows():
                    st.markdown(f"- **[{ev['type']}]** {ev['title']}")
    else: st.info("No events")

elif page == t("reports"):
    st.title(t("reports"))
    clients=load_table("clients"); payments=load_table("payments"); expenses=load_table("expenses")
    te=payments[payments["status"]=="Paid"]["amount"].sum() if not payments.empty else 0
    tex=expenses["amount"].sum() if not expenses.empty else 0
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Clients", len(clients)); c2.metric(t("earned"), fmt_money(te))
    c3.metric(t("expenses_label"), fmt_money(tex)); c4.metric(t("net_profit"), fmt_money(te-tex))
    st.subheader("Export Excel")
    if st.button("Generate Excel", type="primary"):
        out=io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as w:
            for name,df in [("Clients",clients),("Payments",payments),("Expenses",expenses),
                            ("Leads",load_table("leads")),("Projects",load_table("projects"))]:
                if not df.empty: df.to_excel(w, sheet_name=name[:31], index=False)
        st.download_button("Download Excel", data=out.getvalue(), file_name=f"LeadNest_Report_{date.today()}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.subheader(t("tax_report"))
    year=st.selectbox("Year",[2026,2025,2024])
    if not payments.empty:
        p=payments.copy(); p["invoice_date"]=pd.to_datetime(p["invoice_date"],errors="coerce")
        yr=p[(p["invoice_date"].dt.year==year)&(p["status"]=="Paid")]
        e=expenses.copy(); e["date"]=pd.to_datetime(e["date"],errors="coerce")
        ey=e[e["date"].dt.year==year] if not expenses.empty else pd.DataFrame()
        income=yr["amount"].sum() if not yr.empty else 0
        expense=ey["amount"].sum() if not ey.empty else 0
        st.write(f"Gross: {fmt_money(income)} | Expenses: {fmt_money(expense)} | Net: {fmt_money(income-expense)}")
        if st.button("Download Tax PDF"):
            pdf=FPDF(); pdf.add_page()
            pdf.set_font("Helvetica","B",14); pdf.cell(0,10,f"LeadNest Tax Summary {year}",ln=True)
            pdf.set_font("Helvetica","",11)
            pdf.cell(0,8,f"Gross Income: ${income:,.2f}",ln=True)
            pdf.cell(0,8,f"Expenses: ${expense:,.2f}",ln=True)
            pdf.cell(0,8,f"Net: ${income-expense:,.2f}",ln=True)
            pdf.ln(8); pdf.set_font("Helvetica","I",8)
            pdf.cell(0,6,"Copyright by LeadNest v2.3 - Built with Orbit Galax",ln=True)
            st.download_button("Download", data=bytes(pdf.output()), file_name=f"Tax_{year}.pdf", mime="application/pdf")

elif page == t("activity_log"):
    st.title(t("activity_log"))
    df=load_table("activity_log")
    if not df.empty:
        st.dataframe(df.sort_values("created_at",ascending=False).head(150), use_container_width=True, hide_index=True)
    else: st.info("No activity")

elif page == t("schema"):
    st.title(t("schema"))
    schema = {
        "users":"id, username, email, password_hash, full_name, role, created_at",
        "clients":"id, name, company, email, phone, country, platform, service, status, lifetime_value, rating, portal_password, notes",
        "leads":"id, name, company, email, stage, priority, estimated_value, next_followup, notes",
        "projects":"id, name, client_id, client_name, budget, status, deadline, progress, notes",
        "payments":"id, project_id, client_name, amount, status, is_recurring, recurring_interval",
        "expenses":"id, date, category, description, amount",
        "time_logs":"id, project_id, date, hours, billable, task",
        "tasks":"id, title, due_date, priority, status, assigned_to",
        "reminders":"id, title, due_date, email_to, status",
        "activity_log":"id, user, action, entity, entity_id, details, created_at",
        "attachments":"id, entity_type, entity_id, filename, filepath",
        "settings":"key, value",
    }
    for tbl, cols in schema.items():
        with st.expander(tbl):
            st.code(cols)
            try: st.caption(f"Rows: {len(load_table(tbl))}")
            except: pass

elif page == t("settings"):
    st.title(t("settings"))
    if role not in ["admin","manager"]:
        st.warning("Admin only"); st.stop()
    st.subheader(t("currency"))
    st.caption("All amounts stored in USD. Display converts using selected currency rate.")
    st.write("Change display currency from the **sidebar**.")
    st.subheader("Goals & Rates")
    ng=st.number_input("Monthly Earning Goal (USD)", value=float(get_setting("monthly_goal",2500)), step=100.0)
    nhr=st.number_input("Hourly Rate (USD)", value=float(get_setting("hourly_rate",25)), step=1.0)
    if st.button("Save Goals"):
        set_setting("monthly_goal",ng); set_setting("hourly_rate",nhr); st.success("Saved")
    st.subheader("Company (Invoices)")
    cn=st.text_input("Company Name", value=get_setting("company_name","LeadNest"))
    ce=st.text_input("Email", value=get_setting("company_email",""))
    if st.button("Save Company"):
        set_setting("company_name",cn); set_setting("company_email",ce); st.success("Saved")
    st.subheader("Users")
    users=load_table("users")
    if not users.empty:
        st.dataframe(users[["username","full_name","email","role"]], use_container_width=True, hide_index=True)
    st.subheader("Backup")
    if os.path.exists(DB_PATH):
        with open(DB_PATH,"rb") as f:
            st.download_button("Download DB Backup", data=f.read(), file_name=f"leadnest_backup_{date.today()}.db")
