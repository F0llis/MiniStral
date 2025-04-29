def display_len(s):
    """
    Renvoie le nombre de cellules vidéo réellement occupées par la chaîne s,
    en traitant chaque séquence d'accent (prefix 0x19 + 2 octets) comme UN seul caractère.
    """
    length = 0
    i = 0
    while i < len(s):
        if s[i] == '\x19':
            # séquence d'accent : prefix + code + lettre
            i += 3
            length += 1
        else:
            i += 1
            length += 1
    return length



def wrap_text(text, width):
    """
    Variante de wrap_text qui utilise display_len pour ne pas dépasser `width` cellules.
    Retourne une liste de lignes dont la largeur d'affichage ≤ width.
    """
    words = text.split(' ')
    lines = []
    line = ''
    for w in words:
        w_len = display_len(w)
        line_len = display_len(line)
        # mot seul plus long que la largeur → on le découpe
        if w_len > width:
            if line:
                lines.append(line)
                line = ''
            # découpage caractère à caractère
            part = ''
            for ch in w:
                # attention aux séquences d'accent
                add_len = 1
                if ch == '\x19':
                    # ajoutez aussi les deux octets suivants
                    seq = w[w.index(ch):w.index(ch)+3]
                    part += seq
                    continue
                if display_len(part + ch) > width:
                    lines.append(part)
                    part = ch
                else:
                    part += ch
            if part:
                lines.append(part)
        # sinon, on essaie d'ajouter le mot à la ligne courante
        elif (line and line_len + 1 + w_len <= width) or not line:
            line = (line + ' ' + w) if line else w
        else:
            # on bascule à la ligne suivante
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines