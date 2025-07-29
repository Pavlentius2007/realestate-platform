#!/usr/bin/env python
"""
Скрипт для добавления дополнительных переводов
"""

import polib
from pathlib import Path

# Дополнительные переводы
ADDITIONAL_EN_TRANSLATIONS = {
    "Бюджет (тыс ฿/мес)": "Budget (k ฿/month)", 
    "Срок аренды": "Rental Period",
    "Любой срок": "Any period",
    "Краткосрочная (до 1 мес)": "Short-term (up to 1 month)",
    "Среднесрочная (1-6 мес)": "Medium-term (1-6 months)", 
    "Долгосрочная (6+ мес)": "Long-term (6+ months)",
    "Меблированная": "Furnished",
    "С животными": "Pets allowed",
    "Бассейн": "Pool",
    "Спортзал": "Gym",
}

ADDITIONAL_TH_TRANSLATIONS = {
    "Бюджет (тыс ฿/мес)": "งบประมาณ (พัน ฿/เดือน)",
    "Срок аренды": "ระยะเวลาเช่า", 
    "Любой срок": "ระยะเวลาใดก็ได้",
    "Краткосрочная (до 1 мес)": "ระยะสั้น (ไม่เกิน 1 เดือน)",
    "Среднесрочная (1-6 мес)": "ระยะกลาง (1-6 เดือน)",
    "Долгосрочная (6+ мес)": "ระยะยาว (6+ เดือน)",
    "Меблированная": "มีเฟอร์นิเจอร์",
    "С животными": "อนุญาตสัตว์เลี้ยง",
    "Бассейн": "สระว่ายน้ำ",
    "Спортзал": "ห้องออกกำลังกาย",
}

ADDITIONAL_ZH_TRANSLATIONS = {
    "Бюджет (тыс ฿/мес)": "预算（千泰铢/月）",
    "Срок аренды": "租期",
    "Любой срок": "任何期限",
    "Краткосрочная (до 1 мес)": "短期（不超过1个月）",
    "Среднесрочная (1-6 мес)": "中期（1-6个月）",
    "Долгосрочная (6+ мес)": "长期（6个月以上）",
    "Меблированная": "已配备家具",
    "С животными": "允许宠物",
    "Бассейн": "游泳池",
    "Спортзал": "健身房",
}

def add_translations(lang: str, translations: dict):
    """Добавляет переводы в .po файл"""
    
    translations_dir = Path("backend/translations")
    po_file_path = translations_dir / lang / "LC_MESSAGES" / "messages.po"
    
    if not po_file_path.exists():
        print(f"❌ Файл {po_file_path} не найден")
        return 0
    
    try:
        po = polib.pofile(str(po_file_path))
        
        # Получаем существующие msgid
        existing_msgids = {entry.msgid for entry in po}
        
        added_count = 0
        updated_count = 0
        
        for russian_text, translation in translations.items():
            if russian_text in existing_msgids:
                # Обновляем существующий перевод если он пустой
                for entry in po:
                    if entry.msgid == russian_text and not entry.msgstr:
                        entry.msgstr = translation
                        updated_count += 1
                        break
            else:
                # Добавляем новый перевод
                entry = polib.POEntry(
                    msgid=russian_text,
                    msgstr=translation,
                    comment='Добавлено дополнительно'
                )
                po.append(entry)
                added_count += 1
        
        po.save(str(po_file_path))
        print(f"✅ {lang}: добавлено {added_count}, обновлено {updated_count} переводов")
        return added_count + updated_count
        
    except Exception as e:
        print(f"❌ Ошибка при работе с {lang}: {e}")
        return 0

def main():
    """Основная функция"""
    
    print("🌍 Добавление дополнительных переводов")
    print("=" * 45)
    
    # Добавляем переводы для всех языков
    languages = {
        'en': ADDITIONAL_EN_TRANSLATIONS,
        'th': ADDITIONAL_TH_TRANSLATIONS,
        'zh': ADDITIONAL_ZH_TRANSLATIONS
    }
    
    total_updated = 0
    for lang, translations in languages.items():
        count = add_translations(lang, translations)
        total_updated += count
    
    print(f"\n🎯 Всего добавлено/обновлено переводов: {total_updated}")
    print(f"\n💡 Следующий шаг: python backend/compile_translations.py")

if __name__ == "__main__":
    main() 