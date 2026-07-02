"""
Interactive, guided setup for the Twilio .env values.
Run with: python setup_twilio.py
Each answer is validated on the spot so a mismatched value gets caught
immediately instead of failing later with a confusing 401 error.
"""

from pathlib import Path

ENV_PATH = Path(__file__).parent / ".env"


def ask(label, prefix=None, expected_len=None, hint=""):
    while True:
        value = input(f"{label}{' - ' + hint if hint else ''}: ").strip()
        if not value:
            print("  (no puede estar vacío, intenta de nuevo)")
            continue
        if prefix and not value.startswith(prefix):
            print(f"  Ese valor no empieza con '{prefix}' — parece que no es el correcto. Revisa e intenta de nuevo.")
            continue
        if expected_len and len(value) != expected_len:
            print(f"  Ese valor tiene {len(value)} caracteres, se esperaban {expected_len}. Revisa e intenta de nuevo.")
            continue
        return value


def main():
    print("=== Setup de Twilio para International ISA ===\n")

    account_sid = ask(
        "1) Account SID (Dashboard principal, sección 'Account Info')",
        prefix="AC", expected_len=34,
    )
    api_key_sid = ask(
        "2) API Key SID (página de API Keys, columna 'SID' de tu key)",
        prefix="SK", expected_len=34,
    )
    api_key_secret = ask(
        "3) API Key Secret (se mostró junto al SID cuando creaste la key)",
    )
    if api_key_secret == api_key_sid:
        print("\n  El Secret es igual al SID -- eso está mal, son dos valores distintos. Corrige el paso 3.\n")
        api_key_secret = ask("3) API Key Secret (otra vez)")

    from_number = ask(
        "4) Número de Twilio (Phone Numbers > Manage > Active Numbers)",
        prefix="+", hint="formato +1XXXXXXXXXX",
    )
    notify_number = ask(
        "5) Tu número personal, donde quieres recibir los avisos",
        prefix="+", hint="formato +1XXXXXXXXXX",
    )

    ENV_PATH.write_text(
        f"TWILIO_ACCOUNT_SID={account_sid}\n"
        f"TWILIO_API_KEY_SID={api_key_sid}\n"
        f"TWILIO_API_KEY_SECRET={api_key_secret}\n"
        f"TWILIO_FROM_NUMBER={from_number}\n"
        f"TWILIO_NOTIFY_NUMBER={notify_number}\n"
    )
    print(f"\nListo. Guardado en {ENV_PATH}")


if __name__ == "__main__":
    main()
