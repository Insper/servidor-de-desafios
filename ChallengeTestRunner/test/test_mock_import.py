from challenge_test_lib import mock_import


def custom_func():
    return 'Worked!'


def test_from_import_works():
    mock_import.register_module('random_custom_new_module',
                                {'crazy_custom_func': custom_func})

    try:
        from random_custom_new_module import crazy_custom_func
        assert crazy_custom_func() == 'Worked!'
    finally:
        mock_import.deactivate_custom_imports()


def test_import_works():
    mock_import.register_module('random_custom_new_module',
                                {'crazy_custom_func': custom_func})

    try:
        import random_custom_new_module
        assert random_custom_new_module.crazy_custom_func() == 'Worked!'
    finally:
        mock_import.deactivate_custom_imports()
