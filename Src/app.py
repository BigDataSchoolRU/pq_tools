"""
Модуль для запуска приложения. 

Его можно и нужно изменять - проще изменить параметры (типа хоста и номера порта), чем заморачиваться и делать это настраиваемым (для такого небольшого и простого приложения).
"""

from bottle import run

from pq_tool import app

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True, reloader=True)
