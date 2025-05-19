import flet as ft
from gui import root
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

if __name__ == "__main__":
    ft.app(target=root)
