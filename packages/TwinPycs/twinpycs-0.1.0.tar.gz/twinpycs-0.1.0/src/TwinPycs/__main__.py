from TwinPycs.A.main import show_message_box

def mymain():
    print(f"__main__.py has been called & function mymain():\n{sys.argv}.") 
    show_message_box()


if __name__ == "__main__":
    print('__main__.py has been called.') 
    show_message_box()