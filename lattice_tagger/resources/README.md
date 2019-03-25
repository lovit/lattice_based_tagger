# Word and morpheme dictionary directory

Each directory consists of multiple text (`.txt`) file and a rule file (`rules`).

And the file name of .txt means tag of morphemes. For examples, `Adjective.txt` file consists of adjective morphemes

```
--| base
    --| Adjective.txt
    --| Adverb.txt
    --| Determiner.txt
    --| Eomi.txt
    --| Exclamation.txt
    --| Josa.txt
    --| Noun.txt
    --| Number.txt
    --| Pronoun.txt
    --| README.md3 months ago
    --| rules
    --| Verb.txt
```

Lemmatization rules are written in `rules` file. Each line consists with three columns; conjugated substring, canonical form of stem, canonical form of ending which called eomi in Korean.

For examples, we can lemmatize
- `파랬고` to `파랗 + 았고` with `랬고 랗 았고` or
- `설렜다` to `설레 + 었다` with `렜다 레 었다`

```
...
랬고 랗 았고
랬고 러 었고
랬고 렇 었고
랬고 래 었고
...
렜다 레 었다
렜더 러 었더
렜던 러 었던
...
```


## Three dictionaries

- `base` is full-size morpheme dictionary
- `demo_morph` is sample morpheme dictionary for development
- `demo_word` is sample word dictionary for development