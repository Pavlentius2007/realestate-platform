"""
Система тем для white label решения
Позволяет легко кастомизировать внешний вид сайта
"""

from typing import Dict, Any
from .settings import settings

class ThemeManager:
    """Менеджер тем для кастомизации стилей"""
    
    def __init__(self):
        self.current_theme = "default"
        self.themes = {
            "default": self._get_default_theme(),
            "premium": self._get_premium_theme(),
            "minimal": self._get_minimal_theme(),
        }
    
    def _get_default_theme(self) -> Dict[str, Any]:
        """Тема по умолчанию"""
        return {
            "colors": {
                "primary": settings.brand.primary_color,
                "secondary": settings.brand.secondary_color,
                "accent": settings.brand.accent_color,
                "success": settings.brand.success_color,
                "warning": settings.brand.warning_color,
                "error": settings.brand.error_color,
                "background": "#ffffff",
                "surface": "#f8fafc",
                "text": "#1a202c",
                "text_secondary": "#4a5568",
                "border": "#e2e8f0",
            },
            "gradients": {
                "primary": settings.brand.primary_gradient,
                "hero": settings.brand.hero_gradient,
                "card": "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
            },
            "typography": {
                "font_family": settings.brand.font_family,
                "heading_font": settings.brand.heading_font,
                "font_size_base": "16px",
                "line_height_base": "1.6",
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem",
                "2xl": "3rem",
            },
            "border_radius": {
                "sm": "0.25rem",
                "md": "0.5rem",
                "lg": "0.75rem",
                "xl": "1rem",
            },
            "shadows": {
                "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
            },
        }
    
    def _get_premium_theme(self) -> Dict[str, Any]:
        """Премиум тема с золотыми акцентами"""
        theme = self._get_default_theme()
        theme["colors"].update({
            "primary": "#d4af37",
            "secondary": "#b8860b",
            "accent": "#ffd700",
        })
        theme["gradients"].update({
            "primary": "linear-gradient(135deg, #d4af37 0%, #b8860b 100%)",
            "hero": "linear-gradient(135deg, #d4af37 0%, #8b6914 100%)",
        })
        return theme
    
    def _get_minimal_theme(self) -> Dict[str, Any]:
        """Минималистичная тема"""
        theme = self._get_default_theme()
        theme["colors"].update({
            "primary": "#000000",
            "secondary": "#333333",
            "accent": "#666666",
            "background": "#ffffff",
            "surface": "#fafafa",
        })
        theme["gradients"].update({
            "primary": "linear-gradient(135deg, #000000 0%, #333333 100%)",
            "hero": "linear-gradient(135deg, #fafafa 0%, #e5e5e5 100%)",
        })
        return theme
    
    def _get_luxury_theme(self) -> Dict[str, Any]:
        """Люксовая тема с золотыми акцентами"""
        theme = self._get_default_theme()
        theme["colors"].update({
            "primary": "#d4af37",
            "secondary": "#b8860b",
            "accent": "#ffd700",
            "success": "#2d5016",
            "warning": "#b8860b",
            "error": "#8b0000",
            "background": "#1a1a1a",
            "surface": "#2d2d2d",
            "text": "#ffffff",
            "text_secondary": "#cccccc",
            "border": "#444444",
        })
        theme["gradients"].update({
            "primary": "linear-gradient(135deg, #d4af37 0%, #b8860b 100%)",
            "hero": "linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)",
            "card": "linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%)",
        })
        theme["shadows"].update({
            "sm": "0 1px 2px 0 rgba(212, 175, 55, 0.1)",
            "md": "0 4px 6px -1px rgba(212, 175, 55, 0.2)",
            "lg": "0 10px 15px -3px rgba(212, 175, 55, 0.3)",
            "xl": "0 20px 25px -5px rgba(212, 175, 55, 0.4)",
        })
        return theme
    
    def _get_ocean_theme(self) -> Dict[str, Any]:
        """Морская тема с синими тонами"""
        theme = self._get_default_theme()
        theme["colors"].update({
            "primary": "#006994",
            "secondary": "#004d73",
            "accent": "#00bfff",
            "success": "#00a86b",
            "warning": "#ffa500",
            "error": "#dc143c",
            "background": "#f0f8ff",
            "surface": "#e6f3ff",
            "text": "#1a1a1a",
            "text_secondary": "#4a4a4a",
            "border": "#b3d9ff",
        })
        theme["gradients"].update({
            "primary": "linear-gradient(135deg, #006994 0%, #004d73 100%)",
            "hero": "linear-gradient(135deg, #006994 0%, #00bfff 100%)",
            "card": "linear-gradient(135deg, #e6f3ff 0%, #f0f8ff 100%)",
        })
        return theme
    
    def set_theme(self, theme_name: str):
        """Устанавливает активную тему"""
        if theme_name in self.themes:
            self.current_theme = theme_name
    
    def get_theme(self, theme_name: str = None) -> Dict[str, Any]:
        """Возвращает тему"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes["default"])
    
    def get_css_variables(self, theme_name: str = None) -> str:
        """Генерирует CSS переменные для темы"""
        theme = self.get_theme(theme_name)
        
        css_vars = []
        
        # Цвета
        for name, value in theme["colors"].items():
            css_vars.append(f"--color-{name}: {value};")
        
        # Градиенты
        for name, value in theme["gradients"].items():
            css_vars.append(f"--gradient-{name}: {value};")
        
        # Типографика
        for name, value in theme["typography"].items():
            css_vars.append(f"--font-{name}: {value};")
        
        # Отступы
        for name, value in theme["spacing"].items():
            css_vars.append(f"--spacing-{name}: {value};")
        
        # Радиусы
        for name, value in theme["border_radius"].items():
            css_vars.append(f"--radius-{name}: {value};")
        
        # Тени
        for name, value in theme["shadows"].items():
            css_vars.append(f"--shadow-{name}: {value};")
        
        return "\n".join(css_vars)
    
    def get_custom_css(self, theme_name: str = None) -> str:
        """Возвращает кастомные CSS стили для темы"""
        theme = self.get_theme(theme_name)
        
        return f"""
        :root {{
            {self.get_css_variables(theme_name)}
        }}
        
        /* Кастомные стили для темы {theme_name or self.current_theme} */
        .btn-primary {{
            background: var(--gradient-primary);
            border: none;
            color: white;
            padding: var(--spacing-md) var(--spacing-lg);
            border-radius: var(--radius-md);
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}
        
        .card {{
            background: var(--color-surface);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            padding: var(--spacing-lg);
        }}
        
        .hero-section {{
            background: var(--gradient-hero);
            color: white;
        }}
        """

# Глобальный экземпляр менеджера тем
theme_manager = ThemeManager() 