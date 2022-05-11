from pickle import FALSE
from pickletools import read_string1
from pydoc import doc
import string
from sys import displayhook
from tokenize import String
from xml.etree.ElementTree import tostringlist
from numpy import row_stack, true_divide
import pandas as pd
from spacy.lang.es import Spanish
import os
import csv

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
    
    
    lista_final = []
    lista_final.append(lista_inicial_bien)
    lista_final.append(lista_inicial_mal)
    lista_final.append(lista_final_bien)
    lista_final.append(lista_final_mal)
    
    create_csv('bien_mal_parcial.csv', ['file','I/F', 'B/M', 'heidel', 'heidel_type', 'corpus', 'corpus_type'])
    with open ('bien_mal_parcial.csv', 'w') as f:
        write = csv.writer(f)
        write.writerows(["file",'I/F', 'B/M', 'heidel', 'heidel_type', 'corpus', 'corpus_type'])
        write.writerows(lista_inicial_bien)
        write.writerows(lista_inicial_mal)
        write.writerows(lista_final_bien)
        write.writerows(lista_final_mal)
    
    #create_csv('bien_mal_completo.csv', ['file', 'B/M', 'heidel', 'heidel_type', 'corpus', 'corpus_type'])
    with open ('bien_mal_completo.csv', 'w') as f:
        write = csv.writer(f)
        header = ['file', 'B/M', 'heidel', 'heidel_type', 'corpus', 'corpus_type']
        write.writerows(header)
        write.writerows(lista_completa_bien)
        write.writerows(lista_completa_mal)
    
    df_attr_completo = pd.read_csv('bien_mal_completo.csv')
    print(df_attr_completo[df_attr_completo[2] == 'BIEN'])


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
        #break
    #print(df_e3c_final)
    #print(len(df_e3c_final.index))
    #print(df_heidel_final)
    #print(len(df_heidel_final.index))
    
    df_heidel_final.to_csv('fp_heidel.csv')
    df_e3c_final.to_csv('fn_heidel.csv')

    tp_attr_relaxed = tp_attr_relaxed_final + tp_attr_relaxed_principio + tp_attr_relaxed_contenido + tp_attr_strict
    tp_extent_relaxed = tp_extent_relaxed_final + tp_extent_relaxed_principio  + tp_attr_relaxed_contenido        
    
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
    print(len(df_heidel_attr.index))
    #LOS FP SON LOS QUE SE HAN QUEDADO EN LA LISTA DE HEIDEL, PORQUE NO HAN ENCONTRADO COINCIDENCIA. 
    #LOS FN SON LOS QUE SE HAN QUEDADO EN LA LISTA DEL CORPUS
    P_strict = tp_extent_strict/(tp_extent_strict+len(df_heidel_final.index))
    R_strict = tp_extent_strict/(tp_extent_strict+len(df_e3c_final.index))
    F1_strict = (2*P_strict*R_strict)/(P_strict+R_strict)
   
    #LAS MÉTRICAS RELAXED CUENTAN LAS STRICT TAMBIÉN
    P_relaxed = (tp_extent_relaxed+tp_extent_strict)/(tp_extent_relaxed+tp_extent_strict+len(df_heidel_final.index))
    R_relaxed = (tp_extent_relaxed+tp_extent_strict)/(tp_extent_relaxed+tp_extent_strict+len(df_e3c_final.index))
    F1_relaxed = (2*P_relaxed*R_relaxed)/(P_relaxed+R_relaxed)

    #LAS MÉTRICAS DE LOS ATRIBUTOS SE CUENTAN CON RELAXED PORQUE SON ACIERTOS COMPLETOS EN EL ATRIBUTO. 
    #EL RELAXED O ESTRICT ES SOLO PARA LA EXTENSIÓN PERO LOS ATRIBUTOS SE CUENTAN ASÍ PARA VER EL COMPORTAMIENTO DEL HEIDEL
    P_attr = (tp_attr_relaxed)/(tp_attr_relaxed  + len(df_heidel_attr.index))
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
    P_relaxed = tp_relaxed/(tp_relaxed + )
    P_attr_relaxed = P_relaxed * acc_attr_relaxed
    R_attr_relaxed = R_relaxed * acc_attr_relaxed
    P_attr_strict = P_strict * acc_attr_strict
    R_attr_strict = R_strict * acc_attr_strict
    
    """
    """
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
def pre_process_ixamed():

    nlp = Spanish()
    
    df = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/inputs_clear.csv')
    inputs = df['input_clear']
    inputs = inputs.str.replace('\r\n\r\n', '')
    
    
    files = df['file']
    files_ = files.tolist()
    
    tokenized_corpus = []
#HAY QUE HACER QUE DESPUES DE UN PUNTO PONGA UN ESPACIO COMO TOKEN Y QUE LOS SALTOS DE LINEA NO LOS META
    for input in inputs:
        doc = nlp(input)
        tokens = [token.text for token in doc]
        tokenized_corpus.append(tokens)
    new_files = []
    for file in files_:
        file = file.replace('.xml', '.txt')
        new_files.append(file)

    tokenized_corpus_ = []
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
tp -> se coincide el begin
fp -> los remanentes del ixa
fn -> los remanentes del e3c
"""

def expresiones_ixamed():
    #strings guarda los eventos detectados. strings_temp se utiliza para almacenar las palabras que componen un evento mayor. Tipos guarda de forma binaria si una palabra está anotada (1) o no (0) 
    strings = []
    strings_temp = []
    tipos = []
    file_dest = '/Users/asdc/Proyectos/time_line_extraction/events_ixamed.csv'
    #Se crea el csv para las anotaciones de ixamed
    create_csv(filename_e3c=file_dest, fields_e3c=['file', 'string', 'type'])
    for file in  os.listdir(PATH_IXAMED):
        path = PATH_IXAMED + file
        if path != PATH_IXAMED + '.DS_Store':
            with open(path) as f:
                lines = f.readlines()
            for i in range(len(lines)-2): #El -2 no entiendo exactamente porqué hay que ponerlo pero funciona, si no da index error así que entiendo que no puede acceder a los dos últimos elementos por algo? (creo que son caracteres de fin de fichero y se debe rallar)
                #Si está anotado
                if lines[i].split()[1] != 'O':
                    #Guardo en lista temporal
                    strings_temp.append(lines[i].split()[0])
                #Si no está anotado
                else:
                    #Guardo en la lista definitiva y apunto que no está anotado
                    strings.append(lines[i].split()[0])
                    tipos.append(0)
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
                            tipos.append(1)
                            #limpio lista temporal
                            strings_temp.clear()
            #Para sacar el nombre los ficheros con xml hay que sustituir txt-tagged por xml
            file_ = file.replace("txt-tagged", "xml")

            #Se crea un dataframe con el nombre del fichero, los strings y su tipo 
            ixamed_df = pd.DataFrame({'file':file_, 'string':strings, 'type':tipos})

            #Se eliminan todos las líneas que no tengan anotación (tipo == 0)
            temp_df = ixamed_df[ixamed_df['type'] == 0].index
            ixamed_df.drop(temp_df, inplace=True)

            #Se escriben las filas en un csv
            with open(file_dest, 'a') as csvfile: 
                #creating a csv writer object 
                csvwriter = csv.writer(csvfile) 
                #writing the data rows 
                csvwriter.writerows(ixamed_df.values.tolist())

            #Se vacían las listas y el dataframe
            ixamed_df = ixamed_df.iloc[0:0]
            strings.clear()
            tipos.clear()
            f.close()


def evaluacion_ixamed():
    #leer los dos csv
    #sacar lineas por file
    #comparar si un el primer token de cada string de ixa está en corpus
    #si está tp++ y se borra la primera ocurrencia de este token en corpus y la línea en ixa(se puede borrar por índice porque se sabe qué línea es)
    #Para borrar del ixa solo la primera ocurrencia no sé cómo se podrá hacer
    #Quizá pasarlo a listas sería más fácil? Tipo todas las líneas por file se pasan a lista y se comprueba si está, si está se mete un for que busque la primera coincidencia
    #Cuando se termine con el file se append la lista a una lista definitiva tanto para ixa como para corpus
    False

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

def main():
    #insert_file_id('/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel.csv', '/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel_conID.csv')
    
    #file_dif('/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel.csv', '/Users/asdc/Proyectos/time_line_extraction/time_expresions.csv')
    
    evaluacion_heidel('/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel.csv', '/Users/asdc/Proyectos/time_line_extraction/time_expresions.csv')

    #evaluacion_heidel('/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel.csv', '/Users/asdc/Proyectos/time_line_extraction/time_expresions_curated.csv')
    
    #quitar_thyme('/Users/asdc/Proyectos/time_line_extraction/time_expresions.csv', '/Users/asdc/Proyectos/time_line_extraction/time_expresions_curated.csv')
    
    #pre_process_ixamed()

    #expresiones_ixamed()
    False
if __name__ == "__main__":
    main()