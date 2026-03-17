from Flask import allowed_file

def test_allowed_file_extension():
    # Навмисно робимо помилку, щоб зламати CI
    # Очікуємо True, але функція поверне False
    assert allowed_file("document.pdf") == True