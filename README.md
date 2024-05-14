# Структура
Здесь файлик с частью датасета который нужно разметить и приложение, чтобы референсные ответы было проще писать. 

# Инструкция:
Всё тестировалось на Ubuntu, не знаю запуститься ли на других ОС.

1. Все требования в requirements.txt. Чтобы их установить, в консоле нужно запустить ```pip install -r requirements.txt```

2. Чтобы запустить приложение используя файлик, в консоли нужно запустить ```python3 appQT5.py -f data_for_mark.json -of output.json```

Замечание: data_for_mark.json это файл, где хранятся данные с кодами студента, output.json это такой же файл, но с ответами.

Если вы за один подход не запишите все ответы, то просто выключите приложение и в следующйи раз используйте тот же output.json. Все данные от туда подтянутся.

Замечание: Данные в файлик output.json загружаются, только когда вы ответили на ВСЕ вопросы касательно одной задачи. То есть, если вы хотите, чтобы ваш ответ сохранился, ответьте на все вопросы по этой задаче (их всего 7).

3. При запуске приложения перед вами будет неправильное решение студента (слева) и правильное решение студента (справа). Так же будут подсвечены красным строки которые исчезли и зеленым те, которые появились, а желтым те, которые изменились.
Иногда подсветка барахлит, но я вам гаранитрую, что решение слева неверное, а справа верное.

Снизу вы увидете окно с местом для ввода хинта с некоторым шаблоном. Ваша цель: написать хинт по пунктам, что не так в левом коде и как это исправить, чтобы он стал рабочим.

В вашем хинте постарайтесь четко и кратко указать ошибку, которую допустил студент и как её можно исправить. Пишите как вам удобнее. Я пишу по пункту на каждую проблему в коде. В частности, можно обойтись одной подсказкой.

Замечание: ответ нужно писать на английском.

Например:

student_code:

```A,B=map(int,input().split())
if A>=13:
    print(B)
elif A>=6:
    print(B/2)
else:
    print(0)
```
### Hint:
    1. Look at the print answer if A is greater than or equal to 6. Your result will be a float instead of an int.

Вторым заданием будет ответить насколько хороший приведенный хинт. 
Для оценки пользуйтесь следующей эвристикой: 
Если вы считаете, что код никому не поможет как-то продвинуться вперед. Например, подсказки намекает на ошибку которой нет или не говорит ничего полезного. -- жмите 'Bad hint'.
Если вы видите зерно истины, но по каким-то причинам ответ вам не нравится, то нажмите 'So so'. Например, если одна подсказка ок, а другая нет.
И, наконец, если вас всё устраивает, нажимайте 'Good hint'. Замечу, что жмите 'Good hint' даже если обе подсказки об одном и том же, но хорошие.

4. Для вашего удобства добавлена кнопка back, чтобы можно было вернуться к прошлому ответу и что-то поменять. Так же можно использовать чтобы подсмотреть хинты из ответов.

5. На разметку всего своего куска я потратил 40 минут. Мне кажется в зависимости от трудности кода и вашей скорости это может занимать +- 10 минут от этого времени.

6. Если не разметите все -- скажите мне как только это поймете.

7. По всем вопросам/багам приложения пишите в телеграмм @ILPolozov
