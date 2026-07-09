import traceback

try:
    import main
    main.MainWindow()
except Exception as e:
    print("Error occurred:")
    print(traceback.format_exc())
    input("Press Enter to exit...")