
import typing as t
def formatage(chaine: str, *args: t.Any, **kwargs: t.Any) -> str:
    """
    Formate une chaîne en remplaçant les jetons {i} par les éléments de `args`
    et les jetons {x} par les éléments de `kwargs`.

    Args:
        chaine (str): La chaîne contenant les jetons à remplacer.
        *args: Valeurs positionnelles à injecter.
        **kwargs: Valeurs nommées à injecter.

    Returns:
        str: La chaîne formatée.

    Exemple:
        format("Erreur {0} sur champ {champ}", 404, champ="nom")
        => "Erreur 404 sur champ nom"
    """
    import re

    def replacer(match):
        key = match.group(1)
        if key.isdigit():
            index = int(key)
            return str(args[index]) if index < len(args) else ''
        else:
            return str(kwargs.get(key, ''))

    return re.sub(r'{(\w+)}', replacer, chaine)