#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работоспособности Python окружения
"""

import sys
import platform
import datetime
import json

def test_basic_functionality():
    """Проверка базовой функциональности"""
    print("🔍 Проверка базовой функциональности...")
    
    # Проверка версии Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"✓ Версия Python: {python_version}")
    
    # Проверка платформы
    system = platform.system()
    release = platform.release()
    print(f"✓ Платформа: {system} {release}")
    
    # Проверка работы с датами
    now = datetime.datetime.now()
    print(f"✓ Текущая дата и время: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверка работы со строками
    test_string = "Hello, World!"
    reversed_string = test_string[::-1]
    print(f"✓ Работа со строками: '{test_string}' -> '{reversed_string}'")
    
    # Проверка работы со списками
    test_list = [1, 2, 3, 4, 5]
    squared_list = [x**2 for x in test_list]
    print(f"✓ Работа со списками: {test_list} -> {squared_list}")
    
    # Проверка работы с JSON
    test_data = {"name": "Test", "value": 42, "active": True}
    json_string = json.dumps(test_data, ensure_ascii=False)
    parsed_data = json.loads(json_string)
    print(f"✓ Работа с JSON: {parsed_data}")
    
    # Проверка математики
    import math
    sqrt_result = math.sqrt(16)
    pi_value = math.pi
    print(f"✓ Математика: √16 = {sqrt_result}, π ≈ {pi_value:.4f}")
    
    print("\n✅ Все тесты пройдены успешно!")
    return True

def test_file_operations():
    """Проверка операций с файлами"""
    print("\n📁 Проверка операций с файлами...")
    
    test_filename = "/workspace/test_temp_file.txt"
    test_content = "Это тестовый контент для проверки записи файлов.\nСтрока 2\nСтрока 3"
    
    try:
        # Запись в файл
        with open(test_filename, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✓ Файл успешно записан")
        
        # Чтение из файла
        with open(test_filename, 'r', encoding='utf-8') as f:
            read_content = f.read()
        print("✓ Файл успешно прочитан")
        
        # Проверка содержимого
        if read_content == test_content:
            print("✓ Содержимое файла совпадает")
        else:
            print("✗ Содержимое файла не совпадает")
            return False
        
        # Удаление тестового файла
        import os
        os.remove(test_filename)
        print("✓ Тестовый файл удален")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка при работе с файлами: {e}")
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("🧪 ТЕСТОВЫЙ СКРИПТ ПРОВЕРКИ РАБОТОСПОСОБНОСТИ")
    print("=" * 60)
    
    success = True
    
    # Выполнение тестов
    if not test_basic_functionality():
        success = False
    
    if not test_file_operations():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНУ УСПЕШНО!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
