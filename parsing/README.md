# Entrega Práctico 3
# Ejercicio 1

Se programó un script para evaluar los parsers como se pide en la consigna. A
continuación se muestran los resultados.

## Resultados
| Model      | Training Time | Evaluation Time |
|------------|---------------|-----------------|
| flat       | 0m0.681s      | 0m5.471s        |
| rbranch    | 0m0.645s      | 0m6.081s        |
| lbranch    | 0m0.645s      | 0m5.992s        |
| upcfg      | 1m0.969s      | 1m38.222s       |
| upcfg -n 1 | 0m54.760s     | 1m0.169s        |
| upcfg -n 2 | 0m55.370s     | 1m19.996s       |
| upcfg -n 3 | 0m56.964s     | 1m28.433s       |
| upcfg -n 4 | 0m59.084s     | 1m35.200s       |

| Model      | Precision (L) | Recall (L) |     F1 (L) | Precision (U) | Recall (U) |     F1 (U) |
|------------|---------------|------------|------------|---------------|------------|------------|
| flat       |        99.93% |     14.57% |     25.43% |       100.00% |     14.58% |     25.45% |
| rbranch    |         8.81% |     14.57% |     10.98% |         8.87% |     14.68% |     11.06% |
| lbranch    |         8.81% |     14.57% |     10.98% |        14.71% |     24.33% |     18.33% |
| upcfg      |        73.32% |     73.02% |     73.17% |        75.43% |     75.12% |     75.28% |
| upcfg -n 1 |        74.66% |     74.57% | **74.61%** |        76.53% |     76.43% | **76.48%** |
| upcfg -n 2 |        74.88% |     74.36% | **74.62%** |        76.80% |     76.27% | **76.53%** |
| upcfg -n 3 |        74.09% |     73.46% |     73.77% |        76.24% |     75.59% |     75.91% |
| upcfg -n 4 |        73.61% |     73.18% |     73.39% |        75.75% |     75.31% |     75.53% |

## Sobre flat, lbranch y rbranch

El modelo flat sólo asigna las etiquetas a cada uno de los tokens como
constituyentes; es un árbol plano de dos niveles. Por ejemplo el árbol
resultante de parsear de "Y nos quemamos ." es:

```
(S (cc Y ) (pp1 nos) (vmi quemamos) (fp .))
```

Mientras que el parsing correcto es (según el Treebank de Ancora):

```
(sentence
  (conj (cc Y))
  (sn (grup.nom (pp1 nos)))
  (grup.verb (vmi quemamos))
  (fp .))
```

Claramente, el parsing del modelo flat es muy malo.

A pesar de ello la precisión es muy alta. Esto ocurre porque es poco probable
que este modelo asigne mal una etiqueta (pre-terminal).

El mal desempeño del modelo se puede ver al notar que la exhaustividad (recall)
es baja. Esto simplemente ocurre porque faltan nodos en el árbol.

Por el mismo motivo, rbranch y lbranch tienen una baja exhaustividad. Por otra
parte, a diferencia de flat, rbranch y lbranch tienen una baja precisión. Esto
ocurre porque aparecen constituyentes que nunca van a coincidir con los
correctos. Cabe aclarar que estos constituyentes aparecen para lograr la
binarización de las reglas de producción.

Por ejemplo con el modelo LBranch se obtiene el siguiente parsing:
```
(sentence
  (sentence|<> (sentence|<> (cc Y) (pp1 nos)) (vmi quemamos))
  (fp .))
```

Y para RBranch se obtiene:
```
(sentence
  (cc Y)
  (sentence|<> (pp1 nos) (sentence|<> (vmi quemamos) (fp .))))
```

## Sobre upcfg
Como era de esperar el mejor modelo era aquel con una markovización horizontal
de segundo orden seguido del modelo con una markovización horizontal de primer
orden. Se puede observar cómo decaen los valores de F1 a medida que el n crece
luego de n = 2.

# Ejercicio 2: Algoritmo CKY

<!-- TODO:  -->
<!-- Agregar a los tests un test con una gramática y una oración  -->
<!-- tal que la oración tenga más de un análisis posible -->


Se implementó el algoritmo siguiendo el video de 
  [Dan Jurafsky & Chris Manning](https://www.youtube.com/watch?v=hq80J8kBg-Y).

## Sobre binary_rules

Debido a que había una cantidad considerable de loops anidados, por legibilidad
se creo un método adicional `binary_rules` que toma dos conjuntos Bs y Cs de
símbolos (pueden ser no terminales o terminales) y devuelve una lista de todas
las 4-uplas de la forma `(A, B, C, prob)` donde `A -> B C` es una regla de
producción perteneciente a la gramática con probabilidad condicional `prob`.

Este método es requerido cuando se quiere recorrer todas las posibles reglas de
producción binarias que tengan del lado derecho de la regla:
- primero un símbolo del span izquierdo (`B`)
- segundo un símbolo del span derecho (`C`)

La llamada a este método es el cuello de botella del algoritmo. Se evaluaron dos
posibles implementaciones:

### Primera implementación

```
binary_rules = []
for B, C in binary_rhs:
    if B in Bs and C in Cs:
        binary_rules += [(A, B, C, prob)
                          for A, prob in self.from_rhs[(B, C)]]
return binary_rules
```

binary_rhs es un conjunto que guarda todos los rhs (right hand sides) que tienen
dos elementos. Este conjunto se calcula en el constructor de la clase.


### Segunda implementación

```
binary_rules = []
for B, C in product(Bs, Cs):
    if (B, C) in from_rhs:
        binary_rules += [(A, B, C, prob) for A, prob in from_rhs[(B, C)]]
return binary_rules
```

### Evaluación de ambas implementaciones

Se ejecutaron ambas versiones. La primera era muy lenta y se descartó.
Claramente el producto cartesiano entre todas los posibles símbolos para el span
derecho tiene un tamaño mucho menor (en promedio) que el conjunto de las
producciones.



# Ejercicio 3: PCFGs No Lexicalizadas
Se implementó una UPCFG como se indica en la consigna. La implementación depende
fuertemente de la librería nltk. Esta librería provee funciones como:

- `Tree.chomsky_normal_form`: Convierte el árbol en su equivalente de Forma
                              Normal de Chomsky
- `Tree.collapse_unary`: Colapsa subárboles con un único hijo en un nuevo nodo
                         (no-terminal).
- `Tree.productions`: Devuelve todas las reglas de producción de la gramática
                      que le corresponde a los nodos no terminales del árbol.
- `Tree.un_chomsky_normal_form`: Revertir el proceso de `chomsky_normal_form`

- `induce_pcfg`: Induce una pcfg utilizando una lista de producciones.

Los resultados se reportan en el ejercicio 1.

# Ejercicio 4: Markovización Horizontal

Esto ejercicio simplemente implicó cambiar un argumento de
`Tree.chomsky_normal_form` y agregar un modelo más en el script de
entrenamiento. Los resultados se reportan en el ejercicio 1.
