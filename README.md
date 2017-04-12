# Entrega Práctico 1
## Ejercicio 1

Se utiliza el corpus de la Summa Teológica.

Luego de cargar el corpus y correr el tokenizador se obtuvieron muchos errores
de tokenización de oraciones debido a la presencia de abreviaciones. A
continuación se muestran algunos ejemplos de las mismas:
```
    annunt
    avit
    bonifac
    carn
    catilin
    cit
    cledon
    cliv
    consecr
    dardan
    decent
    dioscor
    dom
```

Tres expresiones regulares fueron usadas para extraer las abreviaciones:

```
    # Abbrev that are followed by a number:
    '[a-zA-Z]+\.\s[1-9]'

    # Abbrev that are followed by a latin number:
    [a-zA-Z]+\.\s[ixv]+

    # Abbrev that are followed by a parentheses:
    [a-zA-Z]+\.\)
```

Como se puede notar hay tres tipos de abreviaciones:
- Que aparecen antes de un número
- Que aparecen antes de un número latino (notar que no se usó la regex que
  matchea números romanos de verdad pues se priorizó la legibilidad de la misma)
- Que aparecen antes de un paréntesis

### Paréntesis:
#### Cantidad encontrada: 77

```
    ['a', 'agapit', 'animal', 'annunt', 'avit', 'bonifac', 'carn','catilin',
    'cc', 'circum', 'circumcis', 'cit', 'cledon', 'cliv', 'consecr', 'dardan',
    'decent', 'dioscor', 'dom', 'e', 'ed', 'epict', 'epiph', 'etc', 'eustoch',
    'ev', 'evang', 'exod', 'ezech', 'fid', 'hebdom', 'helvid', 'hier', 'hispan',
    'i', 'ibid', 'ii', 'iii', 'joan', 'julian', 'luc', 'ludifred', 'machab',
    'marc', 'matt', 'matth', 'miss', 'monach', 'nat', 'nativ', 'obj',
    'objection', 'oper', 'optim', 'ordinand', 'orth', 'p', 'pet', 'poenit',
    'praedic', 'prolog', 'prosper', 'qq', 'rom', 'sanct', 'seleuc', 'seq',
    'seqq', 'spirit', 'sqq', 'temp', 'test', 'transfig', 'tusc', 'ult', 'vigil',
    'virg']
```

### Números:
#### Cantidad encontrada: 96

```
    ['a', 'aa', 'act', 'anath', 'ap', 'apoc', 'art', 'bar', 'can', 'cant',
    'cap', 'cf', 'ch', 'cod', 'col', 'comm', 'conc', 'cor', 'd', 'dan', 'deut',
    'dist', 'domin', 'eccl', 'eccles', 'ecclus', 'ep', 'eph', 'ethic', 'etym',
    'evang', 'ex', 'ezech', 'gal', 'gen', 'hab', 'haeres', 'heb', 'hom', 'i',
    'ii', 'isa', 'iv', 'jam', 'jer', 'jos', 'josh', 'lam', 'lev', 'luc', 'mac',
    'macc', 'mal', 'matt', 'matth', 'mic', 'mk', 'n', 'nom', 'num', 'obj',
    'olymp', 'orth', 'p', 'paral', 'paralip', 'pet', 'phil', 'phileb', 'philem',
    'phys', 'prov', 'ps', 'psalm', 'q', 'qq', 'qu', 'quadrag', 'relig', 'remin',
    'rhet', 'rom', 'scip', 'sent', 'serm', 'text', 'thess', 'tim', 'tit', 'tob',
    'tract', 'viii', 'wis', 'xii', 'xviii', 'zech']
```

### Números Romanos:
#### Cantidad encontrada: 190

```
    ['agg', 'anal', 'anim', 'animal', 'annunt', 'ant', 'antiq', 'antiquit',
    'apost', 'arb', 'arbit', 'archon', 'arian', 'art', 'attic', 'boni', 'c',
    'cai', 'can', 'cap', 'casulan', 'categor', 'caus', 'ch', 'chap', 'christ',
    'cleric', 'coel', 'coll', 'collat', 'comm', 'comment', 'concep', 'concup',
    'confess', 'conjug', 'consecr', 'consol', 'constant', 'de', 'decret', 'def',
    'diaboli', 'dial', 'discip', 'dist', 'dogm', 'dogmat', 'dom', 'donat',
    'donatist', 'e', 'eccl', 'enarr', 'ennar', 'ep', 'epiph', 'epist', 'erig',
    'ethic', 'etym', 'eudem', 'evang', 'expos', 'exposit', 'faust', 'felic',
    'felician', 'flav', 'flavian', 'g', 'galat', 'gall', 'gener', 'georg',
    'grat', 'gratian', 'haeres', 'helvid', 'herm', 'hier', 'histor', 'hom',
    'imp', 'imperf', 'incarn', 'incarnat', 'insomn', 'inv', 'invent', 'januar',
    'joan', 'jovin', 'julian', 'just', 'justin', 'justit', 'later', 'law',
    'leg', 'lib', 'lit', 'luc', 'm', 'manich', 'marc', 'matth', 'maxim',
    'memor', 'mendac', 'metaph', 'meteor', 'milit', 'miss', 'moral', 'myst',
    'myster', 'nativ', 'natur', 'nom', 'offic', 'officiis', 'oper', 'orat',
    'ord', 'orth', 'p', 'parad', 'paradox', 'paral', 'parmen', 'parth',
    'pastor', 'pelag', 'perplex', 'persev', 'petilian', 'phys', 'physic',
    'poenit', 'poet', 'polit', 'poster', 'praedest', 'praedic', 'praefat',
    'predic', 'problem', 'prop', 'prosp', 'ps', 'qq', 'qu', 'quaes', 'quaest',
    'regist', 'registr', 'relig', 'rem', 'remin', 'remiss', 'resp', 'retract',
    'rhet', 'rhetor', 'rom', 'rud', 'rudib', 'sacram', 'sanct', 'sent',
    'sentent', 'serm', 'simplician', 'solil', 'soliloq', 'sophon', 'symb',
    'synon', 'theol', 'tit', 'topic', 'tract', 'trin', 'tusc', 'tuscul', 'virg',
    'virgin', 'vit', 'viz']
```

La mejora puede notarse al comparar la versión sin las abreviaciones:


```
Now it has been stated above ( A .

1 ) that acts are called human , inasmuch as they proceed from a deliberate will
.

Now the object of the will is the good and the end .

And hence it is clear that the principle of human acts , in so far as they are
human , is the end .

In like manner it is their terminus : for the human act terminates at that which
the will intends as the end ; thus in natural agents the form of the thing
generated is conformed to the form of the generator .

And since , as Ambrose says ( Prolog .

super Luc .)

" morality is said properly of man ," moral acts properly speaking receive their
species from the end , for moral acts are the same as human acts .

Reply Obj .

1 : The end is not altogether extrinsic to the act , because it is related to
the act as principle or terminus ; and thus it just this that is essential to an
act , viz .

to proceed from something , considered as action , and to proceed towards
something , considered as passion .

Reply Obj .

2 : The end , in so far as it pre - exists in the intention , pertains to the
will , as stated above ( A .

1 , ad 1 ).

And it is thus that it gives the species to the human or moral act .

Reply Obj .

3 : One and the same act , in so far as it proceeds once from the agent , is
ordained to but one proximate end , from which it has its species : but it can
be ordained to several remote ends , of which one is the end of the other .
```

con la versión que sí las tiene:

```
Now it has been stated above ( A . 1 ) that acts are called human , inasmuch as
they proceed from a deliberate will .

Now the object of the will is the good and the end .

And hence it is clear that the principle of human acts , in so far as they are
human , is the end .

In like manner it is their terminus : for the human act terminates at that which
the will intends as the end ; thus in natural agents the form of the thing
generated is conformed to the form of the generator .

And since , as Ambrose says ( Prolog . super Luc .) " morality is said properly
of man ," moral acts properly speaking receive their species from the end , for
moral acts are the same as human acts .

Reply Obj . 1 : The end is not altogether extrinsic to the act , because it is
related to the act as principle or terminus ; and thus it just this that is
essential to an act , viz . to proceed from something , considered as action ,
and to proceed towards something , considered as passion .

Reply Obj . 2 : The end , in so far as it pre - exists in the intention ,
pertains to the will , as stated above ( A . 1 , ad 1 ).

And it is thus that it gives the species to the human or moral act .

Reply Obj . 3 : One and the same act , in so far as it proceeds once from the
agent , is ordained to but one proximate end , from which it has its species :
but it can be ordained to several remote ends , of which one is the end of the
other .
```

Se implementó una clase SummatCorpusReader que hereda de PlaintextCorpusReader.
Esta clase utiliza las abreviaciones extraídas del corpus para generar un
tokenizador de oraciones Punkt (PunktSentenceTokenizer). La ventaja de usar
PunktSentenceTokenizer es que permite proveerle un conjunto de abreviaciones
que luego utiliza para tokenizar las oraciones.



