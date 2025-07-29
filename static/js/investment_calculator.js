// Инвестиционный калькулятор Sianoro - Улучшенная версия

document.addEventListener('DOMContentLoaded', function() {
    // Курсы валют (обновляются через API)
    let exchangeRates = {
        'THB': 1,
        'USD': 0.028,
        'RUB': 2.5,
        'CNY': 0.2
    };
    
    // Элементы формы
    const currencySelect = document.getElementById('currency');
    const currencyRate = document.getElementById('currency-rate');
    const calculateBtn = document.getElementById('calculate-btn');
    const resultsDiv = document.getElementById('calc-results');
    
    // Загрузка курсов валют с API
    async function loadExchangeRates() {
        try {
            // Используем бесплатный API exchangerate.host
            const response = await fetch('https://api.exchangerate.host/latest?base=THB&symbols=USD,RUB,CNY');
            const data = await response.json();
            
            if (data.success && data.rates) {
                exchangeRates = {
                    'THB': 1,
                    'USD': data.rates.USD || 0.028,
                    'RUB': data.rates.RUB || 2.5,
                    'CNY': data.rates.CNY || 0.2
                };
                
                // Обновляем отображение курса
                updateCurrencyRate();
                
                console.log('Курсы валют обновлены:', exchangeRates);
            }
        } catch (error) {
            console.warn('Не удалось загрузить курсы валют, используем значения по умолчанию:', error);
        }
    }
    
    // Обновление курса валют
    function updateCurrencyRate() {
        const selectedCurrency = currencySelect.value;
        const rate = exchangeRates[selectedCurrency];
        if (rate && rate !== 1) {
            currencyRate.textContent = `1 THB = ${rate.toFixed(4)} ${selectedCurrency}`;
        } else {
            currencyRate.textContent = '';
        }
    }
    
    // Конвертация валют
    function convertFromTHB(amount, toCurrency) {
        const rate = exchangeRates[toCurrency] || 1;
        return amount * rate;
    }
    
    function convertToTHB(amount, fromCurrency) {
        const rate = exchangeRates[fromCurrency] || 1;
        return amount / rate;
    }
    
    // Форматирование чисел
    function formatNumber(num, currency = 'THB') {
        const symbols = {
            'THB': '฿',
            'USD': '$',
            'RUB': '₽',
            'CNY': '¥'
        };
        
        const symbol = symbols[currency] || '฿';
        return symbol + num.toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
    }
    
    // Создание графика прироста цены
    function createPriceChart(initialPrice, futurePrice, years, currency) {
        const canvas = document.getElementById('price-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const width = canvas.width = canvas.offsetWidth;
        const height = canvas.height = 200;
        
        // Очистка канваса
        ctx.clearRect(0, 0, width, height);
        
        // Данные для графика
        const data = [];
        for (let i = 0; i <= years; i++) {
            const price = initialPrice * Math.pow(futurePrice / initialPrice, i / years);
            data.push({ year: i, price: price });
        }
        
        // Настройки графика
        const padding = 40;
        const chartWidth = width - 2 * padding;
        const chartHeight = height - 2 * padding;
        
        const maxPrice = Math.max(...data.map(d => d.price));
        const minPrice = Math.min(...data.map(d => d.price));
        const priceRange = maxPrice - minPrice;
        
        // Фон
        ctx.fillStyle = '#f8fafc';
        ctx.fillRect(0, 0, width, height);
        
        // Сетка
        ctx.strokeStyle = '#e2e8f0';
        ctx.lineWidth = 1;
        
        // Горизонтальные линии
        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight * i) / 5;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(width - padding, y);
            ctx.stroke();
        }
        
        // Вертикальные линии
        for (let i = 0; i <= years; i++) {
            const x = padding + (chartWidth * i) / years;
            ctx.beginPath();
            ctx.moveTo(x, padding);
            ctx.lineTo(x, height - padding);
            ctx.stroke();
        }
        
        // Линия графика
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;
        ctx.beginPath();
        
        data.forEach((point, index) => {
            const x = padding + (chartWidth * point.year) / years;
            const y = height - padding - ((point.price - minPrice) / priceRange) * chartHeight;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // Точки на графике
        ctx.fillStyle = '#3b82f6';
        data.forEach(point => {
            const x = padding + (chartWidth * point.year) / years;
            const y = height - padding - ((point.price - minPrice) / priceRange) * chartHeight;
            
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
        });
        
        // Подписи осей
        ctx.fillStyle = '#64748b';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        
        // Годы
        for (let i = 0; i <= years; i++) {
            const x = padding + (chartWidth * i) / years;
            ctx.fillText(i.toString(), x, height - 10);
        }
        
        // Цены
        ctx.textAlign = 'right';
        for (let i = 0; i <= 5; i++) {
            const price = minPrice + (priceRange * i) / 5;
            const y = height - padding - (chartHeight * i) / 5;
            ctx.fillText(formatNumber(convertFromTHB(price, currency), currency), padding - 5, y + 4);
        }
    }
    
    // Основная функция расчета
    function calculateInvestment() {
        try {
            // Получаем значения из формы
            const currency = currencySelect.value;
            const price = parseFloat(document.getElementById('price').value) || 0;
            const area = parseFloat(document.getElementById('area').value) || 0;
            const deposit = parseFloat(document.getElementById('deposit').value) || 0;
            const contractPercent = parseFloat(document.getElementById('contract').value) || 0;
            const installmentPercent = parseFloat(document.getElementById('installment').value) || 0;
            const registrationPercent = parseFloat(document.getElementById('registration').value) || 0;
            const sinking = parseFloat(document.getElementById('sinking').value) || 0;
            const maintenance = parseFloat(document.getElementById('maintenance').value) || 0;
            const growthPercent = parseFloat(document.getElementById('growth').value) || 0;
            const years = parseFloat(document.getElementById('years').value) || 0;
            const rentYieldPercent = parseFloat(document.getElementById('rent_yield').value) || 0;
            
            // Проверка обязательных полей
            if (price <= 0 || area <= 0) {
                alert('Пожалуйста, заполните стоимость квартиры и площадь');
                return;
            }
            
            // Конвертируем в THB если нужно
            const priceInTHB = currency === 'THB' ? price : convertToTHB(price, currency);
            
            // Расчеты
            const contractAmount = priceInTHB * (contractPercent / 100);
            const installmentAmount = priceInTHB * (installmentPercent / 100);
            const registrationAmount = priceInTHB * (registrationPercent / 100);
            
            // Итого вложено до окончания строительства
            const totalInvested = deposit + contractAmount + installmentAmount + registrationAmount + sinking;
            
            // Прогнозируемая цена через N лет
            const futurePrice = priceInTHB * Math.pow(1 + growthPercent / 100, years);
            
            // Прибыль на момент окончания строительства
            const profit = futurePrice - totalInvested;
            
            // Доход от аренды в год (от будущей цены)
            const rentIncome = futurePrice * (rentYieldPercent / 100);
            
            // Общий доход от аренды за весь период
            const totalRentIncome = rentIncome * years;
            
            // ROI за год (на основе арендного дохода)
            const roiYear = totalInvested > 0 ? (rentIncome / totalInvested) * 100 : 0;
            
            // ROI к окончанию строительства (прибыль + аренда)
            const roiTotal = totalInvested > 0 ? ((profit + totalRentIncome) / totalInvested) * 100 : 0;
            
            // Цена за м²
            const pricePerM2 = priceInTHB / area;
            
            // Конвертируем результаты в выбранную валюту
            const convertedResults = {
                totalInvested: convertFromTHB(totalInvested, currency),
                futurePrice: convertFromTHB(futurePrice, currency),
                profit: convertFromTHB(profit, currency),
                rentIncome: convertFromTHB(rentIncome, currency),
                totalRentIncome: convertFromTHB(totalRentIncome, currency),
                pricePerM2: convertFromTHB(pricePerM2, currency),
                roiYear: roiYear,
                roiTotal: roiTotal
            };
            
            // Отображаем результаты
            document.getElementById('result-invested').textContent = formatNumber(convertedResults.totalInvested, currency);
            document.getElementById('result-future-price').textContent = formatNumber(convertedResults.futurePrice, currency);
            document.getElementById('result-profit').textContent = formatNumber(convertedResults.profit, currency);
            document.getElementById('result-rent').textContent = formatNumber(convertedResults.totalRentIncome, currency);
            document.getElementById('result-roi-year').textContent = roiYear.toFixed(1) + '%';
            document.getElementById('result-roi-total').textContent = roiTotal.toFixed(1) + '%';
            document.getElementById('result-price-m2').textContent = formatNumber(convertedResults.pricePerM2, currency);
            document.getElementById('result-years').textContent = years;
            
            // Дублируем для второго места
            const resultYearsRent = document.getElementById('result-years-rent');
            if (resultYearsRent) {
                resultYearsRent.textContent = years;
            }
            
            // Создаем график
            setTimeout(() => {
                createPriceChart(priceInTHB, futurePrice, years, currency);
            }, 100);
            
            // Показываем результаты
            resultsDiv.classList.remove('hidden');
            
            // Прокрутка к результатам на мобильных устройствах
            if (window.innerWidth < 768) {
                resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            
            // Сохраняем в localStorage
            const calculation = {
                timestamp: new Date().toISOString(),
                inputs: {
                    currency, price, area, deposit, contractPercent, installmentPercent,
                    registrationPercent, sinking, maintenance, growthPercent, years, rentYieldPercent
                },
                results: convertedResults
            };
            
            localStorage.setItem('lastCalculation', JSON.stringify(calculation));
            
        } catch (error) {
            console.error('Ошибка расчета:', error);
            alert('Произошла ошибка при расчете. Проверьте введенные данные.');
        }
    }
    
    // Улучшенная генерация PDF отчета с помощью jsPDF
    function generatePDF() {
        const calculation = JSON.parse(localStorage.getItem('lastCalculation'));
        if (!calculation) {
            alert('Сначала выполните расчет');
            return;
        }
        
        try {
            // Проверяем наличие jsPDF
            if (typeof window.jsPDF === 'undefined') {
                // Fallback - простой текстовый отчет
                generateTextReport(calculation);
                return;
            }
            
            const { jsPDF } = window.jsPDF;
            const doc = new jsPDF();
            
            // Заголовок
            doc.setFontSize(20);
            doc.setFont(undefined, 'bold');
            doc.text('ИНВЕСТИЦИОННЫЙ КАЛЬКУЛЯТОР SIANORO', 20, 30);
            
            doc.setFontSize(12);
            doc.setFont(undefined, 'normal');
            doc.text(`Дата расчета: ${new Date(calculation.timestamp).toLocaleDateString('ru-RU')}`, 20, 45);
            
            // Исходные данные
            doc.setFontSize(16);
            doc.setFont(undefined, 'bold');
            doc.text('ИСХОДНЫЕ ДАННЫЕ:', 20, 65);
            
            doc.setFontSize(11);
            doc.setFont(undefined, 'normal');
            let y = 80;
            
            const inputs = [
                [`Стоимость квартиры:`, `${formatNumber(calculation.inputs.price, calculation.inputs.currency)}`],
                [`Площадь:`, `${calculation.inputs.area} м²`],
                [`Депозит:`, `${formatNumber(calculation.inputs.deposit, calculation.inputs.currency)}`],
                [`Контрактный платеж:`, `${calculation.inputs.contractPercent}%`],
                [`Рассрочка:`, `${calculation.inputs.installmentPercent}%`],
                [`Оформление:`, `${calculation.inputs.registrationPercent}%`],
                [`Sinking Fund:`, `${formatNumber(calculation.inputs.sinking, calculation.inputs.currency)}`],
                [`Maintenance Fee:`, `${formatNumber(calculation.inputs.maintenance, calculation.inputs.currency)}`],
                [`Прогноз роста:`, `${calculation.inputs.growthPercent}% в год`],
                [`Срок:`, `${calculation.inputs.years} лет`],
                [`Доход от аренды:`, `${calculation.inputs.rentYieldPercent}% в год`]
            ];
            
            inputs.forEach(([label, value]) => {
                doc.text(label, 25, y);
                doc.text(value, 100, y);
                y += 7;
            });
            
            // Результаты
            y += 10;
            doc.setFontSize(16);
            doc.setFont(undefined, 'bold');
            doc.text('РЕЗУЛЬТАТЫ:', 20, y);
            
            y += 15;
            doc.setFontSize(11);
            doc.setFont(undefined, 'normal');
            
            const results = [
                [`Итого вложено:`, `${formatNumber(calculation.results.totalInvested, calculation.inputs.currency)}`],
                [`Прогнозируемая цена:`, `${formatNumber(calculation.results.futurePrice, calculation.inputs.currency)}`],
                [`Прибыль:`, `${formatNumber(calculation.results.profit, calculation.inputs.currency)}`],
                [`Доход от аренды:`, `${formatNumber(calculation.results.rentIncome, calculation.inputs.currency)} в год`],
                [`ROI за год:`, `${calculation.results.roiYear.toFixed(1)}%`],
                [`ROI общий:`, `${calculation.results.roiTotal.toFixed(1)}%`],
                [`Цена за м²:`, `${formatNumber(calculation.results.pricePerM2, calculation.inputs.currency)}`]
            ];
            
            results.forEach(([label, value]) => {
                doc.text(label, 25, y);
                doc.text(value, 100, y);
                y += 7;
            });
            
            // Футер
            doc.setFontSize(8);
            doc.setTextColor(128, 128, 128);
            doc.text('Расчет выполнен с помощью инвестиционного калькулятора Sianoro', 20, 280);
            doc.text('sianoro.com - недвижимость в Таиланде', 20, 287);
            
            // Сохранение файла
            doc.save(`investment_calculation_${new Date().toISOString().split('T')[0]}.pdf`);
            
        } catch (error) {
            console.error('Ошибка создания PDF:', error);
            // Fallback
            generateTextReport(calculation);
        }
    }
    
    // Fallback функция для генерации текстового отчета
    function generateTextReport(calculation) {
        const report = `
ИНВЕСТИЦИОННЫЙ КАЛЬКУЛЯТОР SIANORO
Дата расчета: ${new Date(calculation.timestamp).toLocaleDateString('ru-RU')}

ИСХОДНЫЕ ДАННЫЕ:
- Стоимость квартиры: ${formatNumber(calculation.inputs.price, calculation.inputs.currency)}
- Площадь: ${calculation.inputs.area} м²
- Депозит: ${formatNumber(calculation.inputs.deposit, calculation.inputs.currency)}
- Контрактный платеж: ${calculation.inputs.contractPercent}%
- Рассрочка: ${calculation.inputs.installmentPercent}%
- Оформление: ${calculation.inputs.registrationPercent}%
- Sinking Fund: ${formatNumber(calculation.inputs.sinking, calculation.inputs.currency)}
- Maintenance Fee: ${formatNumber(calculation.inputs.maintenance, calculation.inputs.currency)}
- Прогноз роста: ${calculation.inputs.growthPercent}% в год
- Срок: ${calculation.inputs.years} лет
- Доход от аренды: ${calculation.inputs.rentYieldPercent}% в год

РЕЗУЛЬТАТЫ:
- Итого вложено: ${formatNumber(calculation.results.totalInvested, calculation.inputs.currency)}
- Прогнозируемая цена: ${formatNumber(calculation.results.futurePrice, calculation.inputs.currency)}
- Прибыль: ${formatNumber(calculation.results.profit, calculation.inputs.currency)}
- Доход от аренды: ${formatNumber(calculation.results.rentIncome, calculation.inputs.currency)} в год
- ROI за год: ${calculation.results.roiYear.toFixed(1)}%
- ROI общий: ${calculation.results.roiTotal.toFixed(1)}%
- Цена за м²: ${formatNumber(calculation.results.pricePerM2, calculation.inputs.currency)}

Расчет выполнен с помощью инвестиционного калькулятора Sianoro
sianoro.com - недвижимость в Таиланде
        `;
        
        // Создаем и скачиваем файл
        const blob = new Blob([report], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `investment_calculation_${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    // Предустановленные сценарии
    const presets = {
        studio: {
            name: 'Студия',
            price: 1500000,
            area: 25,
            deposit: 100000,
            contract: 35,
            installment: 15,
            registration: 1.1,
            sinking: 50000,
            maintenance: 12000,
            growth: 12,
            years: 3,
            rentYield: 8
        },
        oneBR: {
            name: '1 спальня',
            price: 2500000,
            area: 40,
            deposit: 150000,
            contract: 35,
            installment: 15,
            registration: 1.1,
            sinking: 80000,
            maintenance: 20000,
            growth: 12,
            years: 3,
            rentYield: 7
        },
        twoBR: {
            name: '2 спальни',
            price: 4000000,
            area: 65,
            deposit: 200000,
            contract: 35,
            installment: 15,
            registration: 1.1,
            sinking: 120000,
            maintenance: 35000,
            growth: 12,
            years: 3,
            rentYield: 6
        }
    };
    
    // Применение предустановленного сценария
    function applyPreset(presetName) {
        const preset = presets[presetName];
        if (!preset) return;
        
        document.getElementById('price').value = preset.price;
        document.getElementById('area').value = preset.area;
        document.getElementById('deposit').value = preset.deposit;
        document.getElementById('contract').value = preset.contract;
        document.getElementById('installment').value = preset.installment;
        document.getElementById('registration').value = preset.registration;
        document.getElementById('sinking').value = preset.sinking;
        document.getElementById('maintenance').value = preset.maintenance;
        document.getElementById('growth').value = preset.growth;
        document.getElementById('years').value = preset.years;
        document.getElementById('rent_yield').value = preset.rentYield;
        
        // Автоматический расчет
        setTimeout(calculateInvestment, 100);
    }
    
    // Обработчики событий
    if (currencySelect) {
        currencySelect.addEventListener('change', updateCurrencyRate);
    }
    
    if (calculateBtn) {
        calculateBtn.addEventListener('click', calculateInvestment);
    }
    
    const downloadBtn = document.getElementById('download-pdf');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', generatePDF);
    }
    
    // Загрузка последнего расчета
    const lastCalculation = localStorage.getItem('lastCalculation');
    if (lastCalculation) {
        try {
            const data = JSON.parse(lastCalculation);
            console.log('Последний расчет загружен:', data);
        } catch (e) {
            console.warn('Не удалось загрузить последний расчет');
        }
    }
    
    // Инициализация
    loadExchangeRates();
    updateCurrencyRate();
    
    // Экспорт функций для глобального использования
    window.applyPreset = applyPreset;
});

// Функция для открытия калькулятора (вызывается из navbar)
function openInvestmentCalculator() {
    const modal = document.getElementById('investment-calculator-modal');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

// Функция для закрытия калькулятора
function closeInvestmentCalculator() {
    const modal = document.getElementById('investment-calculator-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
} 