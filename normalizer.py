import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from prioriti.normalizer import classificar_senioridade_precisa, normalizar_banco_dados, remover_acentos

if __name__ == "__main__":
    normalizar_banco_dados()
