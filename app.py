import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, date, timedelta
import os, hashlib, io, json
import subprocess, tempfile
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "AI Bots", "ai_calculations": "AI Calculations", "ai_alerts": "Smart Alerts",
           "ai_predictions": "Predictions", "ai_sales_coach": "Sales Coach", "ai_email_writer": "Email Writer",
           "ai_insights": "Insights", "ai_proposal": "Proposal Writer", "ai_assistant": "CRM Assistant",
           "ai_revenue_forecast": "Revenue Forecast", "ai_lead_score": "Lead Score", "ai_churn_risk": "Churn Risk",
           "ai_tax": "Tax Calculator", "ai_margin": "Profit Margin", "ai_breakeven": "Break-even",
           "ai_hourly_cost": "Hourly Cost", "ai_send": "Send", "ai_reply": "Reply", "ai_typing": "Thinking...",
           "ai_disclaimer": "AI-generated. Always review before sending to clients."},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "KI-Bots", "ai_calculations": "KI-Berechnungen", "ai_alerts": "Smart Alerts",
           "ai_predictions": "Vorhersagen", "ai_sales_coach": "Verkaufscoach", "ai_email_writer": "E-Mail-Schreiber",
           "ai_insights": "Einblicke", "ai_proposal": "Angebotsschreiber", "ai_assistant": "CRM-Assistent",
           "ai_revenue_forecast": "Umsatzprognose", "ai_lead_score": "Lead-Score", "ai_churn_risk": "Abwanderungsrisiko",
           "ai_tax": "Steuerrechner", "ai_margin": "Gewinnmarge", "ai_breakeven": "Break-even",
           "ai_hourly_cost": "Stundenkosten", "ai_send": "Senden", "ai_reply": "Antwort", "ai_typing": "Denke nach...",
           "ai_disclaimer": "KI-generiert. Vor dem Senden an Kunden immer prüfen."},
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
           "copyright": "کاپی رائٹ LeadNest v2.3 • Orbit Galax",
           "ai_bots": "ای آئی بوٹس", "ai_calculations": "ای آئی حسابات", "ai_alerts": "اسمارٹ الرٹس",
           "ai_predictions": "پیش گوئیاں", "ai_sales_coach": "سیلز کوچ", "ai_email_writer": "ای میل لکھاری",
           "ai_insights": "تجازیات", "ai_proposal": "پروپوزل لکھاری", "ai_assistant": "سی آر ایم اسسٹنٹ",
           "ai_revenue_forecast": "آمدنی کی پیشگوئی", "ai_lead_score": "لیڈ اسکور", "ai_churn_risk": "چرن رسک",
           "ai_tax": "ٹ�یکس کیلکولیٹر", "ai_margin": "منافع مارجن", "ai_breakeven": "بریک ایون",
           "ai_hourly_cost": "گھنٹہ وار لاگت", "ai_send": "بھیجیں", "ai_reply": "جواب", "ai_typing": "سوچ رہا ہے...",
           "ai_disclaimer": "ای آئی سے تیار شدہ۔ کلائنٹس کو بھیجنے سے پہلے ضرور جائزہ لیں۔"},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "एआई बॉट्स", "ai_calculations": "एआई गणनाएं", "ai_alerts": "स्मार्ट अलर्ट",
           "ai_predictions": "भविष्यवाणियां", "ai_sales_coach": "सेल्स कोच", "ai_email_writer": "ईमेल लेखक",
           "ai_insights": "इनसाइट्स", "ai_proposal": "प्रपोजल लेखक", "ai_assistant": "CRM सहायक",
           "ai_revenue_forecast": "राजस्व पूर्वानुमान", "ai_lead_score": "लीड स्कोर", "ai_churn_risk": "चर्न जोखिम",
           "ai_tax": "टैक्स कैलकुलेटर", "ai_margin": "लाभ मार्जिन", "ai_breakeven": "ब्रेक-ईवन",
           "ai_hourly_cost": "घंटावार लागत", "ai_send": "भेजें", "ai_reply": "उत्तर", "ai_typing": "सोच रहा है...",
           "ai_disclaimer": "एआई द्वारा उत्पन्न। क्लाइंट को भेजने से पहले हमेशा समीक्षा करें।"},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "בוטי AI", "ai_calculations": "חישובי AI", "ai_alerts": "התראות חכמות",
           "ai_predictions": "תחזיות", "ai_sales_coach": "מאמן מכירות", "ai_email_writer": "כותב אימיילים",
           "ai_insights": "תובנות", "ai_proposal": "כותב הצעות", "ai_assistant": "עוזר CRM",
           "ai_revenue_forecast": "תחזית הכנסות", "ai_lead_score": "ציון ליד", "ai_churn_risk": "סיכון נטישה",
           "ai_tax": "מחשבון מס", "ai_margin": "שולי רווח", "ai_breakeven": "נקודת איזון",
           "ai_hourly_cost": "עלות לשעה", "ai_send": "שלח", "ai_reply": "השב", "ai_typing": "חושב...",
           "ai_disclaimer": "נוצר על ידי AI. תמיד לבדוק לפני שליחה ללקוחות."},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "بوتات الذكاء الاصطناعي", "ai_calculations": "حسابات الذكاء", "ai_alerts": "تنبيهات ذكية",
           "ai_predictions": "توقعات", "ai_sales_coach": "مدرب المبيعات", "ai_email_writer": "كاتب البريد",
           "ai_insights": "رؤى", "ai_proposal": "كاتب العروض", "ai_assistant": "مساعد CRM",
           "ai_revenue_forecast": "توقعات الإيرادات", "ai_lead_score": "تقييم العميل", "ai_churn_risk": "مخاطر المغادرة",
           "ai_tax": "حاسبة الضرائب", "ai_margin": "هامش الربح", "ai_breakeven": "نقطة التعادل",
           "ai_hourly_cost": "التكلفة بالساعة", "ai_send": "إرسال", "ai_reply": "رد", "ai_typing": "يفكر...",
           "ai_disclaimer": "مُنشأ بالذكاء الاصطناعي. راجع دائمًا قبل الإرسال للعملاء."},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "Bots IA", "ai_calculations": "Calculs IA", "ai_alerts": "Alertes intelligentes",
           "ai_predictions": "Prédictions", "ai_sales_coach": "Coach commercial", "ai_email_writer": "Rédacteur e-mail",
           "ai_insights": "Aperçus", "ai_proposal": "Rédacteur de propositions", "ai_assistant": "Assistant CRM",
           "ai_revenue_forecast": "Prévision de revenus", "ai_lead_score": "Score de lead", "ai_churn_risk": "Risque d'attrition",
           "ai_tax": "Calculateur d'impôt", "ai_margin": "Marge bénéficiaire", "ai_breakeven": "Seuil de rentabilité",
           "ai_hourly_cost": "Coût horaire", "ai_send": "Envoyer", "ai_reply": "Répondre", "ai_typing": "Réflexion...",
           "ai_disclaimer": "Généré par IA. Toujours vérifier avant l'envoi aux clients."},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "Bots IA", "ai_calculations": "Cálculos IA", "ai_alerts": "Alertas inteligentes",
           "ai_predictions": "Predicciones", "ai_sales_coach": "Coach de ventas", "ai_email_writer": "Redactor de correos",
           "ai_insights": "Insights", "ai_proposal": "Redactor de propuestas", "ai_assistant": "Asistente CRM",
           "ai_revenue_forecast": "Pronóstico de ingresos", "ai_lead_score": "Puntuación de lead", "ai_churn_risk": "Riesgo de abandono",
           "ai_tax": "Calculadora de impuestos", "ai_margin": "Margen de beneficio", "ai_breakeven": "Punto de equilibrio",
           "ai_hourly_cost": "Costo por hora", "ai_send": "Enviar", "ai_reply": "Responder", "ai_typing": "Pensando...",
           "ai_disclaimer": "Generado por IA. Revisar siempre antes de enviar a clientes."},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "Bots IA", "ai_calculations": "Cálculos IA", "ai_alerts": "Alertas inteligentes",
           "ai_predictions": "Previsões", "ai_sales_coach": "Coach de vendas", "ai_email_writer": "Redator de e-mails",
           "ai_insights": "Insights", "ai_proposal": "Redator de propostas", "ai_assistant": "Assistente CRM",
           "ai_revenue_forecast": "Previsão de receita", "ai_lead_score": "Pontuação de lead", "ai_churn_risk": "Risco de churn",
           "ai_tax": "Calculadora de impostos", "ai_margin": "Margem de lucro", "ai_breakeven": "Ponto de equilíbrio",
           "ai_hourly_cost": "Custo por hora", "ai_send": "Enviar", "ai_reply": "Responder", "ai_typing": "Pensando...",
           "ai_disclaimer": "Gerado por IA. Sempre revise antes de enviar aos clientes."},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "AI Botları", "ai_calculations": "AI Hesaplamaları", "ai_alerts": "Akıllı Uyarılar",
           "ai_predictions": "Tahminler", "ai_sales_coach": "Satış Koçu", "ai_email_writer": "E-posta Yazarı",
           "ai_insights": "İçgörüler", "ai_proposal": "Teklif Yazarı", "ai_assistant": "CRM Asistanı",
           "ai_revenue_forecast": "Gelir Tahmini", "ai_lead_score": "Lead Skoru", "ai_churn_risk": "Kayıp Riski",
           "ai_tax": "Vergi Hesaplayıcı", "ai_margin": "Kâr Marjı", "ai_breakeven": "Başabaş Noktası",
           "ai_hourly_cost": "Saatlik Maliyet", "ai_send": "Gönder", "ai_reply": "Yanıtla", "ai_typing": "Düşünüyor...",
           "ai_disclaimer": "AI tarafından üretildi. Müşterilere göndermeden önce her zaman kontrol edin."},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "AI 机器人", "ai_calculations": "AI 计算", "ai_alerts": "智能提醒",
           "ai_predictions": "预测", "ai_sales_coach": "销售教练", "ai_email_writer": "邮件撰写",
           "ai_insights": "洞察", "ai_proposal": "提案撰写", "ai_assistant": "CRM 助手",
           "ai_revenue_forecast": "收入预测", "ai_lead_score": "线索评分", "ai_churn_risk": "流失风险",
           "ai_tax": "税务计算器", "ai_margin": "利润率", "ai_breakeven": "盈亏平衡点",
           "ai_hourly_cost": "每小时成本", "ai_send": "发送", "ai_reply": "回复", "ai_typing": "思考中...",
           "ai_disclaimer": "AI 生成。发送给客户前请始终审查。"},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "AIボット", "ai_calculations": "AI計算", "ai_alerts": "スマートアラート",
           "ai_predictions": "予測", "ai_sales_coach": "セールスコーチ", "ai_email_writer": "メールライター",
           "ai_insights": "インサイト", "ai_proposal": "提案ライター", "ai_assistant": "CRMアシスタント",
           "ai_revenue_forecast": "収益予測", "ai_lead_score": "リードスコア", "ai_churn_risk": "解約リスク",
           "ai_tax": "税計算機", "ai_margin": "利益率", "ai_breakeven": "損益分岐点",
           "ai_hourly_cost": "時間コスト", "ai_send": "送信", "ai_reply": "返信", "ai_typing": "考え中...",
           "ai_disclaimer": "AI生成。クライアントに送信する前に必ず確認してください。"},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "AI 봇", "ai_calculations": "AI 계산", "ai_alerts": "스마트 알림",
           "ai_predictions": "예측", "ai_sales_coach": "세일즈 코치", "ai_email_writer": "이메일 작성기",
           "ai_insights": "인사이트", "ai_proposal": "제안서 작성기", "ai_assistant": "CRM 어시스턴트",
           "ai_revenue_forecast": "수익 예측", "ai_lead_score": "리드 점수", "ai_churn_risk": "이탈 위험",
           "ai_tax": "세금 계산기", "ai_margin": "이익률", "ai_breakeven": "손익분기점",
           "ai_hourly_cost": "시간당 비용", "ai_send": "보내기", "ai_reply": "답장", "ai_typing": "생각 중...",
           "ai_disclaimer": "AI 생성. 클라이언트에게 보내기 전 항상 검토하세요."},
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
           "copyright": "Copyright by LeadNest v2.3 • Built with Orbit Galax",
           "ai_bots": "ИИ-боты", "ai_calculations": "ИИ-расчёты", "ai_alerts": "Умные оповещения",
           "ai_predictions": "Прогнозы", "ai_sales_coach": "Тренер по продажам", "ai_email_writer": "Автор писем",
           "ai_insights": "Инсайты", "ai_proposal": "Автор предложений", "ai_assistant": "CRM-ассистент",
           "ai_revenue_forecast": "Прогноз доходов", "ai_lead_score": "Оценка лида", "ai_churn_risk": "Риск оттока",
           "ai_tax": "Налоговый калькулятор", "ai_margin": "Маржа прибыли", "ai_breakeven": "Точка безубыточности",
           "ai_hourly_cost": "Стоимость часа", "ai_send": "Отправить", "ai_reply": "Ответить", "ai_typing": "Думаю...",
           "ai_disclaimer": "Создано ИИ. Всегда проверяйте перед отправкой клиентам."},
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

# ===================== AI BOTS (z-ai CLI integration) =====================
def ai_chat(prompt, system=None, timeout=120):
    """Call z-ai CLI chat completion. Returns assistant text or error string."""
    try:
        cmd = ["z-ai", "chat", "--prompt", prompt]
        if system:
            cmd.extend(["--system", system])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            out_path = f.name
        cmd.extend(["--output", out_path])
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            return f"⚠️ AI request failed (exit {proc.returncode})."
        with open(out_path) as f:
            data = json.load(f)
        try:
            os.unlink(out_path)
        except OSError:
            pass
        choices = data.get("choices", []) if isinstance(data, dict) else []
        if choices:
            return choices[0].get("message", {}).get("content", "").strip() or "⚠️ Empty response."
        return "⚠️ No response from AI."
    except subprocess.TimeoutExpired:
        return "⚠️ AI request timed out. Try a shorter prompt."
    except FileNotFoundError:
        return "⚠️ z-ai CLI not available on this server."
    except Exception as e:
        return f"⚠️ AI error: {e}"

def crm_snapshot():
    """Build a compact textual snapshot of CRM state for AI context."""
    parts = []
    try:
        cl = load_table("clients")
        ld = load_table("leads")
        pr = load_table("projects")
        pa = load_table("payments")
        ex = load_table("expenses")
        tl = load_table("time_logs")
        if not cl.empty:
            parts.append(f"Clients ({len(cl)}): " + "; ".join(
                f"{r['name']} ({r.get('company','')}, {r.get('status','')}, {r.get('platform','')}, LTV ${r.get('lifetime_value',0):.0f})"
                for _, r in cl.head(15).iterrows()))
        if not ld.empty:
            parts.append(f"Leads ({len(ld)}): " + "; ".join(
                f"{r['name']} ({r.get('company','')}, stage={r.get('stage','')}, priority={r.get('priority','')}, est ${r.get('estimated_value',0):.0f}, next follow-up {r.get('next_followup','')})"
                for _, r in ld.head(15).iterrows()))
        if not pr.empty:
            parts.append(f"Projects ({len(pr)}): " + "; ".join(
                f"{r['name']} ({r.get('client_name','')}, {r.get('status','')}, {r.get('progress',0)}%, budget ${r.get('budget',0):.0f}, deadline {r.get('deadline','')})"
                for _, r in pr.head(15).iterrows()))
        if not pa.empty:
            te = pa[pa["status"] == "Paid"]["amount"].sum() if "status" in pa.columns else 0
            pen = pa[pa["status"].isin(["Pending", "Overdue"])]["amount"].sum() if "status" in pa.columns else 0
            parts.append(f"Payments: earned=${te:.2f}, pending=${pen:.2f}, total invoices={len(pa)}")
        if not ex.empty:
            parts.append(f"Expenses: total ${ex['amount'].sum():.2f} across {len(ex)} entries")
        if not tl.empty:
            parts.append(f"Time logs: {tl['hours'].sum():.1f} hours across {len(tl)} entries")
        parts.append(f"Currency in use: {st.session_state.get('currency','USD')}. "
                     f"Hourly rate: ${get_setting('hourly_rate','25')}. "
                     f"Monthly goal: ${get_setting('monthly_goal','2500')}.")
    except Exception as e:
        parts.append(f"(snapshot error: {e})")
    return "\n".join(parts)

def crm_system_prompt(role="assistant"):
    """System prompt that turns the LLM into a CRM-aware assistant."""
    base = ("You are an AI assistant embedded inside LeadNest CRM (a Streamlit app for freelancers/agencies). "
            "Be concise, actionable, and friendly. Use markdown for structure. "
            "When suggesting actions, prefer specific next steps the user can take inside the CRM "
            "(e.g. add follow-up, mark invoice overdue, send proposal). "
            "Always respond in the user's language unless asked otherwise.\n\n")
    snap = crm_snapshot()
    return base + "CURRENT CRM SNAPSHOT:\n" + snap

# ===================== PDF =====================
class InvoicePDF(FPDF):
    """Modern, professional invoice layout with gradient-style header banner."""
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        # Top color banner (gradient illusion via stacked rects)
        w = self.w
        # Deep indigo band
        self.set_fill_color(37, 99, 235); self.rect(0, 0, w, 4, "F")
        self.set_fill_color(30, 64, 175); self.rect(0, 4, w, 22, "F")
        self.set_fill_color(15, 23, 42);  self.rect(0, 26, w, 1.2, "F")
        # Brand block (left)
        self.set_xy(14, 9)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 18)
        self.cell(60, 8, get_setting("company_name", "LeadNest"), ln=False)
        self.set_font("Helvetica", "", 8)
        self.set_xy(14, 19)
        cemail = get_setting("company_email", "")
        cphone = get_setting("company_phone", "")
        contact_line = " | ".join(x for x in [cemail, cphone] if x)
        if not contact_line:
            contact_line = "LeadNest CRM"
        self.set_text_color(200, 215, 245)
        self.cell(60, 5, contact_line, ln=False)
        # Big "INVOICE" badge (right)
        self.set_xy(w - 70, 8)
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(56, 12, "INVOICE", align="R", ln=True)
        self.set_xy(w - 70, 19)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(200, 215, 245)
        inv_id = str(self._inv_id) if hasattr(self, "_inv_id") else ""
        self.cell(56, 5, f"#{inv_id}", align="R", ln=True)
        # Reset text color
        self.set_text_color(15, 23, 42)
        self.ln(8)

    def footer(self):
        self.set_y(-14)
        # Thin divider
        self.set_draw_color(203, 213, 225); self.set_line_width(0.3)
        self.line(14, self.get_y(), self.w - 14, self.get_y())
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, "Thank you for your business. " +
                  "Copyright by LeadNest v2.3 - Built with Orbit Galax",
                  align="C")

def _status_color(status):
    s = (status or "").strip().lower()
    return {
        "paid":     (16, 185, 129),   # emerald
        "pending":  (245, 158, 11),   # amber
        "partial":  (59, 130, 246),  # blue
        "overdue":  (239, 68, 68),    # red
    }.get(s, (100, 116, 139))

def generate_invoice_pdf(row, client=None):
    pdf = InvoicePDF()
    pdf._inv_id = row.get("id", "")
    pdf.add_page()
    amt = float(row.get("amount", 0) or 0)

    # ---- Bill-To / Invoice meta block ----
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(90, 5, "BILL TO", ln=False)
    pdf.cell(0, 5, "INVOICE DETAILS", align="R", ln=True)
    pdf.set_text_color(15, 23, 42)

    # Left column: client info
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(90, 6, str(row.get("client_name", "")), ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Invoice #: {row.get('id','')}", align="R", ln=True)
    if client is not None:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(71, 85, 105)
        comp = client.get("company", "")
        if comp:
            pdf.cell(90, 5, str(comp), ln=False)
        pdf.cell(0, 5, f"Issue Date: {row.get('invoice_date','')}", align="R", ln=True)
        em = client.get("email", "")
        if em:
            pdf.cell(90, 5, str(em), ln=False)
        ph = client.get("phone", "")
        if ph:
            pdf.cell(90, 5, str(ph), ln=True)
        else:
            pdf.ln(5)
        country = client.get("country", "")
        if country:
            pdf.cell(90, 5, str(country), ln=False)
    else:
        pdf.ln(5)
    pdf.cell(0, 5, f"Due Date: {row.get('due_date','')}", align="R", ln=True)
    pdf.ln(6)

    # ---- Status badge ----
    status = str(row.get("status", ""))
    r, g, b = _status_color(status)
    pdf.set_fill_color(245, 247, 250)
    pdf.set_draw_color(r, g, b)
    pdf.set_text_color(r, g, b)
    pdf.set_font("Helvetica", "B", 10)
    badge_w = 38
    x0 = pdf.get_x(); y0 = pdf.get_y()
    pdf.rect(x0, y0, badge_w, 8, "DF")
    pdf.set_xy(x0 + 2, y0 + 1)
    pdf.cell(badge_w - 4, 6, f"[ {status.upper()} ]", align="C", ln=True)
    pdf.set_text_color(15, 23, 42)
    pdf.ln(6)

    # ---- Items table header ----
    pdf.set_fill_color(15, 23, 42)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 9, "  Description", border=0, fill=True)
    pdf.cell(40, 9, "Project", border=0, fill=True, align="C")
    pdf.cell(40, 9, "Amount", border=0, fill=True, align="R")
    pdf.ln()
    # Thin accent line under header
    pdf.set_draw_color(37, 99, 235); pdf.set_line_width(0.6)
    pdf.line(14, pdf.get_y(), pdf.w - 14, pdf.get_y())
    pdf.ln(0.5)

    # Items row
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_fill_color(248, 250, 252)
    pdf.cell(95, 10, f"  {str(row.get('description',''))}", border=0, fill=True)
    pdf.cell(40, 10, str(row.get("project_id", "")), border=0, fill=True, align="C")
    pdf.cell(40, 10, f"${amt:,.2f}", border=0, fill=True, align="R")
    pdf.ln()

    # Total row
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(37, 99, 235)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(135, 11, "TOTAL DUE", border=0, fill=True, align="R")
    pdf.cell(40, 11, f"${amt:,.2f}", border=0, fill=True, align="R")
    pdf.ln(10)
    pdf.set_text_color(15, 23, 42)

    # ---- Payment info block ----
    pdf.set_draw_color(226, 232, 240); pdf.set_line_width(0.3)
    y_block = pdf.get_y()
    pdf.line(14, y_block, pdf.w - 14, y_block)
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, "PAYMENT INFORMATION", ln=True)
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "", 9)
    method = str(row.get("method", ""))
    terms = "Net 7 (unless otherwise agreed)"
    pdf.cell(0, 5, f"Method: {method or 'Bank Transfer'}    |    Terms: {terms}", ln=True)
    pdf.cell(0, 5, f"Status: {status}    |    Notes: {str(row.get('notes','')) or 'Thank you for your business.'}", ln=True)
    pdf.ln(2)
    pdf.line(14, pdf.get_y(), pdf.w - 14, pdf.get_y())

    # ---- Footer note ----
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(0, 5,
        "Please remit payment by the due date. Late payments may be subject to a 1.5% monthly fee. "
        "For any questions about this invoice, contact the issuer using the details in the header above.")

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
        h1,h2,h3,h4,p,label,span,.stMarkdown{color:#e2e8f0!important}
        .stButton>button{border-radius:8px}
        .block-container{padding-top:1.2rem}
        </style>""", unsafe_allow_html=True)
    else:
        # Light mode - high contrast, readable login + forms
        st.markdown("""<style>
        .stApp{background:#eef2f7!important;color:#0f172a!important}
        section[data-testid="stSidebar"]{background:#e2e8f0!important}
        .block-container{padding-top:1.5rem;background:#eef2f7!important}
        h1,h2,h3,h4{color:#0f172a!important}
        p,label,span,.stMarkdown,.stCaption{color:#1e293b!important}
        .stMetric{background:#ffffff;padding:14px;border-radius:12px;border:1px solid #cbd5e1;
                  box-shadow:0 1px 3px rgba(0,0,0,0.06)}
        div[data-testid="stMetricValue"]{color:#1e40af!important;font-size:1.35rem!important}
        div[data-testid="stMetricLabel"]{color:#475569!important}
        /* Inputs readable */
        .stTextInput input,.stTextInput>div>div>input,
        .stSelectbox div[data-baseweb="select"]>div,
        .stNumberInput input,.stTextArea textarea{
          background:#ffffff!important;color:#0f172a!important;
          border:1px solid #94a3b8!important;border-radius:8px!important;
        }
        .stTextInput label,.stSelectbox label,.stNumberInput label,.stTextArea label{
          color:#0f172a!important;font-weight:600!important;
        }
        /* Tabs */
        button[data-baseweb="tab"]{color:#334155!important}
        button[data-baseweb="tab"][aria-selected="true"]{color:#1d4ed8!important}
        /* Buttons */
        .stButton>button{border-radius:8px;font-weight:600}
        div[data-testid="stDataFrame"]{background:#ffffff;border-radius:8px}
        /* Login page spacing */
        [data-testid="stForm"]{background:#ffffff;padding:20px;border-radius:12px;
          border:1px solid #cbd5e1;box-shadow:0 2px 8px rgba(0,0,0,.06)}
        </style>""", unsafe_allow_html=True)


if "prefs_loaded" not in st.session_state:
    try:
        init_db()
    except Exception:
        pass
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

def render_top_header(user, notif_count=0):
    """Top bar: Logo + Search + Notifications + User"""
    dark = st.session_state.get("dark_mode", False)
    bg = "#1e293b" if dark else "#ffffff"
    border = "#334155" if dark else "#cbd5e1"
    text_c = "#e2e8f0" if dark else "#0f172a"
    muted = "#94a3b8" if dark else "#64748b"
    accent = "#38bdf8" if dark else "#2563eb"

    st.markdown(f"""
    <style>
    .ln-header {{
        background:{bg}; border:1px solid {border}; border-radius:14px;
        padding:10px 16px; margin-bottom:14px;
        display:flex; align-items:center; justify-content:space-between; gap:12px;
        box-shadow:0 1px 3px rgba(0,0,0,.06);
    }}
    .ln-brand {{ display:flex; align-items:center; gap:10px; min-width:140px; }}
    .ln-logo {{
        width:36px; height:36px; border-radius:10px;
        background:linear-gradient(135deg,#3b82f6,#22d3ee);
        display:flex; align-items:center; justify-content:center;
        color:white; font-weight:800; font-size:16px;
    }}
    .ln-title {{ font-weight:800; font-size:1.15rem; color:{text_c}; letter-spacing:-0.02em; }}
    .ln-sub {{ font-size:0.72rem; color:{muted}; }}
    .ln-right {{ display:flex; align-items:center; gap:14px; }}
    .ln-bell {{
        background:rgba(59,130,246,.12); color:{accent};
        border-radius:999px; padding:6px 12px; font-size:0.85rem; font-weight:600;
        border:1px solid rgba(59,130,246,.25);
    }}
    .ln-user {{
        background:rgba(148,163,184,.12); color:{text_c};
        border-radius:999px; padding:6px 12px; font-size:0.85rem; font-weight:600;
        border:1px solid {border};
    }}
    </style>
    <div class="ln-header">
      <div class="ln-brand">
        <div class="ln-logo">L</div>
        <div>
          <div class="ln-title">LeadNest</div>
          <div class="ln-sub">v2.3 · CRM</div>
        </div>
      </div>
      <div class="ln-right">
        <div class="ln-bell">🔔 {notif_count}</div>
        <div class="ln-user">👤 {user.get('full_name','User')} · {user.get('role','admin')}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Search row under header
    q = st.text_input("Search clients, leads, projects...", value=st.session_state.get("global_search",""), key="hdr_search", placeholder="Type to search...")
    st.session_state.global_search = q
    if q and len(q.strip()) >= 2:
        ql = q.strip().lower()
        hits = []
        try:
            for table, cols, label in [
                ("clients", ["name","company","email","country"], "Client"),
                ("leads", ["name","company","email","stage"], "Lead"),
                ("projects", ["name","client_name","status"], "Project"),
            ]:
                df = load_table(table)
                if df.empty: continue
                for _, r in df.iterrows():
                    blob = " ".join(str(r.get(c,"")) for c in cols).lower()
                    if ql in blob:
                        title = r.get("name") or r.get("id")
                        hits.append(f"**{label}:** {title}")
            if hits:
                with st.expander(f"Search results ({len(hits)})", expanded=True):
                    for h in hits[:20]:
                        st.markdown(f"- {h}")
            else:
                st.caption("No matches found.")
        except Exception:
            pass


def show_login():
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1rem 0;">
      <h1 style="color:#0f172a!important;font-size:2rem;margin-bottom:0.25rem;">LeadNest</h1>
      <p style="color:#334155!important;font-size:0.95rem;">Built with Orbit Galax</p>
    </div>
    """, unsafe_allow_html=True)
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


# Session state safety init
for _k, _v in [("logged_in", False), ("user", None), ("dark_mode", False), ("client_portal", False), ("portal_client", None), ("lang", "en"), ("currency", "USD"), ("global_search", "")]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

if not st.session_state.get('logged_in', False):
    show_login(); st.stop()
if st.session_state.get('client_portal', False):
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

# Top header (main area)
render_top_header(user, notif)


pages = [t("dashboard"), t("ai_bots"), t("clients"), t("leads"), t("projects"), t("payments"),
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

# ===================== AI BOTS PAGE =====================
elif page == t("ai_bots"):
    st.title("🤖 " + t("ai_bots"))
    st.caption(t("ai_disclaimer"))

    ai_sub = st.tabs([
        "💬 " + t("ai_assistant"),
        "🎯 " + t("ai_sales_coach"),
        "✉️ " + t("ai_email_writer"),
        "📄 " + t("ai_proposal"),
        "💡 " + t("ai_insights"),
        "🧮 " + t("ai_calculations"),
        "🔔 " + t("ai_alerts"),
        "🔮 " + t("ai_predictions"),
    ])

    # ---------- CRM Assistant (chat) ----------
    with ai_sub[0]:
        st.subheader(t("ai_assistant"))
        st.caption("Ask anything about your CRM — clients, leads, projects, payments, expenses. The assistant has live access to your data.")
        if "ai_chat_msgs" not in st.session_state:
            st.session_state.ai_chat_msgs = []
        # Quick suggestion chips
        chips = ["Summarize my pipeline", "Which leads are overdue?", "Top 3 clients by LTV", "What should I focus on today?"]
        sc1, sc2, sc3, sc4 = st.columns(4)
        for col, chip in zip([sc1, sc2, sc3, sc4], chips):
            if col.button(chip, use_container_width=True, key=f"chip_{chip}"):
                st.session_state.ai_chat_msgs.append({"role": "user", "content": chip})
                with st.spinner(t("ai_typing")):
                    ans = ai_chat(chip, system=crm_system_prompt())
                st.session_state.ai_chat_msgs.append({"role": "assistant", "content": ans})
                st.rerun()
        # Display chat history
        for msg in st.session_state.ai_chat_msgs:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        # Input box
        q = st.chat_input("Type your question...")
        if q:
            st.session_state.ai_chat_msgs.append({"role": "user", "content": q})
            with st.chat_message("user"):
                st.markdown(q)
            with st.spinner(t("ai_typing")):
                ans = ai_chat(q, system=crm_system_prompt())
            st.session_state.ai_chat_msgs.append({"role": "assistant", "content": ans})
            with st.chat_message("assistant"):
                st.markdown(ans)
        if st.button("🗑️ Clear chat", key="clear_ai_chat"):
            st.session_state.ai_chat_msgs = []
            st.rerun()

    # ---------- Sales Coach ----------
    with ai_sub[1]:
        st.subheader("🎯 " + t("ai_sales_coach"))
        st.caption("Get actionable coaching on your hottest leads and stuck deals.")
        leads_df = load_table("leads")
        if leads_df.empty:
            st.info("No leads yet — add a few to get coaching.")
        else:
            hot = leads_df[leads_df["priority"] == "Hot"] if "priority" in leads_df.columns else leads_df
            sel_lead = st.selectbox("Pick a lead to coach on",
                                    [""] + leads_df["name"].tolist())
            if sel_lead:
                row = leads_df[leads_df["name"] == sel_lead].iloc[0]
                prompt = (
                    f"Act as a senior sales coach. Here is a lead from LeadNest CRM:\n"
                    f"- Name: {row.get('name','')}\n- Company: {row.get('company','')}\n"
                    f"- Stage: {row.get('stage','')}\n- Priority: {row.get('priority','')}\n"
                    f"- Estimated value: ${row.get('estimated_value',0):.0f}\n"
                    f"- Next follow-up: {row.get('next_followup','')}\n"
                    f"- Notes: {row.get('notes','')}\n\n"
                    f"Give me: (1) the next 3 concrete actions to move this deal forward, "
                    f"(2) likely objections and how to handle them, (3) a suggested follow-up timeline. "
                    f"Be specific and tactical.")
                if st.button(t("ai_send"), type="primary", key="coach_btn"):
                    with st.spinner(t("ai_typing")):
                        ans = ai_chat(prompt, system=crm_system_prompt())
                    st.markdown(ans)

    # ---------- Email Writer ----------
    with ai_sub[2]:
        st.subheader("✉️ " + t("ai_email_writer"))
        st.caption("Drafts professional emails for follow-ups, payment reminders, proposals.")
        clients_df = load_table("clients")
        leads_df = load_table("leads")
        etype = st.selectbox("Email type", ["Follow-up to lead", "Payment reminder", "Welcome new client", "Project update", "Re-engage cold lead"])
        recipient = st.selectbox("Recipient", [""] + (clients_df["name"].tolist() if not clients_df.empty else []) + (leads_df["name"].tolist() if not leads_df.empty else []))
        tone = st.selectbox("Tone", ["Professional & friendly", "Formal", "Casual", "Urgent"])
        extra = st.text_area("Optional context / specifics")
        if st.button("✍️ Draft email", type="primary", key="email_btn"):
            if not recipient:
                st.warning("Pick a recipient.")
            else:
                prompt = (f"Write a {tone.lower()} email for this scenario: {etype}. "
                          f"Recipient: {recipient}. CRM context: {crm_snapshot()}. "
                          f"Additional context: {extra or 'none'}. "
                          f"Keep it concise (120–180 words), with a clear subject line and a single CTA.")
                with st.spinner(t("ai_typing")):
                    ans = ai_chat(prompt, system=crm_system_prompt())
                st.markdown(ans)
                st.download_button("Download .txt", data=ans, file_name=f"email_{recipient.replace(' ','_')}.txt")

    # ---------- Proposal Writer ----------
    with ai_sub[3]:
        st.subheader("📄 " + t("ai_proposal"))
        st.caption("Generate a proposal draft for a lead or new project.")
        leads_df = load_table("leads")
        projects_df = load_table("projects")
        target = st.selectbox("For lead", [""] + (leads_df["name"].tolist() if not leads_df.empty else []))
        scope = st.text_area("Scope of work (bullet points)", height=120)
        budget = st.number_input("Proposed budget USD", min_value=0.0, value=1000.0, step=100.0)
        timeline = st.text_input("Timeline (e.g. 4 weeks)")
        if st.button("📝 Generate proposal", type="primary", key="prop_btn"):
            if not target or not scope:
                st.warning("Pick a lead and fill scope.")
            else:
                prompt = (f"Draft a professional project proposal for lead '{target}'. "
                          f"Scope: {scope}. Budget: ${budget:.0f}. Timeline: {timeline}. "
                          f"Sections: Summary, Objectives, Deliverables, Timeline, Pricing, Terms, Next Steps. "
                          f"Use clean markdown. 300–450 words.")
                with st.spinner(t("ai_typing")):
                    ans = ai_chat(prompt, system=crm_system_prompt())
                st.markdown(ans)
                st.download_button("Download .md", data=ans, file_name=f"proposal_{target.replace(' ','_')}.md")

    # ---------- Insights ----------
    with ai_sub[4]:
        st.subheader("💡 " + t("ai_insights"))
        st.caption("AI-generated business insights based on your CRM data.")
        if st.button("🔍 Generate insights", type="primary", key="ins_btn"):
            prompt = ("Analyze the following LeadNest CRM snapshot and produce 5–7 actionable insights. "
                      "Group them under: Revenue, Pipeline, Clients, Risks. Be specific (cite names/numbers). "
                      "End with the single most important action for this week.\n\n" + crm_snapshot())
            with st.spinner(t("ai_typing")):
                ans = ai_chat(prompt, system=crm_system_prompt())
            st.markdown(ans)

    # ---------- AI Calculations ----------
    with ai_sub[5]:
        st.subheader("🧮 " + t("ai_calculations"))
        st.caption("Smart calculators that combine your CRM data with AI reasoning.")
        calc_tab1, calc_tab2, calc_tab3, calc_tab4 = st.tabs([
            t("ai_tax"), t("ai_margin"), t("ai_breakeven"), t("ai_hourly_cost")
        ])
        pa = load_table("payments"); ex = load_table("expenses"); tl = load_table("time_logs")

        # Tax
        with calc_tab1:
            st.markdown("**" + t("ai_tax") + "**")
            year = st.selectbox("Year", [2026, 2025, 2024], key="tax_year")
            income = 0; expense = 0
            if not pa.empty and "invoice_date" in pa.columns:
                p = pa.copy(); p["invoice_date"] = pd.to_datetime(p["invoice_date"], errors="coerce")
                yr = p[(p["invoice_date"].dt.year == year) & (p["status"] == "Paid")]
                income = yr["amount"].sum() if not yr.empty else 0
            if not ex.empty and "date" in ex.columns:
                e = ex.copy(); e["date"] = pd.to_datetime(e["date"], errors="coerce")
                ey = e[e["date"].dt.year == year]
                expense = ey["amount"].sum() if not ey.empty else 0
            net = income - expense
            rate = st.slider("Estimated tax rate %", 5, 50, 25)
            tax_due = max(0, net * rate / 100)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Gross income", fmt_money(income))
            c2.metric("Deductible expenses", fmt_money(expense))
            c3.metric("Net taxable", fmt_money(net))
            c4.metric(f"Est. tax @ {rate}%", fmt_money(tax_due))
            if st.button("🤖 Get AI tax optimization tips", key="tax_ai"):
                prompt = (f"My CRM numbers for {year}: gross income ${income:.2f}, expenses ${expense:.2f}, "
                          f"net ${net:.2f}, estimated tax rate {rate}% = ${tax_due:.2f} due. "
                          f"List 5 practical, freelancer-friendly tax optimization tips and what to log in the CRM to track them.")
                with st.spinner(t("ai_typing")):
                    st.markdown(ai_chat(prompt, system=crm_system_prompt()))

        # Profit margin
        with calc_tab2:
            st.markdown("**" + t("ai_margin") + "**")
            projects = load_table("projects")
            if projects.empty:
                st.info("No projects.")
            else:
                pname = st.selectbox("Project", projects["name"].tolist(), key="marg_proj")
                row = projects[projects["name"] == pname].iloc[0]
                budget = float(row.get("budget", 0) or 0)
                hourly = float(get_setting("hourly_rate", 25))
                hrs = 0
                if not tl.empty and "project_id" in tl.columns:
                    hrs = tl[tl["project_id"] == row["id"]]["hours"].sum() if not tl[tl["project_id"] == row["id"]].empty else 0
                cost = hrs * hourly
                profit = budget - cost
                margin = (profit / budget * 100) if budget else 0
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Budget", fmt_money(budget))
                c2.metric(f"Hours × ${hourly:.0f}/h", fmt_money(cost))
                c3.metric("Profit", fmt_money(profit))
                c4.metric("Margin %", f"{margin:.1f}%")
                if st.button("🤖 How to improve this margin?", key="marg_ai"):
                    prompt = (f"Project '{pname}': budget ${budget:.2f}, hours logged {hrs:.1f}, hourly ${hourly:.2f}, "
                              f"cost ${cost:.2f}, profit ${profit:.2f}, margin {margin:.1f}%. "
                              f"Give me 4 specific tactics to lift this margin above 40% without losing the client.")
                    with st.spinner(t("ai_typing")):
                        st.markdown(ai_chat(prompt, system=crm_system_prompt()))

        # Break-even
        with calc_tab3:
            st.markdown("**" + t("ai_breakeven") + "**")
            monthly_goal = float(get_setting("monthly_goal", 2500))
            hourly = float(get_setting("hourly_rate", 25))
            monthly_exp = ex["amount"].sum() if not ex.empty else 0
            be_hours = (monthly_goal + monthly_exp) / hourly if hourly else 0
            c1, c2, c3 = st.columns(3)
            c1.metric("Monthly goal", fmt_money(monthly_goal))
            c2.metric("Monthly expenses", fmt_money(monthly_exp))
            c3.metric(f"Break-even hours @ ${hourly:.0f}/h", f"{be_hours:.1f} h")
            if st.button("🤖 AI plan to hit break-even", key="be_ai"):
                prompt = (f"Monthly goal ${monthly_goal:.2f}, expenses ${monthly_exp:.2f}, hourly rate ${hourly:.2f}, "
                          f"break-even {be_hours:.1f} hours. Suggest a 4-week plan to hit this, "
                          f"using my actual pipeline and clients from the snapshot.")
                with st.spinner(t("ai_typing")):
                    st.markdown(ai_chat(prompt, system=crm_system_prompt()))

        # Hourly cost
        with calc_tab4:
            st.markdown("**" + t("ai_hourly_cost") + "**")
            des_income = st.number_input("Desired monthly income", value=2000.0, step=100.0)
            avail_h = st.number_input("Hours you can work / week", value=30.0, step=1.0)
            overhead = st.number_input("Monthly overhead (software, internet...)", value=50.0, step=10.0)
            billable_ratio = st.slider("Billable ratio %", 40, 100, 70)
            monthly_billable = avail_h * 4.33 * (billable_ratio / 100)
            required_rate = (des_income + overhead) / monthly_billable if monthly_billable else 0
            st.metric("Recommended hourly rate", fmt_money(required_rate))
            st.caption(f"Based on {monthly_billable:.1f} billable hours/month.")
            if st.button("🤖 Validate this rate for my market", key="hr_ai"):
                prompt = (f"I want monthly income ${des_income:.0f}, can work {avail_h:.0f} h/week, "
                          f"overhead ${overhead:.0f}, billable ratio {billable_ratio}%. "
                          f"Required hourly rate: ${required_rate:.2f}. Is this realistic for a freelance CRM user? "
                          f"Suggest 3 ways to increase the billable ratio and 2 ways to justify a higher rate.")
                with st.spinner(t("ai_typing")):
                    st.markdown(ai_chat(prompt, system=crm_system_prompt()))

    # ---------- Smart Alerts ----------
    with ai_sub[6]:
        st.subheader("🔔 " + t("ai_alerts"))
        st.caption("Auto-generated alerts based on your CRM state. No AI call needed for the scan; AI adds prioritization.")
        alerts = []
        today = date.today()
        leads_df = load_table("leads")
        if not leads_df.empty:
            ld = leads_df.copy()
            ld["nf"] = pd.to_datetime(ld["next_followup"], errors="coerce")
            od = ld[(ld["nf"] < pd.Timestamp(today)) & (~ld["stage"].isin(["Won", "Lost"]))]
            for _, r in od.iterrows():
                days_late = (today - r["nf"].date()).days if pd.notna(r["nf"]) else 0
                alerts.append({"severity": "HIGH" if days_late > 7 else "MED",
                               "type": "Overdue follow-up",
                               "msg": f"{r['name']} ({r.get('company','')}) — {days_late}d late. Stage: {r['stage']}.",
                               "action": f"Update stage or reschedule follow-up."})
        projects_df = load_table("projects")
        if not projects_df.empty:
            for _, r in projects_df.iterrows():
                try:
                    dl = pd.to_datetime(r["deadline"], errors="coerce")
                    if pd.notna(dl) and r["status"] == "In Progress":
                        days = (dl.date() - today).days
                        if days < 0:
                            alerts.append({"severity": "HIGH", "type": "Project past deadline",
                                           "msg": f"{r['name']} for {r['client_name']} — {abs(days)}d overdue. Progress {r['progress']}%.",
                                           "action": "Mark complete, or update deadline."})
                        elif days <= 7:
                            alerts.append({"severity": "MED", "type": "Deadline approaching",
                                           "msg": f"{r['name']} — {days}d left, progress {r['progress']}%.",
                                           "action": "Push progress or negotiate extension."})
                except Exception:
                    pass
        pa = load_table("payments")
        if not pa.empty:
            for _, r in pa.iterrows():
                if r["status"] in ("Pending", "Partial", "Overdue"):
                    try:
                        dd = pd.to_datetime(r["due_date"], errors="coerce")
                        if pd.notna(dd):
                            days = (dd.date() - today).days
                            if days < 0:
                                alerts.append({"severity": "HIGH", "type": "Unpaid invoice overdue",
                                               "msg": f"{r['id']} — {r['client_name']} — {fmt_money(r['amount'])} — {abs(days)}d late.",
                                               "action": "Send payment reminder or mark as Overdue."})
                            elif days <= 3:
                                alerts.append({"severity": "LOW", "type": "Invoice due soon",
                                               "msg": f"{r['id']} — {r['client_name']} — {fmt_money(r['amount'])} — due in {days}d.",
                                               "action": "Confirm client will pay on time."})
                    except Exception:
                        pass
        clients_df = load_table("clients")
        if not clients_df.empty:
            for _, r in clients_df.iterrows():
                if r["status"] == "Active":
                    try:
                        sd = pd.to_datetime(r["start_date"], errors="coerce")
                        if pd.notna(sd):
                            months = (today - sd.date()).days / 30
                            if months > 3 and float(r.get("lifetime_value", 0) or 0) < 200:
                                alerts.append({"severity": "MED", "type": "Stagnant client",
                                               "msg": f"{r['name']} active {months:.0f} months but LTV only ${r.get('lifetime_value',0):.0f}.",
                                               "action": "Upsell or schedule a check-in."})
                    except Exception:
                        pass
        if not alerts:
            st.success("✅ No critical alerts. You're on top of things.")
        else:
            sev_color = {"HIGH": "🔴", "MED": "🟡", "LOW": "🟢"}
            alerts_sorted = sorted(alerts, key=lambda a: {"HIGH": 0, "MED": 1, "LOW": 2}[a["severity"]])
            st.metric("Total alerts", len(alerts))
            st.metric("High priority", sum(1 for a in alerts if a["severity"] == "HIGH"))
            for a in alerts_sorted:
                st.markdown(f"**{sev_color[a['severity']]} {a['severity']} — {a['type']}**  ")
                st.caption(f"{a['msg']} → {a['action']}")
                st.divider()
            if st.button("🤖 Prioritize with AI", key="alert_ai"):
                prompt = ("Here are my current CRM alerts. Rank them by urgency+impact, "
                          "and tell me the top 3 to handle today with concrete scripts/actions:\n\n" +
                          "\n".join(f"- [{a['severity']}] {a['type']}: {a['msg']}" for a in alerts_sorted))
                with st.spinner(t("ai_typing")):
                    st.markdown(ai_chat(prompt, system=crm_system_prompt()))

    # ---------- Predictions ----------
    with ai_sub[7]:
        st.subheader("🔮 " + t("ai_predictions"))
        st.caption("AI-driven forecasts and risk scores. Uses your CRM data + LLM reasoning.")
        pred_tab1, pred_tab2, pred_tab3 = st.tabs([
            t("ai_revenue_forecast"), t("ai_lead_score"), t("ai_churn_risk")
        ])

        # Revenue forecast
        with pred_tab1:
            st.markdown("**" + t("ai_revenue_forecast") + "**")
            pa = load_table("payments"); ex = load_table("expenses")
            te = pa[pa["status"] == "Paid"]["amount"].sum() if not pa.empty and "status" in pa.columns else 0
            pen = pa[pa["status"].isin(["Pending", "Overdue"])]["amount"].sum() if not pa.empty and "status" in pa.columns else 0
            tex = ex["amount"].sum() if not ex.empty else 0
            pipeline_value = 0
            leads_df = load_table("leads")
            if not leads_df.empty:
                active = leads_df[~leads_df["stage"].isin(["Won", "Lost"])]
                pipeline_value = active["estimated_value"].sum() if not active.empty else 0
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Earned (YTD)", fmt_money(te))
            c2.metric("Pending", fmt_money(pen))
            c3.metric("Pipeline", fmt_money(pipeline_value))
            c4.metric("Expenses", fmt_money(tex))
            months = st.slider("Forecast horizon (months)", 1, 6, 3)
            if st.button("🔮 Forecast next " + str(months) + " months", type="primary", key="forecast_btn"):
                prompt = (f"Predict my revenue for the next {months} months. "
                         f"Current earned ${te:.2f}, pending ${pen:.2f}, pipeline (estimated) ${pipeline_value:.2f}, "
                         f"expenses ${tex:.2f}. Assume a realistic conversion rate per lead stage "
                         f"(New 5%, Contacted 15%, Proposal Sent 35%, Negotiation 65%). "
                         f"Give me a month-by-month table in markdown, then 3 risks and 3 opportunities.")
                with st.spinner(t("ai_typing")):
                    st.markdown(ai_chat(prompt, system=crm_system_prompt()))

        # Lead score
        with pred_tab2:
            st.markdown("**" + t("ai_lead_score") + "**")
            leads_df = load_table("leads")
            if leads_df.empty:
                st.info("No leads to score.")
            else:
                sel = st.selectbox("Pick lead", leads_df["name"].tolist(), key="lead_score_sel")
                row = leads_df[leads_df["name"] == sel].iloc[0]
                # Heuristic score
                stage_pts = {"New": 10, "Contacted": 30, "Proposal Sent": 55, "Negotiation": 75, "Won": 100, "Lost": 0}
                pri_pts = {"Hot": 25, "Warm": 15, "Cold": 5}
                base = stage_pts.get(row.get("stage", ""), 20) + pri_pts.get(row.get("priority", ""), 10)
                try:
                    nf = pd.to_datetime(row.get("next_followup"), errors="coerce")
                    if pd.notna(nf):
                        days_until = (nf.date() - today).days
                        if days_until < 0:
                            base -= 10
                        elif days_until <= 3:
                            base += 10
                except Exception:
                    pass
                ev = float(row.get("estimated_value", 0) or 0)
                if ev > 3000: base += 10
                elif ev > 1000: base += 5
                score = max(0, min(100, base))
                # Display gauge
                st.progress(score / 100, text=f"{score}/100 — " + ("🔥 Hot" if score >= 75 else ("⚠️ Warm" if score >= 45 else "❄️ Cold")))
                if st.button("🤖 Get AI conversion strategy", key="lead_score_ai"):
                    prompt = (f"Score this lead 0–100 and explain. Lead: {row.get('name','')} ({row.get('company','')}), "
                              f"stage={row.get('stage','')}, priority={row.get('priority','')}, "
                              f"estimated value ${ev:.0f}, next follow-up {row.get('next_followup','')}. "
                              f"My heuristic score is {score}/100. Validate or challenge it, and give 3 actions to push it above 80.")
                    with st.spinner(t("ai_typing")):
                        st.markdown(ai_chat(prompt, system=crm_system_prompt()))

        # Churn risk
        with pred_tab3:
            st.markdown("**" + t("ai_churn_risk") + "**")
            clients_df = load_table("clients")
            if clients_df.empty:
                st.info("No clients.")
            else:
                sel = st.selectbox("Pick client", clients_df["name"].tolist(), key="churn_sel")
                crow = clients_df[clients_df["name"] == sel].iloc[0]
                # Heuristic churn risk
                risk = 0
                rating = float(crow.get("rating", 3) or 3)
                if rating <= 2: risk += 40
                elif rating == 3: risk += 20
                try:
                    sd = pd.to_datetime(crow.get("start_date"), errors="coerce")
                    if pd.notna(sd):
                        months = (today - sd.date()).days / 30
                        if months > 6 and crow.get("status") == "On Hold":
                            risk += 30
                        if months > 12:
                            risk += 15
                except Exception:
                    pass
                if crow.get("status") == "Cancelled": risk = 100
                elif crow.get("status") == "On Hold": risk += 25
                # Check recent project activity
                projects_df = load_table("projects")
                if not projects_df.empty and "client_name" in projects_df.columns:
                    cp = projects_df[projects_df["client_name"] == sel]
                    if cp.empty:
                        risk += 15
                    else:
                        last_dl = pd.to_datetime(cp["deadline"], errors="coerce").max()
                        if pd.notna(last_dl):
                            months_since = (today - last_dl.date()).days / 30
                            if months_since > 3: risk += 20
                risk = max(0, min(100, int(risk)))
                col1, col2 = st.columns([3, 1])
                col1.progress(risk / 100, text=f"Churn risk: {risk}% — " +
                              ("🔴 High" if risk >= 60 else ("🟡 Medium" if risk >= 30 else "🟢 Low")))
                col2.metric("Client rating", f"{rating:.0f}★")
                if st.button("🤖 Get AI retention plan", key="churn_ai"):
                    prompt = (f"Predict churn risk for client {crow.get('name','')} ({crow.get('company','')}). "
                              f"Status: {crow.get('status','')}, rating {rating}/5, "
                              f"lifetime value ${crow.get('lifetime_value',0):.0f}, start {crow.get('start_date','')}. "
                              f"My heuristic risk: {risk}%. Suggest a 30-day retention plan with 4 specific actions.")
                    with st.spinner(t("ai_typing")):
                        st.markdown(ai_chat(prompt, system=crm_system_prompt()))

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
