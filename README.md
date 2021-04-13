# Telegram_bot
После запуска бота и вызова команды /start, он должен выводить текстовое сообщение с описанием своих возможностей.

После запуска бот должен реагировать на три команды: /add и /list.

    При вызове команды /add в базовой реализации, бот предлагают пользователю ввести адрес. После ввода адреса, бот принимает строку, содержащую адрес и сохраняет её в базе данных или другим удобным способом.
    При вызове команды /add в расширенной реализации, бот пошагово опрашивает пользователя о названии места, его координатах, фотографии места. При желании список вопросов можно дополнить. Все эти данные бот сохраняет в базе данных или другим удобным способом. Обязательными полями для заполнения в таком случае будут являться название места и его координаты.
    При вызове команды /list, бот пишет сообщение с 10 последними добавленными местами.
    При вызове команды /reset, бот удаляет все сохранённые данные для данного пользователя.

Расширенная версия бота должна возвращать места в радиусе 500 метров при отправке локации, или возвращать сообщение об отсутствии добавленных мест.

https://t.me/Viktor_Podlevskiy_bot
