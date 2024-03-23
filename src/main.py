if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication

    from assethandling.asset_manager import splash_gif
    from ui.ui_splash_screen import SplashScreen

    print(1)
    app = QApplication(sys.argv)
    splash = SplashScreen(splash_gif)
    splash.show()
    print(2)
    from gui_main import main

    print(3)
    main(app)
    print(4)
