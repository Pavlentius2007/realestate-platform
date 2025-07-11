"""
Конфигурация для white label решения Sianoro
Все настраиваемые параметры вынесены в этот файл
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class BrandConfig:
    """Конфигурация брендинга"""
    name: str = "Sianoro"
    tagline: str = "Ваш надежный партнер в сфере недвижимости в Таиланде"
    logo_url: str = "/static/img/sianoro-logo.png"
    favicon_url: str = "/static/img/favicon.ico"
    
    # Цветовая схема
    primary_color: str = "#1e90ff"
    secondary_color: str = "#005bb5"
    accent_color: str = "#3b82f6"
    success_color: str = "#10b981"
    warning_color: str = "#f59e0b"
    error_color: str = "#ef4444"
    
    # Градиенты
    primary_gradient: str = "linear-gradient(135deg, #0074E4 0%, #005bb5 100%)"
    hero_gradient: str = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    
    # Шрифты
    font_family: str = "'Inter', sans-serif"
    heading_font: str = "'Inter', sans-serif"

@dataclass
class ContactConfig:
    """Конфигурация контактов"""
    phone: str = "+66 1234 5678"
    whatsapp: str = "+66 1234 5678"
    telegram: str = "InvestThailand"
    email: str = "info@sianoro.com"
    
    # Адрес
    address: str = "Паттайя, Таиланд"
    office_address: str = "Паттайя, Таиланд"
    
    # Социальные сети
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    linkedin: Optional[str] = None

@dataclass
class LocalizationConfig:
    """Конфигурация локализации"""
    default_language: str = "ru"
    supported_languages: List[str] = field(default_factory=lambda: ["ru", "en", "th", "zh"])

@dataclass
class FeaturesConfig:
    """Конфигурация функций"""
    enable_calculator: bool = True
    enable_ai_assistant: bool = True
    enable_favorites: bool = True
    enable_articles: bool = True
    enable_projects: bool = True
    enable_rental: bool = True
    enable_investment_calculator: bool = True
    calculator_currencies: List[str] = field(default_factory=lambda: ["THB", "USD", "RUB", "CNY"])
    enable_pdf_export: bool = True
    enable_presets: bool = True
    enable_crm: bool = True
    enable_analytics: bool = True
    enable_payments: bool = False
    
    def __post_init__(self):
        if self.calculator_currencies is None:
            self.calculator_currencies = ["THB", "USD", "RUB", "CNY"]

@dataclass
class SEOConfig:
    """SEO конфигурация"""
    site_title: str = "Sianoro - Недвижимость в Таиланде"
    site_description: str = "Найдите идеальную недвижимость для жизни и инвестиций в Паттайе"
    site_keywords: str = "недвижимость, таиланд, паттайя, квартиры, виллы, инвестиции"
    
    # Open Graph
    og_image: str = "/static/img/og-image.jpg"
    og_type: str = "website"

@dataclass
class AnalyticsConfig:
    """Конфигурация аналитики"""
    google_analytics_id: Optional[str] = None
    yandex_metrika_id: Optional[str] = None
    facebook_pixel_id: Optional[str] = None

@dataclass
class PaymentConfig:
    """Конфигурация платежей"""
    currency: str = "THB"
    currency_symbol: str = "฿"
    enable_payments: bool = False

class Settings:
    """Основной класс настроек"""
    
    def __init__(self):
        # Загружаем конфигурации
        self.brand = BrandConfig()
        self.contact = ContactConfig()
        self.localization = LocalizationConfig()
        self.features = FeaturesConfig()
        self.seo = SEOConfig()
        self.analytics = AnalyticsConfig()
        self.payment = PaymentConfig()
        
        # Загружаем кастомные настройки из переменных окружения
        self._load_from_env()
    
    def _load_from_env(self):
        """Загружает настройки из переменных окружения"""
        # Брендинг
        brand_name = os.getenv("BRAND_NAME")
        if brand_name is not None:
            self.brand.name = brand_name
        brand_tagline = os.getenv("BRAND_TAGLINE")
        if brand_tagline is not None:
            self.brand.tagline = brand_tagline
        primary_color = os.getenv("PRIMARY_COLOR")
        if primary_color is not None:
            self.brand.primary_color = primary_color
        
        # Контакты
        contact_phone = os.getenv("CONTACT_PHONE")
        if contact_phone is not None:
            self.contact.phone = contact_phone
        contact_whatsapp = os.getenv("CONTACT_WHATSAPP")
        if contact_whatsapp is not None:
            self.contact.whatsapp = contact_whatsapp
        contact_telegram = os.getenv("CONTACT_TELEGRAM")
        if contact_telegram is not None:
            self.contact.telegram = contact_telegram
        contact_email = os.getenv("CONTACT_EMAIL")
        if contact_email is not None:
            self.contact.email = contact_email
        
        # Функции
        if os.getenv("ENABLE_CALCULATOR"):
            enable_calc = os.getenv("ENABLE_CALCULATOR")
            if enable_calc is not None:
                self.features.enable_calculator = enable_calc.lower() == "true"
        if os.getenv("ENABLE_AI_ASSISTANT"):
            enable_ai = os.getenv("ENABLE_AI_ASSISTANT")
            if enable_ai is not None:
                self.features.enable_ai_assistant = enable_ai.lower() == "true"
    
    def get_dict(self) -> Dict:
        """Возвращает все настройки в виде словаря для передачи в шаблоны"""
        return {
            "brand": {
                "name": self.brand.name,
                "tagline": self.brand.tagline,
                "logo_url": self.brand.logo_url,
                "favicon_url": self.brand.favicon_url,
                "primary_color": self.brand.primary_color,
                "secondary_color": self.brand.secondary_color,
                "accent_color": self.brand.accent_color,
                "success_color": self.brand.success_color,
                "warning_color": self.brand.warning_color,
                "error_color": self.brand.error_color,
                "primary_gradient": self.brand.primary_gradient,
                "hero_gradient": self.brand.hero_gradient,
                "font_family": self.brand.font_family,
                "heading_font": self.brand.heading_font,
            },
            "contact": {
                "phone": self.contact.phone,
                "whatsapp": self.contact.whatsapp,
                "telegram": self.contact.telegram,
                "email": self.contact.email,
                "address": self.contact.address,
                "office_address": self.contact.office_address,
                "instagram": self.contact.instagram,
                "facebook": self.contact.facebook,
                "youtube": self.contact.youtube,
                "linkedin": self.contact.linkedin,
            },
            "localization": {
                "default_language": self.localization.default_language,
                "supported_languages": self.localization.supported_languages,
            },
            "features": {
                "enable_calculator": self.features.enable_calculator,
                "enable_ai_assistant": self.features.enable_ai_assistant,
                "enable_favorites": self.features.enable_favorites,
                "enable_articles": self.features.enable_articles,
                "enable_projects": self.features.enable_projects,
                "enable_rental": self.features.enable_rental,
                "calculator_currencies": self.features.calculator_currencies,
            },
            "seo": {
                "site_title": self.seo.site_title,
                "site_description": self.seo.site_description,
                "site_keywords": self.seo.site_keywords,
                "og_image": self.seo.og_image,
                "og_type": self.seo.og_type,
            },
            "analytics": {
                "google_analytics_id": self.analytics.google_analytics_id,
                "yandex_metrika_id": self.analytics.yandex_metrika_id,
                "facebook_pixel_id": self.analytics.facebook_pixel_id,
            },
            "payment": {
                "currency": self.payment.currency,
                "currency_symbol": self.payment.currency_symbol,
                "enable_payments": self.payment.enable_payments,
            }
        }

# Глобальный экземпляр настроек
settings = Settings() 