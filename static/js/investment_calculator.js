// Инвестиционный калькулятор Sianoro

document.addEventListener('DOMContentLoaded', function() {
    // Курсы валют (можно заменить на API)
    const exchangeRates = {
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
            
            // Доход от аренды в год
            const rentIncome = futurePrice * (rentYieldPercent / 100);
            
            // ROI за год (на основе арендного дохода)
            const roiYear = (rentIncome / totalInvested) * 100;
            
            // ROI к окончанию строительства
            const roiTotal = (profit / totalInvested) * 100;
            
            // Цена за м²
            const pricePerM2 = priceInTHB / area;
            
            // Конвертируем результаты в выбранную валюту
            const convertedResults = {
                totalInvested: convertFromTHB(totalInvested, currency),
                futurePrice: convertFromTHB(futurePrice, currency),
                profit: convertFromTHB(profit, currency),
                rentIncome: convertFromTHB(rentIncome, currency),
                pricePerM2: convertFromTHB(pricePerM2, currency)
            };
            
            // Отображаем результаты
            document.getElementById('result-invested').textContent = formatNumber(convertedResults.totalInvested, currency);
            document.getElementById('result-future-price').textContent = formatNumber(convertedResults.futurePrice, currency);
            document.getElementById('result-profit').textContent = formatNumber(convertedResults.profit, currency);
            document.getElementById('result-rent').textContent = formatNumber(convertedResults.rentIncome, currency);
            document.getElementById('result-roi-year').textContent = roiYear.toFixed(1) + '%';
            document.getElementById('result-roi-total').textContent = roiTotal.toFixed(1) + '%';
            document.getElementById('result-price-m2').textContent = formatNumber(convertedResults.pricePerM2, currency);
            document.getElementById('result-years').textContent = years;
            
            // Показываем результаты
            resultsDiv.classList.remove('hidden');
            
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
    
    // Генерация PDF отчета
    function generatePDF() {
        const calculation = JSON.parse(localStorage.getItem('lastCalculation'));
        if (!calculation) {
            alert('Сначала выполните расчет');
            return;
        }
        
        // Простой текстовый отчет (в реальном проекте можно использовать jsPDF)
        const report = `
ИНВЕСТИЦИОННЫЙ КАЛЬКУЛЯТОР SIANORO
Дата расчета: ${new Date(calculation.timestamp).toLocaleDateString()}

ИСХОДНЫЕ ДАННЫЕ:
- Стоимость квартиры: ${formatNumber(calculation.inputs.price, calculation.inputs.currency)}
- Площадь: ${calculation.inputs.area} м²
- Депозит: ${formatNumber(calculation.inputs.deposit, calculation.inputs.currency)}
- Контрактный платеж: ${calculation.inputs.contractPercent}%
- Рассрочка: ${calculation.inputs.installmentPercent}%
- Оформление: ${calculation.inputs.registrationPercent}%
- Прогноз роста: ${calculation.inputs.growthPercent}% в год
- Срок: ${calculation.inputs.years} лет
- Доход от аренды: ${calculation.inputs.rentYieldPercent}% в год

РЕЗУЛЬТАТЫ:
- Итого вложено: ${formatNumber(calculation.results.totalInvested, calculation.inputs.currency)}
- Прогнозируемая цена: ${formatNumber(calculation.results.futurePrice, calculation.inputs.currency)}
- Прибыль: ${formatNumber(calculation.results.profit, calculation.inputs.currency)}
- Доход от аренды: ${formatNumber(calculation.results.rentIncome, calculation.inputs.currency)} в год
- Цена за м²: ${formatNumber(calculation.results.pricePerM2, calculation.inputs.currency)}
        `;
        
        // Создаем и скачиваем файл
        const blob = new Blob([report], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `investment_calculation_${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    // Обработчики событий
    if (currencySelect) {
        currencySelect.addEventListener('change', updateCurrencyRate);
        updateCurrencyRate(); // Инициализация
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
            // Можно восстановить последние введенные данные
            console.log('Последний расчет загружен:', data);
        } catch (e) {
            console.warn('Не удалось загрузить последний расчет');
        }
    }
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