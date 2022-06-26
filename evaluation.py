from operator import index
from pickle import FALSE
from pickletools import read_string1
from pydoc import doc
import re
import string
from sys import displayhook
from tokenize import String
from unittest import TestCase
from xml.etree.ElementTree import tostringlist
from numpy import row_stack, true_divide
import pandas as pd
from spacy.lang.es import Spanish
import os
import csv
import matplotlib.pyplot as plt
import statistics
import numpy as np

from zmq import EVENT_HANDSHAKE_FAILED_AUTH

PATH_IXAMED = '/Users/asdc/Desktop/MNER_Perceptron/IxaMed_anotaciones/'

#--------------------------------------------------------------------------------------------------------------------------------------------#
# 
#                                                           HEIDELTIME
#
#--------------------------------------------------------------------------------------------------------------------------------------------#

#------insert_file_id()-----#
"""
Los csv con las expresiones temporales no tenían id asociado al xml, así que para poder comparar expresiones entre ficheros se ha asociado un id igual en ambos csv (E3C y Heidel)
"""
def insert_file_id(file_org, file_dest):
    df = pd.read_csv(file_org)

    array_unique = df.file.unique()
    array_all = df.file
    array_insert = []
    i = 0
    j = 0
    while i < len(array_unique) and j < len(array_all):
        if array_all[j] == array_unique[i]:
            array_insert.append(i)
        else:
            i+=1
            array_insert.append(i)
        j+=1

    df.insert(loc=0, column='id_file', value=array_insert)
    df.to_csv(file_dest)

"""
Elimina expresiones con la clase PREPOSTEXP y QUANTIFIER del corpus ya que no se contemplan en TimeML 1.2.1, solo se contemplan en THYME
"""
def quitar_thyme(file_org, file_dest):
    df = pd.read_csv(file_org)
    print(df.size)
    df = df[df.timex3Class != 'PREPOSTEXP']
    df = df[df.timex3Class != 'QUANTIFIER']
    print(df.size)
    df.to_csv(file_dest)


    False
"""
-La idea es sacar los unique files del heidel y de ahí que devuelva las filas que tengan ese fichero del heidel y del E3C. Como en el heidel hay más documentos anotados (porque en habrá anotado expresiones
en documentos que no debería haber anotado) hay varias opciones:
    -(pre-procesar) Buscar los documentos que están sobre anotados y contar como fp todas las anotaciones
    -(in-live) Que cuando se encuentre uno de estos documentos se sumen las anotaciones como fp
Creo que in-live es mejor porque de la otra forma habría que omitirlos luego y al final haces la comparación igual.

-Con las coincidencias ya se sacan los tp, fp y fn y se calculan las métricas. Se puede poner en 3 métodos distintos, uno para sacar los coincidentes, otro los tp y tal y otro las métricas. 
El de las métricas seguro que va separado, lo otro ya no sé.
"""
def evaluacion_heidel(file_heidel, file_e3c):
    
    df_heidel = pd.read_csv(file_heidel)
    df_e3c = pd.read_csv(file_e3c)
    df_e3c_final = pd.read_csv(file_e3c)
    df_heidel_final = pd.read_csv(file_heidel)
    df_e3c_attr = pd.read_csv(file_e3c)
    df_heidel_attr = pd.read_csv(file_heidel)
    lista_inicial_mal = []
    lista_inicial_bien = []
    lista_final_mal = []
    lista_final_bien = []
    lista_completa_bien = []
    lista_completa_mal = []
    list_unique = df_heidel.file.unique()
    tp_extent_relaxed_final = 0
    tp_extent_relaxed_principio = 0
    tp_extent_relaxed_contenido=0
    tp_extent_strict = 0
    tp_attr_relaxed_final = 0
    tp_attr_relaxed_principio = 0
    tp_attr_relaxed_contenido=0
    tp_attr_strict = 0
    fp_attr_completo = 0
    fp_attr_final = 0    
    fp_attr_principio = 0
    fp_attr_contenido = 0

    for document in list_unique:
        heidel_doc = df_heidel[df_heidel['file'] == document]
        e3c_doc = df_e3c[df_e3c['file'] == document]
        indexes = list(df_e3c[df_e3c['file'] == document].index.values)
        #POR CADA HEIDEL SE COMPARA CON CADA LÍNEA DEL CORPUS EN BUSCA DE COINCIDENCIAS
        for _, time_exp in heidel_doc.iterrows():
            for index, e3c_rows in e3c_doc.iterrows():
                #COINCIDENCIA TOTAL
                if e3c_doc.loc[index].begin == time_exp['begin'] and e3c_doc.loc[index].end == time_exp['end']:
                    tp_extent_strict+=1
                    df_e3c_final.drop(index = index, inplace=True) #SE BORRAN LAS EXPRESIONES ENCONTRADAS PARA PODER CALCULAR FÁCILMENTE LOS FP Y FN
                    df_heidel_final.drop(index = _, inplace=True)
                    #SI COINCIDEN LOS ATRIBUTOS SE SUMA EL ACIERTO DE ATRIBUTO ESTRÍCTO (A PARTE DEL ACIERTO EN LA EXTENSIÓN)
                    if(e3c_doc.loc[index].timex3Class == time_exp['timex3Class'] and e3c_doc.loc[index].value == time_exp['value']):
                        tp_attr_strict+=1
                       #_temp_ se utiliza para sacar qué expresiones son las que se anotan mal por parte de Heidel
                        _temp_ = []
                        _temp_.append(time_exp['file'])
                        _temp_.append('BIEN')
                        _temp_.append(time_exp['string'])
                        _temp_.append(time_exp['timex3Class'])
                        _temp_.append(e3c_doc.loc[index].string)
                        _temp_.append(e3c_doc.loc[index].timex3Class)
                        lista_completa_bien.append(_temp_)
                        #print(index)
                        #print(df_e3c_attr['string'].iloc[120])
                        df_e3c_attr.drop(index = index, inplace=True) 
                        df_heidel_attr.drop(index = _, inplace=True)
                    else:
                        _temp_ = []
                        _temp_.append(time_exp['file'])
                        _temp_.append('MAL')
                        _temp_.append(time_exp['string'])
                        _temp_.append(time_exp['timex3Class'])
                        _temp_.append(e3c_doc.loc[index].string)
                        _temp_.append(e3c_doc.loc[index].timex3Class)
                        lista_completa_mal.append(_temp_)
                        fp_attr_completo+=1
                    break #BREAK PORQUE YA SE HA ENCONTRADO LA COINCIDENCIA Y NO HAY QUE BUSCAR MÁS
                #COINCIDENCIA PARCIAL EN EL PRINCIPIO DE LA EXPRESION
                elif e3c_doc.loc[index].begin == time_exp['begin']:
                    #SOLO SE CUENTA EL ACIERTO EN EXTENSIÓN SI SE ACIERTAN LOS ATRIBUTOS. LOS FALLOS EN LOS ATRIBUTOS EN ESTE CASO NO SE CUENTAN PARA CALCULAR FP, SOLO POR TENER LOS DATOS
                    if(e3c_doc.loc[index].timex3Class == time_exp['timex3Class'] and e3c_doc.loc[index].value == time_exp['value']):
                        tp_extent_relaxed_principio+=1
                        tp_attr_relaxed_principio+=1
                        df_e3c_final.drop(index = index, inplace=True)
                        df_heidel_final.drop(index = _, inplace=True)
                        df_e3c_attr.drop(index = index, inplace=True) 
                        df_heidel_attr.drop(index = _, inplace=True)
                        #temp_ se utiliza para sacar qué expresiones se anotan mal cuando se anota la extensión parcial
                        temp_ = []
                        temp_.append(time_exp['file'])
                        temp_.append('I')
                        temp_.append('B')
                        temp_.append(time_exp['string'])
                        temp_.append(time_exp['timex3Class'])
                        temp_.append(e3c_doc.loc[index].string)
                        temp_.append(e3c_doc.loc[index].timex3Class)
                        lista_inicial_bien.append(temp_)

                    else: 
                        temp_ = []
                        temp_.append(time_exp['file'])
                        temp_.append('I')
                        temp_.append('M')
                        temp_.append(time_exp['string'])
                        temp_.append(time_exp['timex3Class'])
                        temp_.append(e3c_doc.loc[index].string)
                        temp_.append(e3c_doc.loc[index].timex3Class)
                        lista_inicial_mal.append(temp_)
                        fp_attr_principio+=1
                    break
                #COINCIDENCIA PARCIAL EN EL FINAL DE LA EXPRESION
                elif e3c_doc.loc[index].end == time_exp['end']:
                    if(e3c_doc.loc[index].timex3Class == time_exp['timex3Class'] and e3c_doc.loc[index].value == time_exp['value']):
                        tp_extent_relaxed_final+=1
                        tp_attr_relaxed_final+=1
                        df_e3c_final.drop(index = index, inplace=True)
                        df_heidel_final.drop(index = _, inplace=True)
                        df_e3c_attr.drop(index = index, inplace=True) 
                        df_heidel_attr.drop(index = _, inplace=True)
                        temp_ = []
                        temp_.append(time_exp['file'])
                        temp_.append('F')
                        temp_.append('B')
                        temp_.append(time_exp['string'])
                        temp_.append(time_exp['timex3Class'])
                        temp_.append(e3c_doc.loc[index].string)
                        temp_.append(e3c_doc.loc[index].timex3Class)
                        lista_final_bien.append(temp_)

                    else: 
                        fp_attr_final+=1
                        temp_ = []
                        temp_.append(time_exp['file'])
                        temp_.append('F')
                        temp_.append('M')
                        temp_.append(time_exp['string'])
                        temp_.append(time_exp['timex3Class'])
                        temp_.append(e3c_doc.loc[index].string)
                        temp_.append(e3c_doc.loc[index].timex3Class)
                        lista_final_mal.append(temp_)
                    break
    
    """
    #Esto es para sacar qué clase de expresiones anota mal el heidel cuando coge la extensión parcial
    lista_final = []
    lista_final.append(lista_inicial_bien)
    lista_final.append(lista_inicial_mal)
    lista_final.append(lista_final_bien)
    lista_final.append(lista_final_mal)
    
    create_csv('bien_mal_parcial.csv', ['file','I/F', 'B/M', 'heidel', 'heidel_type', 'corpus', 'corpus_type'])
    with open ('bien_mal_parcial.csv', 'w') as f:
        write = csv.writer(f)
        write.writerow(["file",'I/F', 'B/M', 'heidel', 'heidel_type', 'corpus', 'corpus_type'])
        write.writerows(lista_inicial_bien)
        write.writerows(lista_inicial_mal)
        write.writerows(lista_final_bien)
        write.writerows(lista_final_mal)
    
    create_csv('bien_mal_completo.csv', ['file', 'B/M', 'heidel', 'heidel_type', 'corpus', 'corpus_type'])
    with open ('bien_mal_completo.csv', 'w') as f:
        write = csv.writer(f)
        write.writerow(['file', 'B/M', 'heidel', 'heidel_type', 'corpus', 'corpus_type'])
        write.writerows(lista_completa_bien)
        write.writerows(lista_completa_mal)
    """
    """
    #Esto es para sacar qué clase de expresiones anota mal el heidel cuando coge la extensión completa
    df_attr_completo = pd.read_csv('bien_mal_completo.csv')
    attr_completo_mal = df_attr_completo[df_attr_completo['B/M'] == 'MAL']
    attr_completo_mal_uniques = attr_completo_mal.heidel_type.unique()
    print(attr_completo_mal_uniques)
    for class_ in attr_completo_mal_uniques:
        print(str(class_) + str(attr_completo_mal[(attr_completo_mal['heidel_type'] == class_)].count())) #& (attr_completo_mal['corpus_type'] == class_)].count()))
    #print(attr_completo_mal[(attr_completo_mal['heidel_type'] == 'DURATION') & (attr_completo_mal['corpus_type'] == 'DURATION')].count())
    #print(attr_completo_mal[(attr_completo_mal['heidel_type'] == 'DATE') & (attr_completo_mal['corpus_type'] == 'DATE')].count())
    #print(attr_completo_mal[(attr_completo_mal['heidel_type'] == 'DATE') & (attr_completo_mal['corpus_type'] == 'DURATION')].count())
    #print(attr_completo_mal[(attr_completo_mal['heidel_type'] == 'SET') & (attr_completo_mal['corpus_type'] == 'DURATION')].count())
    """

    
    df_fn_completo = pd.read_csv('fn_heidel.csv')
    attr_completo_mal_uniques = df_fn_completo.timex3Class.unique()
    print(attr_completo_mal_uniques)
    #for class_ in attr_completo_mal_uniques:
    #    print(str(class_) + str(df_fn_completo[(df_fn_completo['timex3Class'] == class_)]
    print(str('SET: ') + str(df_fn_completo[(df_fn_completo['timex3Class'] == 'DURATION')]))
    


    list_unique = df_heidel.file.unique()
    for document in list_unique:
        #SE BUSCAN COINCIDENCIAS EN LAS EXPRESIONES QUE NO HAN TENIDO COINCIDENCIAS ANTES
        heidel_doc = df_heidel_final[df_heidel_final['file'] == document]
        e3c_doc = df_e3c_final[df_e3c_final['file'] == document]
        indexes = list(df_e3c_final[df_e3c_final['file'] == document].index.values)
        #SE RECORREN POR CADA EXPRESIÓN DE HEIDEL LAS EXPRESIONES DEL CORPUS EN BUSCA DE COINCIDENCIAS
        for _, time_exp in heidel_doc.iterrows():
            for index, e3c_rows in e3c_doc.iterrows():
                #MIRA A VER SI HAY EXPRESIONES DEL CORPUS CONTENIDAS EN LAS ANOTACIONES
                if e3c_doc.loc[index].string in time_exp['string']:
                    #SI COINCIDE EL STRING Y ESTÁ EN EL RANGO DE LA EXPRESIÓN CONTENEDORA SE COMPRUEBAN LOS ATRIBUTOS
                    if time_exp['end'] > e3c_doc.loc[index].end and time_exp['begin'] < e3c_doc.loc[index].begin:
                        if(e3c_doc.loc[index].timex3Class == time_exp['timex3Class'] and e3c_doc.loc[index].value == time_exp['value']):
                            tp_extent_relaxed_contenido+=1
                            tp_attr_relaxed_contenido+=1
                            df_e3c_final.drop(index = index, inplace=True)
                            df_heidel_final.drop(index = _, inplace=True)
                        else:
                            fp_attr_contenido+=1
                #MIRA A VER SI HAY EXPRESIONES DEL HEIDEL CONTENIDAS EN EL CORPUS
                elif time_exp['string'] in e3c_doc.loc[index].string:
                    #SI COINCIDE EL STRING Y ESTÁ EN EL RANGO DE LA EXPRESIÓN CONTENEDORA SE COMPRUEBAN LOS ATRIBUTOS
                    if e3c_doc.loc[index].end > time_exp['end'] and e3c_doc.loc[index].begin < time_exp['begin']:
                        if(e3c_doc.loc[index].timex3Class == time_exp['timex3Class'] and e3c_doc.loc[index].value == time_exp['value']):
                            tp_extent_relaxed_contenido+=1
                            tp_attr_relaxed_contenido+=1
                            df_e3c_final.drop(index = index, inplace=True)
                            df_heidel_final.drop(index = _, inplace=True)
                        else:
                            fp_attr_contenido+=1
    #print(df_e3c_final)
    #print(len(df_e3c_final.index))
    #print(df_heidel_final)
    #print(len(df_heidel_final.index))
    
    """
    #Esto es para meter en un csv las expresiones que no deberían haberse detectado (fp)
    df_heidel_final.to_csv('fp_heidel.csv')
    #Esto es para meter en un csv las expresiones que deberían haberse detectado (fn)
    df_e3c_final.to_csv('fn_heidel.csv')
    """

    tp_attr_relaxed = tp_attr_relaxed_final + tp_attr_relaxed_principio + tp_attr_relaxed_contenido + tp_attr_strict
    tp_extent_relaxed = tp_extent_relaxed_final + tp_extent_relaxed_principio  + tp_attr_relaxed_contenido        
    
   
   #Las siguientes líneas muestran por línea de comandos los resultados
    """
    print('Final mal:' + str(lista_final_mal))
    print()
    print('Final bien:' + str(lista_final_bien))
    print()
    print('Principio mal:' + str(lista_inicial_mal))
    print()
    print('Principio bien:' + str(lista_inicial_bien))
    """
    """
    print('TP EXTENT RELAXED: ' + str(tp_extent_relaxed)) 
    print('TP EXTENT STRICT: ' + str(tp_extent_strict)) 
    print('TP ATTR: ' + str(tp_attr_relaxed)) 
    print('FP: ' + str(len(df_heidel_final.index)))
    print('FN: ' + str(len(df_e3c_final.index)))
    print('Nº ATRIBUTOS EN EXPRESIONES COMPLETAS MAL: ' + str(fp_attr_completo))
    print('Nº ATRIBUTOS EN EXPRESIONES PRINCIPIO MAL: ' + str(fp_attr_principio))
    print('Nº ATRIBUTOS EN EXPRESIONES FINALES MAL: ' + str(fp_attr_final))
    print('Nº ATRIBUTOS EN EXPRESIONES CONTENIEDAS MAL: ' + str(fp_attr_contenido))
    print('Nº EXTENSIONES Y ATRIBUTOS COMPLETAS CORRECTAS: ' + str(tp_attr_strict))
    print('Nº EXTENSIONES Y ATRIBUTOS PRINCIPIO CORRECTAS: ' + str(tp_extent_relaxed_principio)) #SE PUEDE VER EL % DE ACIERTOS EN LOS ATRIBUTOS CUANDO LA EXTENSIÓN ES PARCIAL_FINAL Y PARCIAL_INICIAL (fp_attr_principio/tp_extent_relaxed_princpio)
    print('Nº EXTENSIONES Y ATRIBUTOS FINAL CORRECTAS: ' + str(tp_extent_relaxed_final)) #tp_extent_relaxed_principio = tp_attr_relaxed_principio
    print('Nº EXTENSIONES Y ATRIBUTOS CONTENIDAS CORRECTAS: ' + str(tp_extent_relaxed_contenido))
    print(len(df_heidel_final.index))
    #LOS FP SON LOS QUE SE HAN QUEDADO EN LA LISTA DE HEIDEL, PORQUE NO HAN ENCONTRADO COINCIDENCIA. 
    #LOS FN SON LOS QUE SE HAN QUEDADO EN LA LISTA DEL CORPUS
    P_strict = tp_extent_strict/(tp_extent_strict+len(df_heidel_final.index) - 31)
    R_strict = tp_extent_strict/(tp_extent_strict+len(df_e3c_final.index))
    F1_strict = (2*P_strict*R_strict)/(P_strict+R_strict)
   
    #LAS MÉTRICAS RELAXED CUENTAN LAS STRICT TAMBIÉN
    P_relaxed = (tp_extent_relaxed+tp_extent_strict)/(tp_extent_relaxed+tp_extent_strict+len(df_heidel_final.index) - 31)
    R_relaxed = (tp_extent_relaxed+tp_extent_strict)/(tp_extent_relaxed+tp_extent_strict+len(df_e3c_final.index))
    F1_relaxed = (2*P_relaxed*R_relaxed)/(P_relaxed+R_relaxed)

    #LAS MÉTRICAS DE LOS ATRIBUTOS SE CUENTAN CON RELAXED PORQUE SON ACIERTOS COMPLETOS EN EL ATRIBUTO. 
    #EL RELAXED O ESTRICT ES SOLO PARA LA EXTENSIÓN PERO LOS ATRIBUTOS SE CUENTAN ASÍ PARA VER EL COMPORTAMIENTO DEL HEIDEL
    P_attr = (tp_attr_relaxed)/(tp_attr_relaxed  + len(df_heidel_attr.index) - 31)
    R_attr = (tp_attr_relaxed )/(tp_attr_relaxed + tp_attr_strict + len(df_e3c_attr.index))
    F1_attr = (2*P_attr*R_attr)/(P_attr+R_attr)
    
    print('----------STRICT----------')
    print('PRECISION STRICT: ' + str(P_strict))
    print('RECALL STRICT: ' + str(R_strict))
    print('F1 STRICT: ' + str(F1_strict))
    print('----------RELAXED----------')
    print('PRECISION RELAXED: ' + str(P_relaxed))
    print('RECALL RELAXED: ' + str(R_relaxed))   
    print('F1 RELAXED: ' + str(F1_relaxed)) 
    print('----------ATTRIBUTES----------')
    print('PRECISION ATTR: ' + str(P_attr))
    print('RECALL ATTR: ' + str(R_attr))   
    print('F1 ATTR: ' + str(F1_attr)) 
    """

    """
    #NOTAS
    P_relaxed = tp_relaxed/(tp_relaxed + )
    P_attr_relaxed = P_relaxed * acc_attr_relaxed
    R_attr_relaxed = R_relaxed * acc_attr_relaxed
    P_attr_strict = P_strict * acc_attr_strict
    R_attr_strict = R_strict * acc_attr_strict
    
    if begin and end -> tp_strict y se borra de e3c_doc
    else if begin    -> tp_relaxed y se borra de e3c_doc
    else if end      -> tp_relaxed y se borra de e3c_doc
    else if string in E3C and +-tokens -> apuntado para comprobar y se comprueba cuando se acabe para evitar asignarlo a anotaciones equivocadas.
    else             -> fp 

    contar cuántos sobran en E3C y contarlos como fn

    if df[df['begin'] == begin] and df[df['end'] == end] 
    else if df[df['begin'] == begin]
    else if df[df['end'] == end]
    """


#------file_diff()-----#
"""
Ya que existen diferencias entre el número de ficheros anotados por HeidelTime y en E3C, se comparan qué ficheros están anotados y no deberían
haciendo una diferencia entre dos listas que contienen los ficheros anotados por ambos.
Se lee el csv, se cogen lo valores únicos de los ficheros y se crea un set para poder compararlos y sacar los elementos que son diferentes de una forma óptima
"""
def file_dif(file_1, file_2):
    

    set_1 = set(pd.read_csv(file_1).file.unique())
    set_2 = set(pd.read_csv(file_2).file.unique())

    print(set_1.symmetric_difference(set_2))




#--------------------------------------------------------------------------------------------------------------------------------------------#
# 
#                                                           IXAMED
#
#--------------------------------------------------------------------------------------------------------------------------------------------#
#Se tokenizan los textos con spicy
def pre_process_ixamed():

    nlp = Spanish()
    
    df = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/inputs_clear.csv')
    inputs = df['input_clear']
    inputs = inputs.str.replace('\r\n\r\n', '')
    begins = df['begin']
    files = df['file']
    files_ = files.tolist()
    tokenized_corpus = []
    offsets = []

    for input in inputs:
        doc = nlp(input)
        tokens = [token.text for token in doc]
        tokenized_corpus.append(tokens)
        offset = [token.idx for token in doc]
        offsets.append(offset)
    new_files = []
    for file in files_:
        file = file.replace('.xml', '.txt')
        new_files.append(file)

    #tokenized_corpus_ = []
    #tokenized_corpus_.remove('\r\n')
    i = 0 
    """
    while i < len(tokenized_corpus):
        if '\r\n' in tokenized_corpus[i]:
            while(tokenized_corpus.count('\r\n')):
                tokenized_corpus[i].remove('\r\n')
        if '\r\n\r\n' in tokenized_corpus:
            while(tokenized_corpus.count('\r\n')):
                tokenized_corpus[i].remove('\r\n\r\n')
        i += 1
    """
    while i < len(tokenized_corpus):
        if '\r\n' in tokenized_corpus[i]:
            #print(type(tokenized_corpus[i]))
            for j in range(tokenized_corpus[i].count('\r\n')):
                tokenized_corpus[i].remove('\r\n')
        """       
        for j in range(tokenized_corpus.count('\r\n')):
            print(i)
            if '\r\n' in tokenized_corpus[i]:
                print('HOLA')
                tokenized_corpus[i].replace('\r\n', '')
        """
        i += 1

    print(tokenized_corpus)


    """
    for row in tokenized_corpus:
        row_ = tostringlist(row)
        print(row)
        #tokenized_corpus.append(row.remove('\r\n'))
    print(tokenized_corpus_)
    """
    
    for lines, file in zip(tokenized_corpus, new_files):
        with open('/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation_tokenized/' + file, 'w') as f:
            for line in lines:
                f.write(line)
                f.write('\n')
             
"""
-Expresiones compuestas -> Si hay más de un token anotados seguidos se mete como 1. Cuando se encuentre coinidencia entre el begin del e3c y del ixamed se cuenta como acierto la expresión compuesta
-Acierto si se acierta el begin
-Fallo si el begin no está

Para cada expresion del ixa buscar en el corpus si hay alguna con el mismo begin -> entonces borrar coincidencias
tp -> si coincide el begin
fp -> los remanentes del ixa
fn -> los remanentes del e3c
"""
#Se cuadran los tokens de ixamed con los tokens del corpus
def expresiones_ixamed():
    #strings guarda los eventos detectados. strings_temp se utiliza para almacenar las palabras que componen un evento mayor. Tipos guarda de forma binaria si una palabra está anotada (1) o no (0) 
    strings = []
    strings_temp = []
    begin_temp = []
    begin_final = []
    end_temp =[]
    end_final = []
    tipos = []
    tipos_temp = []
    file_dest = '/Users/asdc/Proyectos/time_line_extraction/events_ixamed_con_begin.csv'
    #Se crea el csv para las anotaciones de ixamed
    create_csv(filename_e3c=file_dest, fields_e3c=['file', 'string', 'begin', 'end', 'type'])
    create_csv(filename_e3c='all_ixamed_begin_end.csv', fields_e3c=['file', 'string', 'begin', 'end'])
    for file in  os.listdir(PATH_IXAMED):
        path = PATH_IXAMED + file
        if path != PATH_IXAMED + '.DS_Store':
            #Para sacar el nombre los ficheros con xml hay que sustituir txt-tagged por xml
            file_ = file.replace("txt-tagged", "xml")
            df_corpus = pd.read_xml('/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation/Spanish/layer1/' + file_)
            df_begin = df_corpus[df_corpus['order'] == 0]
            df_end = df_begin['end'].astype(int)
            df_begin = df_begin['begin'].astype(int)
            beginings = df_begin.values.tolist()
            endings = df_end.values.tolist()
            

            with open(path) as f:
                lines = f.readlines()
            i = 0
            t = 0
            print(file_)
            while i in range(len(lines)-2):# and t in range(len(beginings)): #El -2 no entiendo exactamente porqué hay que ponerlo pero funciona, si no da index error así que entiendo que no puede acceder a los dos últimos elementos por algo? (creo que son caracteres de fin de fichero y se debe rallar)
                    
                #Guarda los tokens anotados consecutivamente en una sola expresión
                """
                if lines[i].split()[1] != 'O':
                    #Guardo en lista temporal
                    strings_temp.append(lines[i].split()[0]) 
                    #Guardo su begin temporal
                    begin_temp.append(beginings[t])
                """
                #Si está anotado
                #Diferencia en si el token es el principio de una expresión o un token intermedio para evitar anotar como una sola expresión expresiones independientes
                B = re.search(r"B-([a-z]|[A-Z])", lines[i].split()[1])
                I = re.search(r"I-([a-z]|[A-Z])", lines[i].split()[1])
                C = re.search(r"B-Estructura_Corporal", lines[i].split()[1])

                #Si es una expresión intermedia guarda en la lista temporal
                if I:
                    #print(lines[i].split()[0])
                    #Guardo en lista temporal
                    strings_temp.append(lines[i].split()[0]) 
                    #Guardo su begin temporal
                    begin_temp.append(beginings[t])
                    #Guardo su end temporal
                    end_temp.append(endings[t])
                    #Guardo su tipo temporal
                    tipos_temp.append(lines[i].split()[1])
                elif (lines[i].split()[1] == 'B-Estructura_Corporal') | (lines[i].split()[1] == 'B-Calificador'):
                    strings_temp.append(lines[i].split()[0]) 
                    #Guardo su begin temporal
                    begin_temp.append(beginings[t])
                    #Guardo su end temporal
                    end_temp.append(endings[t])
                    #Guardo su tipo temporal
                    tipos_temp.append(lines[i].split()[1])
                #Si es una expresión de comienzo y la lista temporal está vacía (no hay ninguna expreisón anotada), se anota en la lista (porque es la primera expresión encontrada temporalmente)
                elif B and len(strings_temp) == 0:
                    #print(lines[i].split()[0])
                    #Guardo en lista temporal
                    strings_temp.append(lines[i].split()[0]) 
                    #Guardo su begin temporal
                    begin_temp.append(beginings[t])
                    #Guardo su end temporal
                    end_temp.append(endings[t])
                    #Guardo su tipo temporal
                    tipos_temp.append(lines[i].split()[1])
                #Si es una expresión de comienzo y la lista no está vacía, se guarda la lista temporal en la definitiva y se guarda en la lista temporal la expresión nueva
                elif B and len(strings_temp) > 0:
                    #combino strings en uno solo por si es una expresión combinada
                    final_string = ''
                    for j in range(len(strings_temp)):
                        final_string += strings_temp[j]
                        #Mete un espacio entre palabra y palabra, a no ser que sea la última entonces no
                        if j != len(strings_temp) - 1:
                            final_string += ' '
                    #guardo lista temporal
                    strings.append(final_string)
                    tipos.append(tipos_temp[0])
                    begin_final.append(begin_temp[0])
                    end_final.append(end_temp[len(end_temp)-1])
                    #print('temporal: ' + str(end_temp))
                    #print('NUEVO: ' + str(end_temp[len(end_temp)-1]))
                    #limpio lista temporal
                    strings_temp.clear()
                    begin_temp.clear()
                    end_temp.clear()
                    tipos_temp.clear()
                    #Guardo en lista temporal
                    strings_temp.append(lines[i].split()[0]) 
                    #Guardo su begin temporal
                    begin_temp.append(beginings[t])
                    end_temp.append(endings[t])
                    #Guardo su tipo temporal
                    tipos_temp.append(lines[i].split()[1])

                #Si no está anotado
                else:
                    #Si la lista temporal NO está vacía: hay elementos anotados que guardar
                    if len(strings_temp) != 0:
                            #combino strings en uno solo por si es una expresión combinada
                            final_string = ''
                            for j in range(len(strings_temp)):
                                final_string += strings_temp[j]
                                #Mete un espacio entre palabra y palabra, a no ser que sea la última entonces no
                                if j != len(strings_temp) - 1:
                                    final_string += ' '
                            #guardo lista temporal
                            strings.append(final_string)
                            tipos.append(tipos_temp[0])
                            begin_final.append(begin_temp[0])
                            end_final.append(end_temp[len(end_temp)-1])
                            #limpio lista temporal
                            strings_temp.clear()
                            begin_temp.clear()
                            end_temp.clear()
                            tipos_temp.clear()
                    #Guardo en la lista definitiva y apunto que no está anotado
                    strings.append(lines[i].split()[0])
                    tipos.append(0)
                    begin_final.append(beginings[t])
                    end_final.append(endings[t])

                x = re.search(r"((([0-9]|[A-Z]|[a-z])-[0-9])|([0-9]-([0-9]|[A-Z]|[a-z]))|(([0-9]/[0-9])|([a-z]/[0-9]))|([a-z]\.[A-Z])|(\.\.\.))", lines[i].split()[0])               
                if x :
                    #print(lines[i].split()[0])
                    t += lines[i].split()[0].count('-') * 2
                    t += lines[i].split()[0].count('/') * 2
                    if lines[i].split()[0].count('.') == 1:
                        t += lines[i].split()[0].count('.') * 2
                    elif lines[i].split()[0].count('.') == 3:
                        t+=2
                    False
                i+=1
                t+=1
                """
                for h in range(len(strings)):
                    print(str(h) + ' BEGIN: ' + str(begin_final[h]))
                    #print(str(h) + ' END: ' + str(end_final[h]))
                    print(str(h) + ' STRING: ' + str(strings[h]))
                    print()
                """
            
            #Se crea un dataframe con el nombre del fichero, los strings y su tipo 
            ixamed_df = pd.DataFrame({'file':file_, 'string':strings, 'begin':begin_final, 'end': end_final, 'type':tipos})
            ixamed_all_df = pd.DataFrame({'file':file_, 'string':strings, 'begin':begin_final, 'end':end_final})
            #Se eliminan todos las líneas que no tengan anotación (tipo == 0)
            temp_df = ixamed_df[ixamed_df['type'] == 0].index
            ixamed_df.drop(temp_df, inplace=True)

            #Se escriben las filas en un csv
            with open(file_dest, 'a') as csvfile: 
                #creating a csv writer object 
                csvwriter = csv.writer(csvfile) 
                #writing the data rows 
                csvwriter.writerows(ixamed_df.values.tolist())
            
            #Se escriben todas los tokens del ixa con begin y end
            
            with open('all_ixamed_begin_end.csv', 'a') as csvfile: 
                #creating a csv writer object 
                csvwriter = csv.writer(csvfile) 
                #writing the data rows 
                csvwriter.writerows(ixamed_all_df.values.tolist())
                
            #Se vacían las listas y el dataframe
            ixamed_df = ixamed_df.iloc[0:0]
            ixamed_all_df = ixamed_all_df.iloc[0:0]
            strings.clear()
            tipos.clear()
            begin_final.clear()
            end_final.clear()
            f.close()

#Evalúa las anotaciones IxaMed con los clinentity del corpus
def evaluacion_ixamed_clinentity():
    
    df_ixa = pd.read_csv('events_ixamed_con_begin.csv')
    df_corpus = pd.read_csv('events.csv')
    files = df_corpus.file.unique()

    #unique_type = df_ixa.type.unique()
    

    df_corpus_sin = df_corpus[df_corpus['TLINK'] == '0']
    df_corpus_con = df_corpus[df_corpus['TLINK'] != '0']
    

    #Evaluación de clinentity
    df_clinentity = pd.read_csv('clinentity.csv')
    df_clinentity_aux_full = df_clinentity.copy()
    files = df_clinentity.file.unique()
    df_ixa_enf = df_ixa[df_ixa['type'] == 'B-Grp_Enfermedad']
    df_ixa_aux_full = df_ixa_enf.copy()
    ixa_parcial_inicial = []
    ixa_parcial_final = []
    tp_full = 0
    tp_begin = 0
    tp_end = 0
    fp = 0
    fn = 0
    
    for file in files:
        df_clinentity_act = df_clinentity[df_clinentity['file'] == file]
        df_ixa_act = df_ixa_enf[df_ixa_enf['file'] == file]
        
        #Por cada entrada en el ixa busca en a ver si está en las anotaciones
        for _, ixa_exp in df_ixa_act.iterrows(): 
            for index_, corpus_exp in df_clinentity_act.iterrows():
                #Si coincide begin y end se suma tp y tal
                if (ixa_exp['begin'] == corpus_exp['begin']) and (ixa_exp['end'] == corpus_exp['end']):
                    tp_full += 1
                    df_ixa_aux_full.drop(index = _, inplace=True)
                    df_clinentity_aux_full.drop(index=index_, inplace = True)
                    break
                #Si coincide solo begin
                elif ixa_exp['begin'] == corpus_exp['begin']:
                    tp_begin += 1
                    df_ixa_aux_full.drop(index = _, inplace=True)
                    df_clinentity_aux_full.drop(index=index_, inplace = True)
                    ixa_parcial_inicial.append(ixa_exp.tolist())
                    break   
                elif ixa_exp['end'] == corpus_exp['end']:
                    tp_end += 1
                    df_ixa_aux_full.drop(index = _, inplace=True)
                    df_clinentity_aux_full.drop(index=index_, inplace = True)
                    ixa_parcial_final.append(ixa_exp.tolist())
                    break
                
    """
    df_ixa_tp_parcial_final = pd.DataFrame(ixa_parcial_final, columns = ['file','string','begin','end','type'])
    df_ixa_tp_parcial_inicial = pd.DataFrame(ixa_parcial_inicial, columns = ['file','string','begin','end','type'])
    df_ixa_tp_parcial_final.to_csv('clinentity_ixamed_tp_parcial_final.csv')
    df_ixa_tp_parcial_inicial.to_csv('clinentity_ixamed_tp_parcial_inicial.csv')
    df_ixa_aux_full.to_csv('clinentity_ixamed_fp.csv')
    df_clinentity_aux_full.to_csv('clinentity_ixamed_fn.csv')
    """

    tp_parcial = tp_begin + tp_end
    #print(tp_parcial)
    

    print('Expresiones detectadas con extensión completa: ' + str(tp_full))
    print('Expresiones detectadas con parcial comienzo: ' + str(tp_begin))
    print('Expresiones detectadas con parcial final: ' + str(tp_end))
    print('FP: ' + str(len(df_ixa_aux_full.index)))
    print('FN: ' + str(len(df_clinentity_aux_full.index)))

    precision_total = (tp_full + tp_parcial)/((tp_full + tp_parcial + len(df_ixa_aux_full.index)))
    recall_total = (tp_full + tp_parcial)/((tp_full + tp_parcial + len(df_clinentity_aux_full.index)))
    F1 = (2*precision_total*recall_total) / (precision_total + recall_total)

    print('PRECISION: ' + str(precision_total))
    print('RECALL: ' + str(recall_total)) 
    print('F1: ' + str(F1))
    
        
    #df_corpus.to_csv('events_sinTLINK.csv', index=False)
    #df_corpus_con.to_csv('events_conTLINK.csv', index=False)

#Evalúa las anotaciones de IxaMed sobre el conjunto EVENT del corpus
def evaluacion_ixamed_events():
    df_events_corpus = pd.read_csv('events.csv')
    df_events_corpus_aux = df_events_corpus.copy()
    df_events_ixa = pd.read_csv('events_ixamed_con_begin.csv')
    df_events_ixa_aux = df_events_ixa.copy()
    
    print('Nº EXPRESIONES CORPUS: ' + str(len(df_events_corpus.index)))
    print('Nº EXPRESIONES IXA: ' + str(len(df_events_ixa.index)))

    files = df_events_corpus.file.unique()
    tp_inicial = 0
    tp_final = 0
    tp_completo = 0
    ixa_tp = []

    for file in files:
        df_ixa_act = df_events_ixa[df_events_ixa['file'] == file]
        df_corpus_act = df_events_corpus[df_events_corpus['file'] == file]
        for _, ixa_exp in df_ixa_act.iterrows(): 
            for index_, corpus_exp in df_corpus_act.iterrows():
                if (ixa_exp['begin'] == corpus_exp['begin']) and (ixa_exp['end'] == corpus_exp['end']):
                    tp_completo += 1
                    df_events_ixa_aux.drop(index = _, inplace=True)
                    df_events_corpus_aux.drop(index = index_, inplace=True)
                    ixa_tp.append(ixa_exp)
                    break  
                elif ixa_exp['begin'] == corpus_exp['begin']:
                    tp_inicial += 1
                    df_events_ixa_aux.drop(index = _, inplace=True)
                    df_events_corpus_aux.drop(index = index_, inplace=True)
                    ixa_tp.append(ixa_exp)
                    break   
                elif ixa_exp['end'] == corpus_exp['end']:
                    tp_final += 1
                    df_events_ixa_aux.drop(index = _, inplace=True)
                    df_events_corpus_aux.drop(index = index_, inplace=True)
                    ixa_tp.append(ixa_exp)
                    break
    tp = tp_completo + tp_final + tp_inicial
    print('TP COMPLETO: ' + str(tp_completo))
    print('TP INICIAL: ' + str(tp_inicial))
    print('TP FINAL: ' + str(tp_final))
    print('FN: ' + str(len(df_events_corpus_aux.index)))
    print('FP: ' + str(len(df_events_ixa_aux.index)))

    precision_total = (tp)/((tp + len(df_events_ixa_aux.index)))
    recall_total = (tp)/((tp + len(df_events_corpus_aux.index)))
    F1 = (2*precision_total*recall_total) / (precision_total + recall_total)

    print('PRECISION: ' + str(precision_total))
    print('RECALL: ' + str(recall_total)) 
    print('F1: ' + str(F1))

    df_ixa_tp = pd.DataFrame(ixa_tp, columns = ['file','string','begin','end','type'])
    
    df_events_corpus_aux.to_csv('events_FN.csv')
    df_events_ixa_aux.to_csv('events_FP.csv')
    df_ixa_tp.to_csv('events_TP.csv')


    False

#Calcula el número de entidades que son eventos y los que no 
def clinentity_events_join():
    df_clinentity = pd.read_csv('clinentity.csv')
    df_events = pd.read_csv('events.csv')
    files = df_clinentity.file.unique()
    clinentity_events = [] 
    tp = 0

    for file in files:
        df_clinentity_act = df_clinentity[df_clinentity['file'] == file]
        df_events_act = df_events[df_events['file'] == file]
        

        #Eventos que son entidades clínicas == entidades clínicas que son eventos
        #Entidades clínicas que son eventos (para saber cuántas entidades NO son eventos)

        #Por cada entrada en el ixa busca en a ver si está en las anotaciones
        for _, clintentity_exp in df_clinentity_act.iterrows(): 
            for index_, corpus_exp in df_events_act.iterrows():
                if clintentity_exp['begin'] == corpus_exp['begin']:
                    tp += 1
                    clinentity_events.append(clintentity_exp.tolist())
                    break   
                elif clintentity_exp['end'] == corpus_exp['end']:
                    tp += 1
                    clinentity_events.append(clintentity_exp.tolist())
                    break
    df_clinentity_events = pd.DataFrame(clinentity_events, columns = ['file','string','begin','end','type'])
    #df_clinentity_events.to_csv('clinentity_events.csv')

    print('Número de entidades clínicas que son eventos: ' + str(len(df_clinentity_events.index)))
    print('Número de entidades clínicas que NO son eventos: ' + str(int(len(df_clinentity.index)) - len(df_clinentity_events.index)))

#Se utiliza para crear los csv con las columnas que se quieran
def create_csv(filename_e3c, fields_e3c):

    with open(filename_e3c, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the FIELDS_E3C 
        csvwriter.writerow(fields_e3c) 

def write_ixamed_to_csv(file, output_clear, type):
    rows = []
    file_output = '/Users/asdc/Proyectos/time_line_extraction/prueba.csv'
    #Generates the rows for the csv
    for type_, output in zip(type, output_clear):
        row = [str(file), str(output), str(type_)]
        rows.append(row)
    # writing to csv file 
    with open(file_output, 'a') as csvfile: 
        #creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        #writing the data rows 
        csvwriter.writerows(rows)

#Los siguientes métodos sacan gráficos de los resultados de los modelos de transformers
def results_roberta_to_img():

    df_results_completo = pd.read_csv('resultados_train_24.csv', delimiter=';')
    df_results = df_results_completo[df_results_completo['Epoch'] != 0]
    index = []
    index = df_results[df_results['Run'] == 0].index.tolist()
    precision = []
    recall = []
    f1 = []
    eval_loss = []
    train_loss = [] 
    #wd = ['0.01', '0.1', '0.1', '0.01']
    #bs = ['8','8','16','16']
    wd = ['0.1', '0.1', '0.01', '0.01']
    bs = ['8','16','8','16']


    for i in range(0,4):
        #index.append(df_results[df_results['Run'] == 0].index.tolist())
        precision.append(df_results[df_results['Run'] == i]['precision'].tolist())
        plt.plot(index, precision[i], label = "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
    plt.xlabel('Epoch')
    plt.ylabel('Precision')
    plt.legend(fontsize = 'small')
    plt.savefig("precision.pdf", format="pdf", bbox_inches="tight")
    plt.show()

    for i in range(0,4):
        #index.append(df_results[df_results['Run'] == 0].index.tolist())
        recall.append(df_results[df_results['Run'] == i]['recall'].tolist())
        plt.plot(index, recall[i], label = "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
    plt.xlabel('Epoch')
    plt.ylabel('Recall')
    plt.legend(fontsize = 'small')
    plt.savefig("recall.pdf")
    plt.show()
    
    for i in range(0,4):
        #index.append(df_results[df_results['Run'] == 0].index.tolist())
        f1.append(df_results[df_results['Run'] == i]['f1'].tolist())
        plt.plot(index, f1[i], label = "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
    plt.xlabel('Epoch')
    plt.ylabel('f1')
    plt.legend(fontsize = 'small')
    plt.savefig("f1.pdf", format="pdf", bbox_inches="tight")
    plt.show()

    for i in range(0,4):
        #index.append(df_results[df_results['Run'] == 0].index.tolist())
        eval_loss.append(df_results[df_results['Run'] == i]['evaluation_loss'].tolist())
        plt.plot(index, eval_loss[i], label = "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
    plt.xlabel('Epoch')
    plt.ylabel('evaluation_loss')
    plt.legend(fontsize = 'small')
    plt.savefig("eval_loss.pdf", format="pdf", bbox_inches="tight")
    plt.show()

    for i in range(0,4):
        #index.append(df_results[df_results['Run'] == 0].index.tolist())
        train_loss.append(df_results[df_results['Run'] == i]['training_loss'].tolist())
        plt.plot(index, train_loss[i], label = "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
    plt.xlabel('Epoch')
    plt.ylabel('training_loss')
    plt.legend(fontsize = 'small')
    plt.savefig("train_loss.pdf", format="pdf", bbox_inches="tight")
    plt.show()
    
    for i in range(0,4):
        plt.plot(index, train_loss[i], label = "Training_loss: " + "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
        plt.plot(index, eval_loss[i], label = "Evaluation_loss: " + "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(fontsize = 'small')
        plt.savefig("Train_Eval_Batch_size=" + str(bs[i]) + '_Weight_decay=' + str(wd[i]) + ".pdf", format="pdf", bbox_inches="tight")
        plt.show()

def results_roberta_to_img2():
    df_results_completo = pd.read_csv('resultados_train_24_4_2.csv', delimiter=';')
    df_results = df_results_completo[0:24]
    index = []
    index = df_results.index.tolist()

    print(df_results)

    precision = df_results['precision']
    recall = df_results['recall']
    f1 = df_results['f1']
    eval_loss = df_results['evaluation_loss']
    train_loss = df_results['training_loss']


    
    #index.append(df_results[df_results['Run'] == 0].index.tolist())
    #precision.append(df_results[df_results['Run'] == i]['precision'].tolist())
    plt.plot(index, precision, label = "Precisión")
    plt.plot(index, recall, label = "Recall" )
    plt.plot(index, f1, label = "f1" )
    plt.xlabel('Epoch')
    plt.ylabel('Metric Value')
    plt.legend(fontsize = 'small')
    plt.savefig("total2.pdf", format="pdf", bbox_inches="tight")
    plt.show()
    
    plt.plot(index, eval_loss, label = "Evaluation Loss")
    plt.plot(index, train_loss, label = "Train Loss" )
    plt.xlabel('Epoch')
    plt.ylabel('Metric Value')
    plt.legend(fontsize = 'small')
    plt.savefig("total_loss2.pdf", format="pdf", bbox_inches="tight")
    plt.show()
    
    """
    for i in range(0,4):
        #index.append(df_results[df_results['Run'] == 0].index.tolist())
        recall.append(df_results[df_results['Run'] == i]['recall'].tolist())
        plt.plot(index, recall[i], label = "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
    plt.xlabel('Epoch')
    plt.ylabel('Recall')
    plt.legend(fontsize = 'small')
    plt.savefig("recall2.pdf")
    plt.show()
    
    for i in range(0,4):
        #index.append(df_results[df_results['Run'] == 0].index.tolist())
        f1.append(df_results[df_results['Run'] == i]['f1'].tolist())
        plt.plot(index, f1[i], label = "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
    plt.xlabel('Epoch')
    plt.ylabel('f1')
    plt.legend(fontsize = 'small')
    plt.savefig("f12.pdf", format="pdf", bbox_inches="tight")
    plt.show()

    for i in range(0,4):
        #index.append(df_results[df_results['Run'] == 0].index.tolist())
        eval_loss.append(df_results[df_results['Run'] == i]['evaluation_loss'].tolist())
        plt.plot(index, eval_loss[i], label = "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
    plt.xlabel('Epoch')
    plt.ylabel('evaluation_loss')
    plt.legend(fontsize = 'small')
    plt.savefig("eval_loss2.pdf", format="pdf", bbox_inches="tight")
    plt.show()

    for i in range(0,4):
        #index.append(df_results[df_results['Run'] == 0].index.tolist())
        train_loss.append(df_results[df_results['Run'] == i]['training_loss'].tolist())
        plt.plot(index, train_loss[i], label = "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
    plt.xlabel('Epoch')
    plt.ylabel('training_loss')
    plt.legend(fontsize = 'small')
    plt.savefig("train_loss2.pdf", format="pdf", bbox_inches="tight")
    plt.show()
    
    for i in range(0,4):
        plt.plot(index, train_loss[i], label = "Training_loss: " + "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
        plt.plot(index, eval_loss[i], label = "Evaluation_loss: " + "Batch_size = " + str(bs[i]) + ', Weight_decay = ' + str(wd[i]))
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(fontsize = 'small')
        plt.savefig("Train_Eval_Batch_size=" + str(bs[i]) + '_Weight_decay=' + str(wd[i]) + "2.pdf", format="pdf", bbox_inches="tight")
        plt.show()
    """
def results_roberta_loss():
    df_results_completo = pd.read_csv('resultados_train_24_4.csv', delimiter=';')
    df_results = df_results_completo[(df_results_completo['Epoch'] != 0)] #| (df_results_completo['Epoch'] != -1)]
    eval_loss = df_results[df_results['Run'] == 0]['evaluation_loss'].tolist()
    training_loss = df_results[df_results['Run'] == 0]['training_loss'].tolist()

    print('.------------.')
   

    eval_loss_evolucion = [eval_loss[i] - eval_loss[i+1] for i in range(len(eval_loss) - 1)]
    training_loss_evolucion = [training_loss[i] - training_loss[i+1] for i in range(len(training_loss) - 1)]
    
    training_loss_entre_eval_loss = [training_loss[i] / eval_loss[i] for i in range(len(training_loss))]
    eval_loss_entre_training_loss = [eval_loss[i] / training_loss[i] for i in range(len(training_loss))]


    #eval_loss_total_ = [abs(var) for var in eval_loss_total]
    #print(statistics.mean(eval_loss_total_))
    
    print('Media de DECRECIMIENTO de EVALUATION LOSS: ' + str(statistics.mean(eval_loss_evolucion))) 
    print('Media de DECRECIMIENTO de TRAINING LOSS: ' + str(statistics.mean(training_loss_evolucion))) 

    
    print('Media de PROPORCION de TRAINING LOSS/EVAL LOSS: ' + str(statistics.mean(training_loss_entre_eval_loss)))
    print('Desviación estándar de PROPORCION de TRAINING LOSS/EVAL LOSS: ' + str(statistics.stdev(training_loss_entre_eval_loss)))
    print('Media de PROPORCION de EVAL LOSS/TRAINING LOSS: ' + str(statistics.mean(eval_loss_entre_training_loss))) 
    print('Desviación estándar de PROPORCION de EVAL LOSS/TRAINING LOSS: ' + str(statistics.stdev(eval_loss_entre_training_loss))) 
    
    False

def results_roberta_loss2():
    df_results_completo = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/eventos_evaluacion/resultados_train_24_4_2.csv', delimiter=';')
    df_results = df_results_completo[0:24] #| (df_results_completo['Epoch'] != -1)]

    eval_loss = df_results['evaluation_loss'].tolist()
    training_loss = df_results['training_loss'].tolist()

    print('.------------.')
   

    eval_loss_evolucion = [eval_loss[i] - eval_loss[i+1] for i in range(len(eval_loss) - 1)]
    training_loss_evolucion = [training_loss[i] - training_loss[i+1] for i in range(len(training_loss) - 1)]
    
    training_loss_entre_eval_loss = [training_loss[i] / eval_loss[i] for i in range(len(training_loss))]
    eval_loss_entre_training_loss = [eval_loss[i] / training_loss[i] for i in range(len(training_loss))]


    #eval_loss_total_ = [abs(var) for var in eval_loss_total]
    #print(statistics.mean(eval_loss_total_))
    
    print('Media de DECRECIMIENTO de EVALUATION LOSS: ' + str(statistics.mean(eval_loss_evolucion))) 
    print('Media de DECRECIMIENTO de TRAINING LOSS: ' + str(statistics.mean(training_loss_evolucion))) 

    
    print('Media de PROPORCION de TRAINING LOSS/EVAL LOSS: ' + str(statistics.mean(training_loss_entre_eval_loss)))
    print('Desviación estándar de PROPORCION de TRAINING LOSS/EVAL LOSS: ' + str(statistics.stdev(training_loss_entre_eval_loss)))
    print('Media de PROPORCION de EVAL LOSS/TRAINING LOSS: ' + str(statistics.mean(eval_loss_entre_training_loss))) 
    print('Desviación estándar de PROPORCION de EVAL LOSS/TRAINING LOSS: ' + str(statistics.stdev(eval_loss_entre_training_loss))) 
    


def resultados_epoch_relaciones():
    
    labels = ['NO', 'Before', 'Simultaneous', 'Contains', 'Overlap', 'Ends-On', 'Begins-On', 'Weighted-Average']
    labels = ['No-Relation', 'Contains', 'Overlap', 'Before', 'Begins-On', 'Ends-On', 'Simultaneous', 'Weighted-Average']
    x = np.arange(len(labels)) 

    #Para los epochs
    #df_4 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_bioRoberta_bs16_epoch4_dataset_1.csv')
    #df_8 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_bioRoberta_bs16_epoch8_dataset_1.csv')
    #df_12 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_bioRoberta_bs16_epoch12_dataset_1.csv')

    #Para el batch size
    #df_4 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_bioRoberta_bs4_epoch4_dataset_1.csv')
    #df_8 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_bioRoberta_bs8_epoch4_dataset_1.csv')
    #df_12 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_bioRoberta_bs16_epoch4_dataset_1.csv') #Se llama df_12 aunque sea batch size 16 para no cambiar más código

    #Para el loss
    #df_8 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_bioRoberta_bs8_epoch4_dataset_1.csv')
    #df_12 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_bioRoberta_bs4_epoch4_lossNORMAL_dataset_1.csv')

    #Para los modelos dataset 1
    #df_4 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_bioRoberta_bs8_epoch4_dataset_1.csv')
    #df_8 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_beto_bs8_epoch4_dataset_1.csv')
    #df_12 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_roberta_bs8_epoch4_dataset_1.csv')
    #df_12 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_beto_bs8_epoch8_dataset_1.csv')

    #Para los modelos dataset 2
    df_4 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_bioRoberta_bs8_epoch4_dataset_2.csv')
    df_8 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_beto_bs8_epoch4_dataset_2.csv')
    df_12 = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/relaciones_resultados/class_report_roberta_bs8_epoch4_dataset_2.csv')

    df_4 = df_4.iloc[len(df_4) - 8: len(df_4)] 
    df_8 = df_8.iloc[len(df_8) - 8: len(df_8)] 
    df_12 = df_12.iloc[len(df_12) - 8: len(df_12)] 


    df_4['Unnamed: 0'] = labels 
    df_8['Unnamed: 0'] = labels 
    df_12['Unnamed: 0'] = labels 


    data1 = df_4['f1-score'].tolist()
    data2 = df_8['f1-score'].tolist()
    data3 = df_12['f1-score'].tolist()
    width = 0.25

    
    fig, ax = plt.subplots(figsize=(10,8))
    #Para los epochs
    #rect1 = ax.bar(x - width/2, data1, label='4 epochs', width=width)
    #rect2 = ax.bar(x + width/2, data2, label='8 epochs', width=width)
    #rect3 = ax.bar(x + width/2 + width, data3, label='12 epochs', width=width)

    #Para el batch size
    #rect1 = ax.bar(x - width/2, data1, label='batch size 4', width=width)
    #rect2 = ax.bar(x + width/2, data2, label='batch size 8', width=width)
    #rect3 = ax.bar(x + width/2 + width, data3, label='batch size 16', width=width)

    #Para el loss
    rect1 = ax.bar(x - width/2, data1, label='BioThyme-RoBERTa-es', width=width)
    rect2 = ax.bar(x + width/2, data2, label='BETO', width=width)
    rect3 = ax.bar(x + width/2 + width, data3, label='RoBERTa', width=width)
    #rect2 = ax.bar(x + width/2, data2, label='Beto 4 epoch', width=width)
    #rect3 = ax.bar(x + width/2 + width, data3, label='Beto 8 epoch', width=width)
    #rect2 = ax.bar(x + width/2, data2, label='BETO', width=width)
    #rect3 = ax.bar(x + width/2 + width, data3, label='RoBERTa', width=width)

    ax.set_ylabel('Relation Class')
    ax.set_xlabel('F-1 Value', labelpad=0)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, fontsize = 'small')
    ax.legend(fontsize = 'small')
    
    #plt.savefig("bioRoberta_4_8_12epochs_f1.pdf", format="pdf", bbox_inches="tight")
    #plt.savefig("bioRoberta_4_8_16batchsize_f1.pdf", format="pdf", bbox_inches="tight")
    #plt.savefig("bioRoberta_8bs_4epoch_loss_f1.pdf", format="pdf", bbox_inches="tight")
    plt.savefig("modelos_8bs_4epoch_f1_dataset1.pdf", format="pdf", bbox_inches="tight")
    #plt.savefig("modelos_8bs_4epoch_f1_dataset2.pdf", format="pdf", bbox_inches="tight")
    plt.show()

    """
    plt.bar(np.arange(len(data1)), data1, alpha=0.7, width=width, label='4 epochs')
    plt.bar(np.arange(len(data2))+ width, data2, width=width, alpha=0.7, label='8 epochs')
    plt.bar(np.arange(len(data3))+ width*2, data3, width=width, alpha=0.7, label='12 epochs')
    plt.grid(color='#95a5a6', linestyle='--', linewidth=1.5, axis='y', alpha=0.4)
    plt.xlabel('Relation Class')
    plt.ylabel('F-1 Value')
    plt.legend(fontsize = 'small')
    plt.show()
    """
    
def main():
    #insert_file_id('/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel.csv', '/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel_conID.csv')
    
    #file_dif('/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel.csv', '/Users/asdc/Proyectos/time_line_extraction/time_expresions.csv')
    
    #evaluacion_heidel('/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel.csv', '/Users/asdc/Proyectos/time_line_extraction/time_expresions.csv')

    #evaluacion_heidel('/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel.csv', '/Users/asdc/Proyectos/time_line_extraction/time_expresions_curated.csv')
    
    #quitar_thyme('/Users/asdc/Proyectos/time_line_extraction/time_expresions.csv', '/Users/asdc/Proyectos/time_line_extraction/time_expresions_curated.csv')
    
    #pre_process_ixamed()

    #expresiones_ixamed()

    #evaluacion_ixamed_clinentity()

    #clinentity_events_join()
    
    #evaluacion_ixamed_events()

    #results_roberta_to_img()

    #results_roberta_to_img2()

    #results_roberta_loss()

    #results_roberta_loss2()

    resultados_epoch_relaciones()
    



    False
if __name__ == "__main__":
    main()