# Core independente de linguagem

[← Índice](../doc.md)

Decisão arquitetural importante: o core **não** deve espalhar lógica do tipo `if language == "python": run_pytest()` em dezenas de lugares.

Em vez disso, abstração de projeto:

```text
ProjectAdapter
    ├── detect()
    ├── test()
    ├── build()
    ├── lint()
    └── run()

Implementações: PythonAdapter | NodeAdapter | GoAdapter | GenericAdapter
```

Manter isso **simples** na primeira versão.
