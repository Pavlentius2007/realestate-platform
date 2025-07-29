"""
Утилиты для работы с конфигурацией в шаблонах
"""

from typing import Dict, Any
from backend.config.settings import settings
from backend.config.themes import theme_manager

def get_config_for_template() -> Dict[str, Any]:
    """Возвращает конфигурацию для передачи в шаблоны"""
    config = settings.get_dict()
    
    # Добавляем CSS переменные текущей темы
    config["theme_css"] = theme_manager.get_css_variables()
    config["custom_css"] = theme_manager.get_custom_css()
    
    return config

def get_brand_info() -> Dict[str, str]:
    """Возвращает информацию о бренде"""
    return {
        "name": settings.brand.name,
        "tagline": settings.brand.tagline,
        "logo_url": settings.brand.logo_url,
        "favicon_url": settings.brand.favicon_url,
    }

def get_contact_info() -> Dict[str, str]:
    """Возвращает контактную информацию"""
    return {
        "phone": settings.contact.phone,
        "whatsapp": settings.contact.whatsapp,
        "telegram": settings.contact.telegram,
        "email": settings.contact.email,
        "address": settings.contact.address,
        "office_address": settings.contact.office_address,
    }

def get_social_links() -> Dict[str, str]:
    """Возвращает ссылки на социальные сети"""
    social = {}
    if settings.contact.instagram:
        social["instagram"] = settings.contact.instagram
    if settings.contact.facebook:
        social["facebook"] = settings.contact.facebook
    if settings.contact.youtube:
        social["youtube"] = settings.contact.youtube
    if settings.contact.linkedin:
        social["linkedin"] = settings.contact.linkedin
    return social

def is_feature_enabled(feature_name: str) -> bool:
    """Проверяет, включена ли функция"""
    return getattr(settings.features, f"enable_{feature_name}", False)

def get_currency_info() -> Dict[str, str]:
    """Возвращает информацию о валюте"""
    return {
        "currency": settings.payment.currency,
        "symbol": settings.payment.currency_symbol,
    }

def get_seo_info() -> Dict[str, str]:
    """Возвращает SEO информацию"""
    return {
        "title": settings.seo.site_title,
        "description": settings.seo.site_description,
        "keywords": settings.seo.site_keywords,
        "og_image": settings.seo.og_image,
        "og_type": settings.seo.og_type,
    }

def get_analytics_scripts() -> str:
    """Возвращает скрипты аналитики"""
    scripts = []
    
    if settings.analytics.google_analytics_id:
        scripts.append(f"""
        <!-- Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={settings.analytics.google_analytics_id}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());
            gtag('config', '{settings.analytics.google_analytics_id}');
        </script>
        """)
    
    if settings.analytics.yandex_metrika_id:
        scripts.append(f"""
        <!-- Yandex Metrika -->
        <script type="text/javascript">
            (function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
            m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})
            (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
            ym({settings.analytics.yandex_metrika_id}, "init", {{
                clickmap:true,
                trackLinks:true,
                accurateTrackBounce:true
            }});
        </script>
        <noscript><div><img src="https://mc.yandex.ru/watch/{settings.analytics.yandex_metrika_id}" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
        """)
    
    if settings.analytics.facebook_pixel_id:
        scripts.append(f"""
        <!-- Facebook Pixel -->
        <script>
            !function(f,b,e,v,n,t,s)
            {{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
            n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
            if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
            n.queue=[];t=b.createElement(e);t.async=!0;
            t.src=v;s=b.getElementsByTagName(e)[0];
            s.parentNode.insertBefore(t,s)}}(window, document,'script',
            'https://connect.facebook.net/en_US/fbevents.js');
            fbq('init', '{settings.analytics.facebook_pixel_id}');
            fbq('track', 'PageView');
        </script>
        <noscript><img height="1" width="1" style="display:none"
            src="https://www.facebook.com/tr?id={settings.analytics.facebook_pixel_id}&ev=PageView&noscript=1"
        /></noscript>
        """)
    
    return "\n".join(scripts) 