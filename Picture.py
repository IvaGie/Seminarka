import re
import itertools
from collections import defaultdict


def parse_affix_file(affix_file):
    """Načte pravidla afixů z cs_affix.dat"""
    prefix_rules = []
    suffix_rules = []

    with open(affix_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

        for line in lines[2:]:  # První dva řádky jsou komentáře, ty přeskočíme
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if parts[0] == 'PFX':
                # Předpona
                prefix_rules.append(parts)
            elif parts[0] == 'SFX':
                # Přípona
                suffix_rules.append(parts)

    return prefix_rules, suffix_rules


def parse_base_words(cat_file):
    """Načte základní slova a jejich pravidla z .cat souboru"""
    base_words = []

    with open(cat_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            word_and_affix = line.split('/')
            base_word = word_and_affix[0]
            affix = word_and_affix[1] if len(word_and_affix) > 1 else ''
            base_words.append((base_word, affix))

    return base_words


def apply_affixes(base_word, affix, prefix_rules, suffix_rules):
    """Aplikuje pravidla afixů na základní slovo"""
    word_variants = set()

    # Aplikujeme prefixy
    for prefix_rule in prefix_rules:
        prefix, _, _, _ = prefix_rule
        new_word = prefix + base_word
        word_variants.add(new_word)

    # Aplikujeme přípony
    for suffix_rule in suffix_rules:
        suffix, _, _, _ = suffix_rule
        new_word = base_word + suffix
        word_variants.add(new_word)

    return word_variants


def expand_variants(word_with_variants):
    """Expanze variant ve složených závorkách {}"""
    if '{' not in word_with_variants:
        return {word_with_variants}

    variants = re.findall(r'\{([^\}]+)\}', word_with_variants)
    if variants:
        # Rozšíříme varianty v závorkách do všech možných kombinací
        expanded_variants = []
        for v in variants[0].split(','):
            expanded_variants.append(word_with_variants.replace(f'{{{variants[0]}}}', v))

        return set(expanded_variants)

    return {word_with_variants}


def generate_words(cat_file, affix_file, output_file):
    # Načteme pravidla afixů
    prefix_rules, suffix_rules = parse_affix_file(affix_file)

    # Načteme základní slova
    base_words = parse_base_words(cat_file)

    # Sada pro uchování všech unikátních generovaných slov
    all_generated_words = set()

    for base_word, affix in base_words:
        # Aplikace afixů na základní slovo
        generated_words = apply_affixes(base_word, affix, prefix_rules, suffix_rules)

        # Expanzí varianty v závorkách {}
        for word in generated_words:
            expanded_words = expand_variants(word)
            all_generated_words.update(expanded_words)

    # Uložení všech vygenerovaných slov do výstupního souboru
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted(all_generated_words):
            f.write(word + '\n')

    print(f"Generated {len(all_generated_words)} unique words.")


# Příklad použití
cat_file = 'cat/hovor.cat'  # Soubor se základními slovy
affix_file = 'cs_affix.dat'  # Soubor s pravidly afixů
output_file = 'out/generated_words.txt'  # Výstupní soubor

generate_words(cat_file, affix_file, output_file)
