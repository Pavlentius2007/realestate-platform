-- Создание таблицы projects
-- Выполните этот скрипт в PGAdmin4

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    slug VARCHAR UNIQUE NOT NULL,
    title VARCHAR NOT NULL,
    subtitle VARCHAR,
    description TEXT,
    location VARCHAR,
    district VARCHAR,
    
    -- Основные характеристики
    developer VARCHAR,
    completion_year INTEGER,
    total_units INTEGER,
    floors INTEGER,
    
    -- Цены
    price_from FLOAT,
    price_to FLOAT,
    currency VARCHAR DEFAULT 'THB',
    
    -- Координаты
    lat FLOAT,
    lng FLOAT,
    
    -- Изображения и медиа
    hero_image VARCHAR,
    gallery_images TEXT[], -- Массив строк для изображений
    video_url VARCHAR,
    
    -- Особенности и удобства
    highlights TEXT[], -- Массив строк для highlights
    amenities TEXT[], -- Массив строк для удобств
    
    -- Планировки и типы квартир
    unit_types TEXT, -- JSON строка
    
    -- Платежи и инвестиции
    payment_plan TEXT,
    down_payment VARCHAR,
    monthly_payment VARCHAR,
    roi_info TEXT,
    
    -- Контактная информация
    sales_office_address VARCHAR,
    sales_office_phone VARCHAR,
    sales_office_email VARCHAR,
    
    -- Статус проекта
    status VARCHAR DEFAULT 'active',
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- Мета-информация
    meta_title VARCHAR,
    meta_description VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание индексов
CREATE INDEX idx_projects_slug ON projects(slug);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_is_featured ON projects(is_featured);
CREATE INDEX idx_projects_district ON projects(district);

-- Комментарии к таблице
COMMENT ON TABLE projects IS 'Таблица проектов недвижимости';
COMMENT ON COLUMN projects.slug IS 'Уникальный идентификатор для URL';
COMMENT ON COLUMN projects.status IS 'Статус проекта: active, completed, upcoming';
COMMENT ON COLUMN projects.unit_types IS 'JSON с информацией о типах квартир';

-- Вставка тестовых данных
INSERT INTO projects (
    slug, title, subtitle, description, location, district, developer,
    completion_year, price_from, price_to, hero_image, highlights, amenities,
    payment_plan, status, is_featured
) VALUES 
(
    'pty-residence',
    'PTY Residence',
    'Современный жилой комплекс в центре Паттайи',
    'PTY Residence - это новый уровень комфорта в самом сердце Паттайи. Комплекс предлагает современные апартаменты с панорамными видами на море и город.',
    'Паттайя',
    'Центральная Паттайя',
    'PTY Development',
    2025,
    2500000,
    8500000,
    '/static/img/pty-hero.jpg',
    ARRAY['Панорамные виды на море', 'Центральное расположение', 'Современный дизайн', 'Высокий ROI'],
    ARRAY['Бассейн на крыше', 'Фитнес-центр', 'Спа-зона', 'Консьерж-сервис', 'Охраняемая территория'],
    'Первоначальный взнос 30%, остальное в рассрочку до 2 лет',
    'active',
    true
),
(
    'zenith-pattaya',
    'Zenith Pattaya',
    'Элитная высотка с видом на залив',
    'Zenith Pattaya - самая высокая башня Паттайи с роскошными апартаментами и непревзойденными видами на Сиамский залив.',
    'Паттайя',
    'Пратамнак',
    'Zenith Group',
    2026,
    4000000,
    15000000,
    '/static/img/zenith-hero.jpg',
    ARRAY['Самая высокая башня Паттайи', 'Роскошные апартаменты', 'Инфинити-бассейн', 'Частный пляжный клуб'],
    ARRAY['Инфинити-бассейн', 'Частный пляж', 'Мишленовский ресторан', 'Вертолетная площадка', 'Private club'],
    'Гибкие условия оплаты, возможна рассрочка до 3 лет',
    'active',
    true
); 