import easygui

test = easygui.enterbox(msg='Enter something.', title='Hello!', default='', strip=True)
print test