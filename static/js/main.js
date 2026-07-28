// ФУНКЦИЯ ДЛЯ СТРАНИЦЫ ТОВАРА
function initItemPage(stripePublishableKey, itemId) {
    /**
     * Инициализация страницы товара
     * @param {string} stripePublishableKey - Публичный ключ Stripe
     * @param {number} itemId - ID товара
     */

    // Проверяем, что Stripe загружен
    if (typeof Stripe === 'undefined') {
        console.error('Stripe library not loaded');
        return;
    }

    // Инициализируем Stripe
    var stripe = Stripe(stripePublishableKey);

    // Получаем элементы
    var buyButton = document.getElementById('buy-button');
    var loading = document.getElementById('loading');

    // Если кнопки нет - выходим
    if (!buyButton) {
        console.error('Buy button not found');
        return;
    }

    // Обработчик нажатия кнопки
    buyButton.addEventListener('click', function() {
        // Блокируем кнопку и показываем загрузку
        buyButton.disabled = true;
        buyButton.textContent = 'Processing...';
        if (loading) {
            loading.classList.add('active');
        }

        // Запрашиваем session_id у сервера
        fetch('/buy/' + itemId + '/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(function(response) {
            // Проверяем успешность ответа
            if (!response.ok) {
                throw new Error('Failed to create checkout session');
            }
            return response.json();
        })
        .then(function(data) {
            // Проверяем ошибку
            if (data.error) {
                throw new Error(data.error);
            }
            // Перенаправляем на Stripe Checkout
            return stripe.redirectToCheckout({ sessionId: data.id });
        })
        .then(function(result) {
            if (result && result.error) {
                throw new Error(result.error.message);
            }
        })
        .catch(function(error) {
            // 4. Обрабатываем ошибку
            console.error('Error:', error);
            alert('Payment error: ' + error.message);

            // Возвращаем кнопку в исходное состояние
            buyButton.disabled = false;
            buyButton.textContent = 'Buy Now';
            if (loading) {
                loading.classList.remove('active');
            }
        });
    });
}

// АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ

// При загрузке страницы проверяем, есть ли элемент с данными
document.addEventListener('DOMContentLoaded', function() {
    // Ищем скрытый элемент с данными для инициализации
    var initData = document.getElementById('init-data');

    if (initData) {
        try {
            var data = JSON.parse(initData.textContent);

            // Инициализируем страницу товара
            if (data.type === 'item') {
                initItemPage(data.publishableKey, data.itemId);
            }
        } catch (error) {
            console.error('Failed to parse init data:', error);
        }
    }
});