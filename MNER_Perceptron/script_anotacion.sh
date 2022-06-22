#!/bin/bash

for file in /Users/asdc/Desktop/MNER_Perceptron/corpus/*; do java -jar /Users/asdc/Desktop/MNER_Perceptron/perceptron.jar $file; done
mv /Users/asdc/Desktop/MNER_Perceptron/corpus/*.txt-tagged  /Users/asdc/Desktop/MNER_Perceptron/IxaMed_anotaciones
