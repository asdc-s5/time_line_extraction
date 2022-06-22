from cmath import nan
import difflib as dl
from errno import EAGAIN
from lib2to3.pgen2 import token
from logging.handlers import DEFAULT_TCP_LOGGING_PORT
from operator import index
from pickle import FALSE
from pprint import pprint
from turtle import clear, pensize
from venv import create
from xml.etree.ElementInclude import FatalIncludeError
from matplotlib.pyplot import bar_label
from pyparsing import col
import unidecode
import pandas as pd
import ast
import string
import re
import os
import csv
import sys
import numpy as np
import math
import ast
import random
from itertools import combinations
from zmq import EVENT_CLOSE_FAILED

sys.path.insert(0, '/Users/asdc/Proyectos/time_line_extraction/python_heideltime/python_heideltime')

from python_heideltime import Heideltime
from xml.etree import cElementTree as ET

#------GLOBAL VARIABLES-----#
FIELDS_E3C = ['file', 'id', 'string','begin', 'end', 'value', 'timex3Class', 'timexLink'] 
FILENAME_E3C = "time_expresions.csv"
PATH = '/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation/Spanish/layer1/'
PATH_HEIDEL = '/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation_heidel/'


#SACAR LA FECHA DE REGISTRO DEL FICHERO PARA PASARSELA COMO REFERENCIA EL HEIDEL#
#ESTRUCTURAR EL CÓDIGO CON MAIN Y MÉTODO PARA EXTRAER TEXTO Y EXPRESIONES DEL DATASET Y RESULTADOS DEL HEIDELTIME#

    
#------EXTRACT_TEXT-----#
"""
Extrae el texto clínico del XML
Generalmente el id de la fila que contiene el texto tiene id=12, pero no siempre es así. 
Lo que sí se cumple siempre es que el sofa de todas las filas indica el id de la fila con el texto.
Por lo que se saca el sofa de la primera fila y se matchea con la fila con id=sofa.
Por otra parte, en la fila con el texto, el texto no siempre ocupa la posición 0, también puede ser la 1. 
Para solucionarlo se ejecuta un if por si la posición 0==None
""" 
def extract_text(file):
    path = PATH + file

    df = pd.read_xml(path)
    input_id = df.loc[df['id'] == 1]
    input_id = input_id['sofa']
    input_id = int(input_id.values[0])

    input_ = df.loc[df['id'] == input_id]
    input_ = input_['sofaString']
    if input_.values[0] == None:
        return input_.values[1]#.replace("\n\t", "  ")
    else: 
        return input_.values[0]#.replace("\n\t", "  ")

    
#------EXTRACT_EXPRESIONS-----#
"""
Extrae las expresiones temporales correspondientes al texto del XML
Teniendo dos listas de pares, una 'begin' y otra 'end' que tienen el caracter inicial y final de cada expresión respecitavamente,
solo se recorre caracter a caracter cada pareja begin-end y lo guarda en un String 
"""
def extract_expresions(df_xml, input_clear):

    output_=[]

    for begin, end in zip(df_xml['begin'], df_xml['end']):
        texp = ""
        begin = int(begin)
        end = int(end)
        while begin <= end:
            texp += input_clear[begin] 
            begin+=1
        output_.append(texp)


    """
    Elimina los posibles espacios finales y signos de puntuación de las expresiones temporales
    -Puede darse el caso en el que se cuente un espacio o un signo de puntuación después de la primera palabra.
    Por lo que se van a eliminar todos los signos de puntuación y espacios que no estén entre palabras.
    -La forma más sencilla de eliminar los espacios sobrantes es con la función split, aunque podría buscarse una re que fuera más rápida.
    -El método más rápido para eliminar signos de puntuación es translate.
    """
    output_clear = []
    for out in output_:
        #------ELIMINA SIGNOS DE PUNTUACIÓN----#
        clear_string = out.translate(str.maketrans('', '', string.punctuation))

        #------ELIMINA ESPACIOS----#
        clear_string = ' '.join(clear_string.split())

        output_clear.append(clear_string)
    return output_clear

#------EXTRACT_EVENTS-----#
"""
Extrae los eventos del XML
-Como el xml está ordenado por etiquetas y los eventos no tienen etiquetas distintivas sobre las que poder filtrar sobre otras,
se ha utilizado otra librería para tratar el XML. Primero filtra por la etiqueta correspondiente a los eventos, que está definido en el XML
(en la primera fila) y después filtra por las etiquetas correspondientes (begin, end, etc.), todo eso lo mete en un dataframe
para poder pasarlo a un csv más tarde.
"""
def extract_events():
    create_csv(filename_e3c='/Users/asdc/Proyectos/time_line_extraction/events.csv', fields_e3c=['file', 'id_event', 'string', 'begin', 'end', 'ALINK', 'TLINK', 'contextualAspect', 'contextualModality', 'degree', 'docTimeRel', 'eventType', 'permanence', 'polarity'])
    for file in  os.listdir(PATH):
        path = PATH + file
        if path != '/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation/Spanish/layer1/.DS_Store':
            df = pd.read_xml(path)
            df_event = pd.DataFrame(df, columns= ['id','begin','end','ALINK', 'TLINK', 'contextualAspect', 'contextualModality', 'degree', 'docTimeRel', 'eventType', 'permanence', 'polarity'])
            df_event = df_event.loc[df_event['permanence'].isin(['FINITE', 'PERMANENT'])]
            input_clear = extract_text(file)
            output_clear = extract_expresions(df_event, input_clear)
            df_event = df_event.fillna(0)
            #print(df_event)
            write_events_to_csv(file, df_event['id'], output_clear, df_event['begin'], df_event['end'], df_event['ALINK'], df_event['TLINK'], df_event['contextualAspect'], df_event['contextualModality'], df_event['degree'], df_event['docTimeRel'], df_event['eventType'], df_event['permanence'], df_event['polarity'])
        
    #La forma original con la que sacaba los eventos. Mucho más enrevesado y menos eficiente.
    """
    dfcols = ['begin', 'end']
    df_event = pd.DataFrame(columns=dfcols)
    root = ET.parse(path)

    rows = root.findall('.//{http:///webanno/custom.ecore}EVENT')
    for row in rows:
        #print(row.attrib['begin'])
        begin = row.attrib['begin']
        end = row.attrib['end'] 
        #print(begin, end)
        df_event = df_event.append(pd.Series([begin, end], index=dfcols), ignore_index=True)
    """

#------EXTRACT_CLINENTITY-----#
def extract_clienentity():
    dfcols = ['file', 'string', 'begin', 'end', 'entityID']
    create_csv(filename_e3c='/Users/asdc/Proyectos/time_line_extraction/clinentity.csv', fields_e3c=dfcols)
    df_clinEntities = pd.DataFrame(columns=dfcols)
    file_ = []
    strings = []
    begin = []
    end = []
    entityID = []
    for file in  os.listdir(PATH):
        path = PATH + file
        if path != '/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation/Spanish/layer1/.DS_Store':
            for event, elem in ET.iterparse(path):
                if elem.tag == '{http:///webanno/custom.ecore}CLINENTITY':
                    file_.append(file)
                    begin.append(elem.attrib['begin'])
                    end.append(elem.attrib['end'])
                    entityID.append(elem.attrib['entityID'])
            input_clear = extract_text(file)
            df_clinEntities = pd.DataFrame(list(zip(begin, end)), columns = ['begin', 'end'])
            output_clear = extract_expresions(df_clinEntities, input_clear)
            print(output_clear)
            write_clinentity_to_csv(file, output_clear, begin, end, entityID)
            begin.clear()
            file_.clear()
            end.clear()
            entityID.clear()
            df_clinEntities.iloc[0:0]
#SACAR EL STRING TAMBIÉN

    #df_prueba = pd.DataFrame(list(zip(file_, begin, end, entityID)), columns = ['file','begin', 'end', 'CLINENTITY'])
    """
    Esto es un intento de sacarlo pero que no va. La idea es ya teniendo qué begin y end son de qué file pues sacar el string. No sé porqué no va
    for file in os.listdir(PATH):
            input_clear = extract_text(file)
            output_clear = extract_expresions(df_prueba, input_clear)
            print(output_clear)
            strings.append(output_clear)
    """

    #print(df_prueba)
    #create_csv(filename_e3c='clinentity.csv', fields_e3c=['begin', 'end', 'CLINENTITY'])
    #df_prueba.to_csv('clinentity.csv')

#------EXTRACT_TLINKS()-----#
def extract_tlinks():
    

    False      

#------EXTRACT_TIMEX3-----#
"""
Extrae las expresiones temporales del XML
-La clase que corresponde a las relaciones temporales tiene un campo específico, llamado timex3Class que puede tomar unos valores limitados, 
determinados por los autores. Por lo que se puede utilizar esto para filtrar de un dataframe directamente sin tener que hacer el tratado
que se hace para extraer los eventos.
"""
def extract_timex3(file):
    path = PATH + file
    print(file)
    df = pd.read_xml(path)
    df_time = pd.DataFrame(df, columns= ['id','begin','end','timex3Class', 'value', 'timexLink'])
    df_time = df_time.loc[df_time['timex3Class'].isin(['DATE', 'TIME', 'DURATION', 'QUANTIFIER', 'SET', 'PREPOSTEXP', 'DOCTIME', 'DOCTIME'])]    
    df_time = df_time.fillna(0)
    print(df_time)
    input_clear = extract_text(file)
    output_clear = extract_expresions(df_time, input_clear)

    write_timex_to_csv(file, df_time['id'], output_clear, df_time['begin'], df_time['end'], df_time['value'], df_time['timex3Class'], df_time['timexLink']) 

def extract_timex3_con_tlink(file):
  False

def extract_text_to_csv(filename):
       
    rows = []
    files = []
    for file in  os.listdir(PATH):
        row = [str(file), str(extract_text(file))]
        rows.append(row)
    
    with open(filename, 'a') as csvfile: 
        #creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        #writing the data rows 
        csvwriter.writerows(rows)


    False

#------WRITE_TIMEX_TO_CSV()-----#
"""
Escribe en un CSV las expresiones y distintos valores relacionados
-output_clear es una lista con todas las expresiones, por lo que hay que separarlas de 1 en 1
y emparejarlas con su begin, end, value y class, como vienen en orden no pasa nada.
"""
#Cambiar begin, end, etc por una lista para poder reutilizarlo
def write_timex_to_csv(file, id, output_clear, begin, end, value, timex3Class, tlink):
    rows = []
    file_dest = '/Users/asdc/Proyectos/time_line_extraction/time_expresions.csv'
    #Generates the rows for the csv
    for id_, beg, end_, val, timex3, output, tlink_ in zip(id, begin, end, value, timex3Class, output_clear, tlink):
        row = [str(file), str(int(id_)), str(output), str(int(beg)), str(int(end_)), str(val), str(timex3), str(tlink_)]
        rows.append(row)
    # writing to csv file 
    with open(file_dest, 'a') as csvfile: 
        #creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        #writing the data rows 
        csvwriter.writerows(rows)

#------WRITE_EVENTS_TO_CSV()-----#
def write_events_to_csv(file, id_event, output_clear, begin, end, ALINK, TLINK, contextualAspect, contextualModality, degree, docTimeRel, eventType, permanence, polarity):
    file_output = '/Users/asdc/Proyectos/time_line_extraction/events.csv'
    rows = []

    for begin_, end_, id_event_, ALINK_, TLINK_, contextualAspect_, contextualModality_, degree_, docTimeRel_, eventType_, permanence_, polarity_, output in zip(begin, end, id_event, ALINK, TLINK, contextualAspect, contextualModality, degree, docTimeRel, eventType, permanence, polarity, output_clear):
        row = [str(file), str(int(id_event_)), str(output), str(int(begin_)), str(int(end_)), str(ALINK_), str(TLINK_), str(contextualAspect_), str(contextualModality_), str(degree_), str(docTimeRel_), str(eventType_), str(permanence_), str(polarity_)]
        rows.append(row)
    # writing to csv file 
    with open(file_output, 'a') as csvfile: 
        #creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        #writing the data rows 
        csvwriter.writerows(rows)


#------WRITE_CLINENTITY_TO_CSV()-----#
def write_clinentity_to_csv(file, output_clear, begin, end, clinentity):
    rows = []
    file_output = '/Users/asdc/Proyectos/time_line_extraction/clinentity.csv'
    #Generates the rows for the csv
    for beg, end_, clinentity_, output in zip(begin, end, clinentity, output_clear):
        row = [str(file), str(output), str(int(beg)), str(int(end_)), str(clinentity_)]
        rows.append(row)
    # writing to csv file 
    with open(file_output, 'a') as csvfile: 
        #creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        #writing the data rows 
        csvwriter.writerows(rows)

#------WRITE_TLINKS_TO_CSV()-----#
def write_tlink_to_csv():
    False

#------CREATE_CSV()-----#
"""
Crea un csv según los parametros definidos en las constantes globales
"""
def create_csv(filename_e3c, fields_e3c):

    with open(filename_e3c, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the FIELDS_E3C 
        csvwriter.writerow(fields_e3c) 


#------HEIDELTIME()-----#
"""
Extrae el texto y el nombre del fichero de inputs_clear.csv y crea las anotaciones de heidel para textos narrativos en español en la carpeta data_annotation_heidel. 
Un fichero para cada texto con el mismo nombre que tiene en el corpus del E3C.
"""
def heidelTime():

    
    df = pd.read_csv('/Users/asdc/Proyectos/time_line_extraction/inputs_clear.csv')
    
    heideltime_parser = Heideltime()
    heideltime_parser.set_output_type('XMI')
    heideltime_parser.set_language('SPANISH')
    heideltime_parser.set_document_type('NARRATIVES')

    for file_name, input_clear in zip(df.file, df.input_clear):
        output_clear= heideltime_parser.parse(input_clear)
        myfile = open('/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation_heidel/' + file_name, "w")
        myfile.write(output_clear)


#------TRANSFORM_HEIDEL()-----#
"""
Extrae las expresiones temporales según las anotaciones timex3 que saca heideltime. Las clases son 'timexType' y los valores 'timexValue'
El heidel saca anotaciones más completas sobre las expresiones, pero en las anotaciones del E3C no hay más detalle, así que no vale para nada.
"""
def transform_heidel():
    
    file_output = '/Users/asdc/Proyectos/time_line_extraction/time_expresions_heidel.csv'
    create_csv(filename_e3c=file_output, fields_e3c=['file','string','begin','end','value','timex3Class'])

    for file in  os.listdir(PATH_HEIDEL):        
        df = pd.read_xml(PATH_HEIDEL + file)
        df_time = pd.DataFrame(df, columns= ['begin','end','timexType', 'timexValue'])
        df_time = df_time.loc[df_time['timexType'].isin(['DATE', 'TIME', 'DURATION', 'QUANTIFIER', 'SET', 'PREPOSTEXP', 'DOCTIME', 'DOCTIME'])]
        
        input_clear = df.loc[df['id'] == 1]
        input_clear = input_clear['sofaString']
        input_clear = input_clear.values[0]

        output_clear = extract_expresions(df_time, input_clear)

        write_timex_to_csv(file_output, file, output_clear, df_time['begin'], df_time['end'], df_time['timexValue'], df_time['timexType'])  


# 1º) Sacar el string de cada token
# 2º) Sacar si el string es o no un evento:
#   -Sacar el bgin y el end de tokens y eventos
#       -Se recorre la lista de eventos sobre la lista de tokens, for_eventos for_tokens (menor fuera grande dentro)
#       -Si coinciden el token se apunta como evento si no no
# columna1: token; columna2: type
# si evento -> type = 1; else -> type = 0

def get_tokens_events():
    abs_path = '/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation/Spanish/layer1/'
    file_output = '/Users/asdc/Proyectos/time_line_extraction/tokens_event_tagged.csv'
    create_csv(filename_e3c=file_output, fields_e3c=['file', 'string', 'begin', 'end', 'tag'])
    #create_csv(filename_e3c=file_output, fields_e3c=['string', 'begin', 'end', 'tag'])
    for file in  os.listdir(abs_path): 
        path = abs_path + file
        if path != abs_path + '.DS_Store':
            df = pd.read_xml(path)
            """
            input_id = df.loc[df['id'] == 1]
            input_id = input_id['sofa']
            input_id = int(input_id.values[0])


            input_ = df.loc[df['id'] == input_id]
            input_ = input_['sofaString']
            """
            beginings_token = []
            endings_token = []
            tokens = []
            beginings_events = []
            endings_events = []
            events = []
            for _, string in ET.iterparse(path):
                if string.tag == '{http:///uima/cas.ecore}Sofa':
                    input_ = string.attrib['sofaString']
            for _, token in ET.iterparse(path): 
                if token.tag == '{http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore}Token':
                    beginings_token.append(token.attrib['begin'])
                    endings_token.append(token.attrib['end'])
                    tokens.append(input_[int(token.attrib['begin']):int(token.attrib['end'])])

                if token.tag == '{http:///webanno/custom.ecore}EVENT':
                    beginings_events.append(token.attrib['begin'])
                    endings_events.append(token.attrib['end'])
                    events.append(input_[int(token.attrib['begin']):int(token.attrib['end'])])

            tags_pos = []
            tags = []
            """
            beginings_token_ = beginings_token
            for begin_event in beginings_events:
                for begin_token in beginings_token_:
                    if begin_token == begin_event:
                        tags.append(1)
                        #beginings_token_.pop(0)
                        beginings_token_ = beginings_token_[1:]
                    else:
                        tags.append(0)
                        beginings_token_.pop(0)
                        beginings_token_ = beginings_token_[1:]
            """

            for begin_event in beginings_events:
                i = 0 
                while i in range (len(beginings_token)):
                    if beginings_token[i] == begin_event:
                        tags_pos.append(i)
                    i+=1
            j = 0
            while j in range (len(beginings_token)):
                if j in tags_pos:
                    tags.append(1)
                else:
                    tags.append(0)
                j += 1
            #print(tokens)
            #print(beginings_events)
            rows = [[file, tokens, beginings_token, endings_token, tags]]
            #rows.append(file)
            
            df_row = pd.DataFrame(rows, columns = ['file','string', 'begin', 'end', 'tag'])
            print(rows)
            #print(df_row)
            #df_row.to_csv('tokens_event_tagged.csv', mode = 'a', index = False, header=False)
            


            #Generates the rows for the csv
            """
            for beg, end_, tag, output in zip(beginings_token, endings_token, tags, tokens):
                row = [str(file), str(output), str(int(beg)), str(int(end_)), str(tag)]
                rows.append(row)
            

            # writing to csv file 
            with open(file_output, 'a') as csvfile: 
                #creating a csv writer object 
                csvwriter = csv.writer(csvfile) 
                    
                #writing the data rows 
                csvwriter.writerows(rows)
            """

def train_test():
    df = pd.read_csv('tokens_event_tagged.csv')
    list_test = ['ES100001.xml', 'ES100002.xml', 'ES100030.xml', 'ES100042.xml', 'ES100079.xml', 'ES100143.xml', 'ES100163.xml', 'ES100178.xml', 'ES100214.xml', 'ES100363.xml', 'ES100410.xml', 'ES100412.xml', 'ES100417.xml', 'ES100445.xml', 'ES100513.xml', 'ES100526.xml', 'ES100569.xml', 'ES100594.xml', 'ES100634.xml', 'ES100642.xml', 'ES100686.xml', 'ES100688.xml', 'ES100705.xml', 'ES100713.xml', 'ES100715.xml', 'ES100727.xml', 'ES100737.xml', 'ES100775.xml', 'ES100778.xml', 'ES100803.xml', 'ES100819.xml', 'ES100832.xml', 'ES100840.xml', 'ES100848.xml', 'ES100937.xml', 'ES100947.xml']
    
    list_train = ['ES100214.xml','ES100445.xml', 'ES100513.xml', 'ES100526.xml', 'ES100569.xml', 'ES100594.xml', 'ES100634.xml', 'ES100642.xml', 'ES100686.xml', 'ES100688.xml', 'ES100705.xml', 'ES100713.xml', 'ES100715.xml', 'ES100727.xml', 'ES100737.xml', 'ES100775.xml', 'ES100778.xml', 'ES100803.xml', 'ES100819.xml', 'ES100832.xml', 'ES100840.xml', 'ES100848.xml', 'ES100937.xml', 'ES100947.xml']
    
    list_dev = ['ES100001.xml', 'ES100002.xml', 'ES100030.xml', 'ES100042.xml', 'ES100079.xml', 'ES100143.xml', 'ES100163.xml', 'ES100178.xml',  'ES100363.xml', 'ES100410.xml', 'ES100412.xml', 'ES100417.xml']
    #df_train = df[df['file'] isin list]
    df_filter = df['file'].isin(list_train)
    df_train = df[df_filter]
    df_filter = ~df['file'].isin(list_test)
    df_test = df[df_filter]
    df_filter = df['file'].isin(list_dev)
    df_dev = df[df_filter]
    #print(len(df_train))
    #print(len(df_test))
    #print(len(df))
    df_train.to_csv('events_train.csv',index = False)
    df_test.to_csv('events_test.csv',index = False)
    df_dev.to_csv('events_dev.csv', index = False)
    #df_comprobar = pd.read_csv('events_train.csv')
    #df_comprobar_ = pd.to_numeric(df_comprobar['tag'])
    #df_comprobar_ = df_comprobar['tag'].astype(str).astype(int)
    #print(df_comprobar_.dtypes)

def numero_tokens_train_test():
    df_train = pd.read_csv('events_train.csv', converters={'string': ast.literal_eval, 'tag': ast.literal_eval, 'begin': ast.literal_eval, 'end': ast.literal_eval})
    df_test = pd.read_csv('events_test.csv', converters={'string': ast.literal_eval, 'tag': ast.literal_eval, 'begin': ast.literal_eval, 'end': ast.literal_eval})
    df_dev = pd.read_csv('events_dev.csv', converters={'string': ast.literal_eval, 'tag': ast.literal_eval, 'begin': ast.literal_eval, 'end': ast.literal_eval})
    df_todo = pd.read_csv('tokens_event_tagged.csv', converters={'string': ast.literal_eval, 'tag': ast.literal_eval, 'begin': ast.literal_eval, 'end': ast.literal_eval})
    list_train = df_train['string'].tolist()
    
    #Saca el número de tokens del conjunto train sacando el número de strings que hay por documento
    tokens_train = 0
    for i in list_train:
        tokens_train+=len(i)
        #Saca el número de tokens por documento
        #print(len(i))
    print(tokens_train)

    #Saca el número de tokens del conjunto test sacando el número de strings que hay por documento
    
    tokens_test = 0
    list_test = df_test['string'].tolist()
    for i in list_test:
        tokens_test+=len(i)
    print(tokens_test)
    
    
    #Saca el número de tokens del conjunto dev sacando el número de strings que hay por documento
    list_dev = df_dev['string'].tolist()
    tokens_dev = 0
    for j in list_dev:
        tokens_dev+=len(j)
        #Saca el número de tokens por documento
        #print(len(j))
    print(tokens_dev)

    print(df_todo.columns)
    
    #Saca el número de documentos por conjunto
    #print(len(df_train['file']))
    #print(len(df_dev['file']))

def sacar_eventos_total():
    abs_path = '/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation/Spanish/layer1/'
    create_csv(filename_e3c='eventos_sentence_completo.csv', fields_e3c=['file','id_event','begin_event','end_event','tlink','alink','contextualAspect','contextualModality','degree','docTimeRel','eventType','permanence','polarity','id_sentence', 'begin_sentence', 'end_sentence','id_timex', 'begin_timex', 'end_timex', 'tlink_timex'])
    create_csv(filename_e3c='timex_completo.csv', fields_e3c=['file','id', 'begin', 'end'])
    create_csv(filename_e3c='sentence_completo.csv', fields_e3c=['file','id', 'begin', 'end'])
    create_csv(filename_e3c='tlink_completo.csv', fields_e3c=['file','id', 'type', 'role', 'target'])
    for file in  os.listdir(abs_path): 
        path = abs_path + file     
        if path != abs_path + '.DS_Store':        
            df = pd.read_xml(path)
            id = []
            id_timex = []
            id_sentence = []
            id_tlink = []
            role_tlink = []
            target_tlink = []
            type_tlink = []
            begin = []
            begin_timex = []
            begin_sentence = []
            end = []
            end_timex = []
            end_sentence = []
            tlink = []
            tlink_timex = []
            alink = []
            contextualAspect = []
            contextualModality = []
            degree = []
            docTimeRel = []
            eventType = []
            permanence = []
            polarity = []
            for _, token in ET.iterparse(path): 
                #print(token)
                #Guarda los eventos
                if token.tag == '{http:///webanno/custom.ecore}EVENT':
                    #Hay eventos que no tienen TLINK y/o ALINK
                    if ('TLINK' in token.attrib) and ('ALINK' in token.attrib):
                        #print(token.attrib)
                        id.append(token.attrib['{http://www.omg.org/XMI}id'])
                        begin.append(token.attrib['begin'])
                        end.append(token.attrib['end'])
                        tlink.append(token.attrib['TLINK'])
                        alink.append(token.attrib['ALINK'])
                        contextualAspect.append(token.attrib['contextualAspect'])
                        contextualModality.append(token.attrib['contextualModality'])
                        degree.append(token.attrib['degree'])
                        docTimeRel.append(token.attrib['docTimeRel'])
                        eventType.append(token.attrib['eventType'])
                        permanence .append(token.attrib['permanence'])
                        polarity.append(token.attrib['polarity'])

                    else:
                        #print(token.attrib)
                        id.append(token.attrib['{http://www.omg.org/XMI}id'])
                        begin.append(token.attrib['begin'])
                        end.append(token.attrib['end'])
                        tlink.append('')
                        alink.append('')
                        contextualAspect.append(token.attrib['contextualAspect'])
                        contextualModality.append(token.attrib['contextualModality'])
                        degree.append(token.attrib['degree'])
                        docTimeRel.append(token.attrib['docTimeRel'])
                        eventType.append(token.attrib['eventType'])
                        permanence .append(token.attrib['permanence'])
                        polarity.append(token.attrib['polarity'])
                #Guarda los timex
                if  token.tag == '{http:///webanno/custom.ecore}TIMEX3':
                    if 'timexLink' in token.attrib:
                        id_timex.append(token.attrib['{http://www.omg.org/XMI}id'])
                        begin_timex.append(token.attrib['begin'])
                        end_timex.append(token.attrib['end'])
                        tlink_timex.append(token.attrib['timexLink'])
                    else: 
                        id_timex.append(token.attrib['{http://www.omg.org/XMI}id'])
                        begin_timex.append(token.attrib['begin'])
                        end_timex.append(token.attrib['end'])
                        tlink_timex.append('')
                    
                if  token.tag == '{http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore}Sentence':
                    id_sentence.append(token.attrib['{http://www.omg.org/XMI}id'])
                    begin_sentence.append(token.attrib['begin'])
                    end_sentence.append(token.attrib['end'])
                if token.tag == '{http:///webanno/custom.ecore}EVENTTLINKLink' or token.tag == '{http:///webanno/custom.ecore}TIMEX3TimexLinkLink':
                    id_tlink.append(token.attrib['{http://www.omg.org/XMI}id'])
                    role_tlink.append(token.attrib['role'])
                    target_tlink.append(token.attrib['target'])
                    if token.tag == '{http:///webanno/custom.ecore}EVENTTLINKLink':
                        type_tlink.append('EVENTTLINKLink')
                    else: 
                        type_tlink.append('TIMEX3TimexLinkLink')
            #Escribe eventos y sentence
            rows = [[file, id, begin, end, tlink, alink, contextualAspect,contextualModality,degree,docTimeRel,eventType,permanence,polarity, id_sentence, begin_sentence, end_sentence, id_timex, begin_timex, end_timex, tlink_timex]]
            df_row = pd.DataFrame(rows, columns = ['file','id_event','begin_event','end_event','tlink_event', 'alink','contextualAspect','contextualModality','degree','docTimeRel','eventType','permanence','polarity', 'id_sentence', 'begin_sentence', 'end_sentence', 'id_timex', 'begin_timex', 'end_timex', 'tlink_timex'])
            df_row.to_csv('eventos_sentence_completo.csv', mode = 'a', index = False, header=False)
            #Escribe expresiones temporales
            rows_timex = [[file, id_timex, begin_timex, end_timex]]
            df_row_timex = pd.DataFrame(rows_timex, columns=['file', 'id', 'begin', 'end'])
            df_row_timex.to_csv('timex_completo.csv', mode='a', index=False, header=False)
            #Escribe sentences
            rows_timex = [[file, id_sentence, begin_sentence, end_sentence]]
            df_row_timex = pd.DataFrame(rows_timex, columns=['file', 'id', 'begin', 'end'])
            df_row_timex.to_csv('sentence_completo.csv', mode='a', index=False, header=False)
            #Escribe tlinks
           
            for id_tlink_, type_tlink_, role_tlink_, target_tlink_ in zip(id_tlink, type_tlink, role_tlink, target_tlink):
                df_row_timex
                rows_timex = [[file, id_tlink_, type_tlink_, role_tlink_, target_tlink_]]
                df_row_timex = pd.DataFrame(rows_timex, columns=['file','id', 'type', 'role', 'target'])
                df_row_timex.to_csv('tlink_completo.csv', mode='a', index=False, header=False)

            
def estadísticas_eventos():
    df_eventos = pd.read_csv('prueba.csv')

    print('----------contextualAspect----------')
    contextual_aspect = df_eventos['contextualAspect'].unique().tolist()
    print(contextual_aspect)
    
    for i in contextual_aspect:
        print(i)
        if isinstance(i, float):
            if math.isnan(i):
                print(len(df_eventos['contextualAspect'].isnull()))
        else:
            print(len(df_eventos[df_eventos['contextualAspect'] == i]))
    
    print()

    print('----------contextualModality----------')
    contextual_modality = df_eventos['contextualModality'].unique()
    print(contextual_modality)
    for i in contextual_modality:
        print(i)
        if isinstance(i, float):
            if math.isnan(i):
                print(len(df_eventos['contextualModality'].isnull()))
        else:
            print(len(df_eventos[df_eventos['contextualModality'] == i]))

    print()

    
    print('----------Degree----------')
    degree = df_eventos['degree'].unique()
    print(degree)
    for i in degree:
        print(i)
        if isinstance(i, float):
            if math.isnan(i):
                print(len(df_eventos['degree'].isnull()))
        else:
            print(len(df_eventos[df_eventos['degree'] == i]))
    print()
    
    print('----------docTimeRel----------')
    docTimeRel = df_eventos['docTimeRel'].unique()
    print(docTimeRel)
    for i in docTimeRel:
        print(i)
        if isinstance(i, float):
            if math.isnan(i):
                print(len(df_eventos['docTimeRel'].isnull()))
        else:
            print(len(df_eventos[df_eventos['docTimeRel'] == i]))
    print()
    
    print('----------eventType----------')
    eventType = df_eventos['eventType'].unique()
    print(eventType)
    for i in eventType:
        print(i)
        if isinstance(i, float):
            if math.isnan(i):
                print(len(df_eventos['eventType'].isnull()))
        else:
            print(len(df_eventos[df_eventos['eventType'] == i]))
    print()
    
    print('----------Permanence----------')
    permanence = df_eventos['permanence'].unique()
    print(permanence)
    for i in permanence:
        print(i)
        if isinstance(i, float):
            if math.isnan(i):
                print(len(df_eventos['permanence'].isnull()))
        else:
            print(len(df_eventos[df_eventos['permanence'] == i]))
    print()

    print('----------Polarity----------')
    polarity = df_eventos['polarity'].unique()
    print(polarity)
    for i in polarity:
        print(i)
        if isinstance(i, float):
            if math.isnan(i):
                print(len(df_eventos['polarity'].isnull()))
        else:
            print(len(df_eventos[df_eventos['polarity'] == i]))
    print()


def get_event_timex_pairs():
    
    create_csv('event_timex_pairs.csv',['file', 'id_sentence', 'sentence_begin', 'sentence_end', 'link', 'pairs_events'])
    create_csv('sentences_no_pairs.csv',['file', 'id_sentence', 'sentence_begin', 'sentence_end', 'link', 'pairs_events'])
    
    df_event = pd.read_csv('eventos_completo.csv', converters={'id': ast.literal_eval, 'begin': ast.literal_eval, 'end': ast.literal_eval})
    df_timex = pd.read_csv('timex_completo.csv', converters={'id': ast.literal_eval, 'begin': ast.literal_eval, 'end': ast.literal_eval})
    df_sentence = pd.read_csv('sentence_completo.csv', converters={'id': ast.literal_eval, 'begin': ast.literal_eval, 'end': ast.literal_eval})
    df_event_sentence = pd.read_csv('eventos_sentence_completo.csv', converters={'id_event': ast.literal_eval, 'begin_event': ast.literal_eval, 'end_event': ast.literal_eval, 'id_sentence': ast.literal_eval, 'begin_sentence': ast.literal_eval, 'end_sentence': ast.literal_eval, 'id_timex': ast.literal_eval, 'begin_timex': ast.literal_eval, 'end_timex': ast.literal_eval})
    
    #pairs_act_event = []
    #pairs_act_timex = []
    #eventos_borrar = []
    #timex_borrar = []
    
    #Sacar parejas
    for index_, row in df_event_sentence.iterrows():
        pairs_act_event = []
        pairs_act_timex = []
        eventos_borrar = []
        timex_borrar = []
        #for index_event, event_row in df_event.iterrows():
        for (sentence_id, sentence_begin, sentence_end) in zip(row['id_sentence'], row['begin_sentence'], row['end_sentence']):               
            pairs_act_event.clear()
            #Borrar los eventos que ya se han visitado 
            
            if len(eventos_borrar)>0:
                row['id_event'] = row['id_event'][len(eventos_borrar):]
                row['begin_event'] = row['begin_event'][len(eventos_borrar):]
                row['end_event'] = row['end_event'][len(eventos_borrar):]
            if len(timex_borrar)>0:
                row['id_timex'] = row['id_timex'][len(timex_borrar):]
                row['begin_timex'] = row['begin_timex'][len(timex_borrar):]
                row['end_timex'] = row['end_timex'][len(timex_borrar):]
            #Resetear la lista de eventos visitados
            eventos_borrar.clear()
            timex_borrar.clear()
            
            #Para cada evento, emparejarle con todos los eventos de su misma sentence
            for (event_id, event_begin, event_end) in zip(row['id_event'], row['begin_event'], row['end_event']):
                #Si el evento no pertenece a la sentence actual se pasa de sentence(break)
                if int(event_end) > int(sentence_end):
                        break
                for (event_id_copia, event_begin_copia, event_end_copia) in zip(row['id_event'], row['begin_event'], row['end_event']):
                    #Si son el mismo evento no se guarda la pareja
                    if event_id_copia != event_id:
                        #Si el evento con el que se quiere emparejar está en la misma sentence se guarda si no se pasa al siguiente evento(break)
                        if int(event_end_copia) <= int(sentence_end):
                            #print('(' + event_id  + ',' + event_id_copia + ')')
                            pairs_act_event.append([event_id, event_id_copia])
                            #Si el evento ya se había guardado antes como parte principal de la pareja no se vuelve a guardar para borrar
                            if event_id not in eventos_borrar:
                                eventos_borrar.append(event_id)
                        else: 
                            break
                for (timex_id_copia, timex_begin_copia, timex_end_copia) in zip(row['id_timex'], row['begin_timex'], row['end_timex']):
                    #Si son el mismo evento no se guarda la pareja
                    if timex_id_copia != event_id:
                        #Si el evento con el que se quiere emparejar está en la misma sentence se guarda si no se pasa al siguiente evento(break)
                        if int(timex_end_copia) <= int(sentence_end):
                            pairs_act_event.append([event_id, timex_id_copia])
                            #Si el evento ya se había guardado antes como parte principal de la pareja no se vuelve a guardar para borrar
                            if timex_id_copia not in timex_borrar:
                                timex_borrar.append(timex_id_copia)
                            if event_id not in eventos_borrar:
                                eventos_borrar.append(event_id)
                        else: 
                            break
                
            df_temp = pd.DataFrame([[row['file'], sentence_id, sentence_begin, sentence_end, 'EVENTTLINKLink', pairs_act_event]], columns=['file', 'id_sentence', 'sentence_begin', 'sentence_end', 'link', 'pairs_events'])
            
            if len(pairs_act_event) > 0:
                 df_temp.to_csv('event_timex_pairs.csv', mode='a', header=False, index=False)
            else:
                df_temp.to_csv('sentences_no_pairs.csv', mode='a', header=False, index=False)
    
    df_event_sentence = pd.read_csv('eventos_sentence_completo.csv', converters={'id_event': ast.literal_eval, 'begin_event': ast.literal_eval, 'end_event': ast.literal_eval, 'id_sentence': ast.literal_eval, 'begin_sentence': ast.literal_eval, 'end_sentence': ast.literal_eval, 'id_timex': ast.literal_eval, 'begin_timex': ast.literal_eval, 'end_timex': ast.literal_eval})
    
    #pairs_act_event = []
    #pairs_act_timex = []
    #eventos_borrar = []
    #timex_borrar = []

    #Sacar parejas
    for index_, row in df_event_sentence.iterrows():
        pairs_act_event = []
        pairs_act_timex = []
        eventos_borrar = []
        timex_borrar = []
        for (sentence_id, sentence_begin, sentence_end) in zip(row['id_sentence'], row['begin_sentence'], row['end_sentence']):               
            #Borrar los eventos que ya se han visitado 
            #print(timex_borrar)
            if len(eventos_borrar)>0:
                row['id_event'] = row['id_event'][len(eventos_borrar):]
                row['begin_event'] = row['begin_event'][len(eventos_borrar):]
                row['end_event'] = row['end_event'][len(eventos_borrar):]
            if len(timex_borrar)>0:
                row['id_timex'] = row['id_timex'][len(timex_borrar):]
                row['begin_timex'] = row['begin_timex'][len(timex_borrar):]
                row['end_timex'] = row['end_timex'][len(timex_borrar):]
            #Resetear la lista de eventos visitados
            eventos_borrar.clear()
            timex_borrar.clear()
            pairs_act_timex.clear()
            #Para cada evento, emparejarle con todos los eventos de su misma sentence
            for (timex_id, timex_begin, timex_end) in zip(row['id_timex'], row['begin_timex'], row['end_timex']):
                #Si el evento no pertenece a la sentence actual se pasa de sentence(break)
                if int(timex_end) > int(sentence_end):
                        break
                for (event_id_copia, event_begin_copia, event_end_copia) in zip(row['id_event'], row['begin_event'], row['end_event']):
                    #Si son el mismo evento no se guarda la pareja
                    if event_id_copia != timex_id:
                        #Si el evento con el que se quiere emparejar está en la misma sentence se guarda si no se pasa al siguiente evento(break)
                        if int(event_end_copia) <= int(sentence_end):
                            #print('(' + event_id  + ',' + event_id_copia + ')')
                            pairs_act_timex.append([timex_id, event_id_copia])
                            #Si el evento ya se había guardado antes como parte principal de la pareja no se vuelve a guardar para borrar
                            if event_id_copia not in eventos_borrar:
                                eventos_borrar.append(event_id_copia)
                            if timex_id not in timex_borrar:
                                #print(sentence_id)
                                timex_borrar.append(timex_id)
                        else: 
                            break
                for (timex_id_copia, timex_begin_copia, timex_end_copia) in zip(row['id_timex'], row['begin_timex'], row['end_timex']):
                    #Si son el mismo evento no se guarda la pareja
                    if timex_id_copia != timex_id:
                        #Si el evento con el que se quiere emparejar está en la misma sentence se guarda si no se pasa al siguiente evento(break)
                        if int(timex_end_copia) <= int(sentence_end):
                            pairs_act_timex.append([timex_id, timex_id_copia])
                            #Si el evento ya se había guardado antes como parte principal de la pareja no se vuelve a guardar para borrar
                            #print(timex_borrar)
                            if timex_id not in timex_borrar:
                                #print(sentence_id)
                                timex_borrar.append(timex_id)
                        else: 
                            break
            df_temp = pd.DataFrame([[row['file'], sentence_id, sentence_begin, sentence_end, 'TIMEX3TimexLinkLink', pairs_act_timex]], columns=['file', 'id_sentence', 'sentence_begin', 'sentence_end','link', 'pairs_events'])
            if len(pairs_act_timex) > 0:
                df_temp.to_csv('event_timex_pairs.csv', mode='a', header=False, index=False)
            else: 
                df_temp.to_csv('sentences_no_pairs.csv', mode='a', header=False, index=False)
                
    
    #Asignar tags

def get_tlink():
    create_csv('pairs_tlink_tagged.csv', ['file', 'id_tlink', 'id_pairs', 'role', 'type'])
    df_events_con_tlink = pd.read_csv('events_conTLINK.csv')
    df_timex_completo = pd.read_csv('time_expresions.csv')
    df_tlink_completo = pd.read_csv('tlink_completo.csv')

    #print(df_tlink_completo[df_tlink_completo['id'] == 5546])
    #print(df_events_con_tlink[df_events_con_tlink['file'] == 'ES100447.xml'])
    pairs = []
    

    #df_events_con_tlink = df_events_con_tlink[df_events_con_tlink['file'] == 'ES100447.xml']
    for index, row in df_events_con_tlink.iterrows():
        tlinks = row['TLINK'].split()
        tlinks_ = list(map(int, tlinks))
        for tlink in tlinks_: 
            pairs.clear()
            tl = df_tlink_completo[(df_tlink_completo['id'] == tlink) & (df_tlink_completo['file'] == row['file'])]
            #print(role)
            pairs.append(row['id_event'])
            pairs.append(tl['target'].values[0])
            row_store = [row['file'], tlink, pairs, tl['role'].values[0], tl['type'].values[0]]
            #print(row_store)
            df_row = pd.DataFrame([row_store], columns=['file', 'id_tlink', 'id_pairs', 'role', 'type'])
            df_row.to_csv('pairs_tlink_tagged.csv', mode='a', header=False, index=False)
        #print(pairs)
    
    df_timex_con_tlink = df_timex_completo[df_timex_completo['timexLink'] != '0']
    for index, row in df_timex_con_tlink.iterrows():
        tlinks = row['timexLink'].split()
        tlinks_ = list(map(int, tlinks))
        print(row['file'])
        print(tlinks_)
        for tlink in tlinks_: 
            pairs.clear()
            tl = df_tlink_completo[(df_tlink_completo['id'] == tlink) & (df_tlink_completo['file'] == row['file'])]
            #print(role)
            pairs.append(row['id'])
            pairs.append(tl['target'].values[0])
            row_store = [row['file'], tlink, pairs, tl['role'].values[0], tl['type'].values[0]]
            #print(row_store)
            df_row = pd.DataFrame([row_store], columns=['file', 'id_tlink', 'id_pairs', 'role', 'type'])
            df_row.to_csv('pairs_tlink_tagged.csv', mode='a', header=False, index=False)
        #print(pairs)
    
#Sacar las parejas que tienen tlink (y cuál) y las parejas que no. 
#Reducir el número de parejas que NO tienen enlace en proporción 45 sí 55 no o 40/60
#CSV con: String_sentence, id_sentence, pair, type_relation, role(0 nada, 1 before, etc.). 
def pairs_tagged():
    df_pairs_tagged = pd.read_csv('pairs_tlink_tagged.csv', converters={'id_pairs': ast.literal_eval})
    df_pairs_untagged = pd.read_csv('event_timex_pairs.csv', converters={'pairs_events': ast.literal_eval})
    
    #print(type(df_pairs_untagged_full.iloc[11]['pairs_events']))
    
    columnas = ['file', 'id_sentence', 'id_tlink', 'pair', 'role', 'type']
    create_csv('events_timex_pairs_tagged.csv', columnas)
    #Recorro todas las líneas de parejas de eventos
    for index_untagged, row_untagged in df_pairs_untagged.iterrows():
        #Cada línea es un documento. Así que para cada documento miro todas las combinaciones de parejas a ver cuáles tienen enlace.
        pairs_events = row_untagged['pairs_events']
        #Recorro las parejas del documento una a una
        for pair in pairs_events:
            pair_ = []
            pair_.append(int(pair[0]))
            pair_.append(int(pair[1]))
            df_pairs_tagged_act = df_pairs_tagged[df_pairs_tagged['file'] == row_untagged['file']]#['id_pairs'].values.tolist()
            #Miro a ver si la pareja está en la lista de parejas con enlace
            #df_row = pd.DataFrame(columns=columnas)
            df_row = pd.DataFrame(columns=columnas)
            for index_tagged, row_tagged in df_pairs_tagged_act.iterrows():
                if row_tagged['id_pairs'] == pair_:
                    df_row = pd.DataFrame([[row_tagged['file'], row_untagged['id_sentence'], row_tagged['id_tlink'], np.array(pair_), row_tagged['role'], row_tagged['type']]], columns=columnas)
                    #Si la pareja tiene enlace dejo de buscar
                    break
            #Si no lo he guardado lo guardo (la pareja actual), porque ya he recorrido todas las parejas con enlace
            if df_row.empty:
                df_row = pd.DataFrame([[row_tagged['file'], row_untagged['id_sentence'], -1, np.array(pair_), -1, row_tagged['type']]], columns=columnas)
            df_row.to_csv('events_timex_pairs_tagged.csv', header=False, mode='a', index=False)
    
def sentence_strings():
    create_csv('sentence_strings.csv', ['file','id_sentence','string_sentence', 'begin', 'end'])
    for file in  os.listdir(PATH):
        if file != '.DS_Store':
            path = PATH + file
            for _, string in ET.iterparse(path):
                if string.tag == '{http:///uima/cas.ecore}Sofa':
                    input_ = string.attrib['sofaString']
            for _, row in ET.iterparse(path):
                if row.tag == '{http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore}Sentence':
                    sentence = input_[int(row.attrib['begin']):int(row.attrib['end'])]
                    id_sentence = row.attrib['{http://www.omg.org/XMI}id']
                    df_row = pd.DataFrame([[file, id_sentence, str(sentence), row.attrib['begin'], row.attrib['end']]], columns=['file','id_sentence','string_sentence', 'begin', 'end'])
                    df_row.to_csv('sentence_strings.csv', mode='a', index=False, header=False)

def sentence_strings_con_pair():
    create_csv('sentence_strings_con_pair.csv', ['file', 'id_sentence', 'string_sentence', 'begin', 'end'])
    df_all_sentences = pd.read_csv('sentence_strings.csv')
    df_sentences_pair = pd.read_csv('event_timex_pairs.csv')
    #En event_timex_pairs se guardan todas las sentences que tienen eventos (con sus pares de eventos). Como se meten primero los tipo eventlink y luego los timexlink, hay sentences que están duplicadas. Por eso el tamaño es mayor al conjunto de sentences. Si se suman las sentences de tipo eventlink que hay ahí más las que no tienen enlace(sentences_no_pairs) da el número total. (Si se hace con timexlink da el mismo resultado). Por eso hay tantas frases que no tienen enlace, porque la mayoría no tienen timexlink. Hay que diferenciar a la hora de decir cuántas sentences tienen enlaces, entre cuáles tienen eventlink y cuales timexlink. 
    
    for index, row in df_sentences_pair.iterrows():
        row_sentence = df_all_sentences[(df_all_sentences['file'] == row['file']) & (df_all_sentences['id_sentence'] == row['id_sentence'])]
        string_sentence = row_sentence['string_sentence'].values[0]
        begin = row_sentence['begin'].values[0]
        end = row_sentence['end'].values[0]
        #print(string_sentence
        df_temp = pd.DataFrame([[row['file'], row['id_sentence'], string_sentence, begin, end]], columns=(['file', 'id_sentence', 'string_sentence', 'begin', 'end']))
        df_temp.to_csv('sentence_strings_con_pair.csv', mode='a', header=False, index=False)
        


#NO SÉ PORQUÉ SE DESCUADRA Y A VECES COGE FRASES Y LAS METE DONDE NO ES 
def pairs_tagged_string():
    #SE PUEDE MIRAR QUE SI EL EVENTO PRINCIPAL VA DESPUÉS QUE EL SEGUNDO EVENTO EN EL TEXTO NO SE DESORDENEN
    columnas = ['file', 'sentence', 'type', 'tag']
    create_csv('sentence_event_timex_tagged.csv', columnas)
    df_eventos = pd.read_csv('events_timex.csv')
    df_sentences = pd.read_csv('sentence_strings_con_pair.csv')
    df_pairs_tagged = pd.read_csv('events_timex_pairs_tagged.csv')
    df_strings = pd.read_csv('inputs_clear.csv')

    for index, row in df_pairs_tagged.iterrows():
        #e1_arr = np.array(row['pair'], dtype=np.int32)
        #Pasar de np array con el tipo [a b] a lista de enteros. Se quitan los [ ] y se split en los elementos que hay y se mapean cada uno a int y se meten en una lista
    
        e_arr = list(map(int, row['pair'].replace('[', '').replace(']', '').split()))
        e_1 = df_eventos[(df_eventos['file'] == row['file']) & (df_eventos['id'] == e_arr[0])]
        e_2 = df_eventos[(df_eventos['file'] == row['file']) & (df_eventos['id'] == e_arr[1])]
        e_begin = [e_1['begin'].values[0], e_2['begin'].values[0]]
        e_end = [e_1['end'].values[0], e_2['end'].values[0]]
        string_sentence_begin = df_sentences[(df_sentences['file'] == row['file']) & (df_sentences['id_sentence'] == row['id_sentence'])]['begin'].values[0]
        string_sentence_end = df_sentences[(df_sentences['file'] == row['file']) & (df_sentences['id_sentence'] == row['id_sentence'])]['end'].values[0]
        string_clear = df_strings[df_strings['file'] == row['file']]['input_clear'].values[0]
        #new_string_sentence = string_sentence[0:e_begin[0]] + '<t>' + string_sentence[e_begin[0]:e_end[0]] + '</t>' + string_sentence[e_end[0]:e_begin[1]] + '<t>' + string_sentence[e_begin[1]:e_end[1]] + '</t>' + string_sentence[e_end[1]:]
        new_string_sentence = string_clear[string_sentence_begin:e_begin[0]] + '<t>' + string_clear[e_begin[0]:e_end[0]] + '</t>' + string_clear[e_end[0]:e_begin[1]] + '<t>' + string_clear[e_begin[1]:e_end[1]] + '</t>' + string_clear[e_end[1]:string_sentence_end]
        #print(new_string_sentence)
        
        df_row = pd.DataFrame([[row['file'], new_string_sentence, row['type'], row['role']]], columns=columnas)
        df_row.to_csv('sentence_event_timex_tagged.csv', mode='a', header=False, index=False)

#HAY QUE LIMPIAR LAS SENTENCES QUE NO TIENEN EVENTOS Y EQUILIBRAR EL DATASET

def prueba():        
    df_train = pd.read_csv('dataset_link_train_DOS.csv')
    df_test = pd.read_csv('dataset_link_test_DOS.csv')
    df_dev = pd.read_csv('dataset_link_dev_DOS.csv')
    df = pd.read_csv('dataset_link_final_DOS.csv')

    uniques = df_train['labels'].unique()
    for unique in uniques:
        print(unique)
        print(len(df[df['labels'] == unique]))
    
    values_replace = ['-1', 'CONTAINS', 'OVERLAP', 'BEFORE', 'BEGINS-ON', 'ENDS-ON', 'SIMULTANEOUS']
    values = ['0', '1', '2', '3', '4', '5', '6']
    
    
    for unique in uniques:
        print(unique)
        print('TRAIN: ')
        print(len(df_train[df_train['labels'] == unique]))
        print('TEST: ')
        print(len(df_test[df_test['labels'] == unique]))
        print('DEV: ')
        print(len(df_dev[df_dev['labels'] == unique]))
        print()
    
    False

def get_events_timex():
    columnas = ['file','id','begin','end', 'type']
    create_csv('events_timex.csv', columnas)
    for file in  os.listdir(PATH):
        if file != '.DS_Store':
            path = PATH + file
            for event, elem in ET.iterparse(path):
                if elem.tag == '{http:///webanno/custom.ecore}TIMEX3':
                    row = [file, elem.attrib['{http://www.omg.org/XMI}id'], elem.attrib['begin'], elem.attrib['end'], 'TIMEX3']
                    df_row = pd.DataFrame([row], columns=columnas)
                    df_row.to_csv('events_timex.csv', columns=columnas, mode='a', header=False, index=False)
                if elem.tag == '{http:///webanno/custom.ecore}EVENT': 
                    row = [file, elem.attrib['{http://www.omg.org/XMI}id'], elem.attrib['begin'], elem.attrib['end'], 'EVENT']
                    df_row = pd.DataFrame([row], columns=columnas)
                    df_row.to_csv('events_timex.csv', columns=columnas, mode='a', header=False, index=False)

#GUARDAR UNA COPIA DEL DATASET CAMBIANDO LAS ETIQUETAS DEL TAG POR NÚMEROS (0-6) PARA LUEGO PODER PASARLO A INT Y QUE LO MAPEE EL CLASSLABEL
def clear_sentence_event_timex_tagged():
    #df = pd.read_csv('sentence_event_timex_tagged.csv')
    #Para generar el segundo dataset hay que partir del primero 
    df = pd.read_csv('dataset_link_final.csv')
    print(len(df[df['labels'] != 0]))
    print(len(df[df['labels'] == 0]))
    size_pos_neg = 24684 #Para reducir el dataset dejando 55% sin relación y 45% con 
    size_contains_no_relation =  4608 - 2287
    #QUITAR HASTA IGUALAR A CONTAIN Y LUEGO DIVIDIR EN TEST Y TRAIN OTRA VEZ
    to_remove = np.random.choice(df[df['labels']==0].index,size=size_contains_no_relation,replace=False)
    df_ = df.drop(to_remove)

    print(len(df_))
    df_.to_csv('dataset_link_final_DOS.csv', columns=['file', 'sentence', 'type', 'labels'])


def change_tag_column():
    df = pd.read_csv('dataset_link.csv')
    columnas = ['file', 'sentence', 'type', 'labels']
    create_csv('dataset_link_final.csv', columnas)

    #Lista de los valores antiguos y nuevos
    values_replace = ['-1', 'CONTAINS', 'OVERLAP', 'BEFORE', 'BEGINS-ON', 'ENDS-ON', 'SIMULTANEOUS']
    values = ['0', '1', '2', '3', '4', '5', '6']

    #Hace replace de todos ellos
    for i in values_replace:
        df = df.replace(to_replace=i, value=values[values_replace.index(i)])
    
    #Quita la columna esta que metí sin querer
    df.pop('Unnamed: 0')

    df.to_csv('dataset_link_final.csv', mode='a', index=False, header=False)

def split_train_test_tlink():
    df = pd.read_csv('dataset_link_final.csv')
    #df = pd.read_csv('dataset_link.csv')
    #Para esta división lo importante es que haya un número de parejas equilibrado en train y dev (número de filas). Así que hay que buscar documentos para que se equilibre el número final

    list_test = ['ES100001.xml', 'ES100002.xml', 'ES100030.xml', 'ES100042.xml', 'ES100079.xml', 'ES100143.xml', 'ES100163.xml', 'ES100178.xml', 'ES100214.xml', 'ES100363.xml', 'ES100410.xml', 'ES100412.xml', 'ES100417.xml', 'ES100445.xml', 'ES100513.xml', 'ES100526.xml', 'ES100569.xml', 'ES100594.xml', 'ES100634.xml', 'ES100642.xml', 'ES100686.xml', 'ES100688.xml', 'ES100705.xml', 'ES100713.xml', 'ES100715.xml', 'ES100727.xml', 'ES100737.xml', 'ES100775.xml', 'ES100778.xml', 'ES100803.xml', 'ES100819.xml', 'ES100832.xml', 'ES100840.xml', 'ES100848.xml', 'ES100937.xml', 'ES100947.xml']
    
    list_train = ['ES100686.xml', 'ES100775.xml','ES100526.xml', 'ES100042.xml', 'ES100727.xml', 'ES100848.xml', 'ES100445.xml', 'ES100079.xml', 'ES100737.xml', 'ES100642.xml', 'ES100143.xml', 'ES100778.xml', 'ES100803.xml', 'ES100634.xml', 'ES100594.xml', 'ES100030.xml', 'ES100178.xml', 'ES100363.xml', 'ES100001.xml', 'ES100410.xml', 'ES100412.xml', 'ES100002.xml', 'ES100214.xml', 'ES100163.xml', 'ES100417.xml']
    
    list_dev = ['ES100832.xml',  'ES100947.xml', 'ES100819.xml', 'ES100937.xml', 'ES100513.xml', 'ES100705.xml', 'ES100840.xml', 'ES100713.xml', 'ES100688.xml', 'ES100715.xml', 'ES100569.xml']

    columnas = ['file','sentence','type','labels']
    create_csv('dataset_link_train.csv', columnas)
    create_csv('dataset_link_test.csv', columnas)
    create_csv('dataset_link_dev.csv', columnas)

    df_filter = df['file'].isin(list_train)
    df_train = df[df_filter]
    df_filter = ~df['file'].isin(list_test)
    df_test = df[df_filter]
    df_filter = df['file'].isin(list_dev)
    df_dev = df[df_filter]
    #print(len(df_train))
    #print(len(df_dev))
    #print(len(df_test))
    #print(len(df))

    df_train.to_csv('dataset_link_train.csv', columns=columnas, index=False)
    df_test.to_csv('dataset_link_test.csv', columns=columnas, index=False)
    df_dev.to_csv('dataset_link_dev.csv', columns=columnas, index=False)
    #Ver cuántas instancias de cada etiqueta hay en cada split. Si se quieren ver las etiquetas con su nombre y no su número cargar el df que está comentado
    """
    tag_unique = df_train['tag'].unique()
    #print(df_test[df_test['tag'] == tag_unique[2]])
    for tag in tag_unique:
        print(tag)
        print(len(df_train[df_train['tag'] == tag]))
        print(len(df_dev[df_dev['tag'] == tag]))
        print(len(df_test[df_test['tag'] == tag]))
    """  

    #Esto es para sacar la suma acumulada de sentences de cada documento para ver dónde sumaba más o menos 2306
    """
    unique_train = df_train['file'].unique()
    suma = 0
    lista_train = []
    lista_dev = []
    for unique in unique_train:
        #print(unique)
        #print('longitud: ' + str(len(df_train[df_train['file'] == unique])))
        suma = suma + len(df_train[df_train['file'] == unique])
        #print('SUMA: ' + str(suma))
        if suma < 2300:
            lista_train.append(unique)
        if suma > 2300:
            lista_dev.append(unique)
    
    #df_train.to_csv('events_train.csv',index = False)
    #df_test.to_csv('events_test.csv',index = False)
    suma = 0
    for file in list_train_:
         suma = suma + len(df[df['file'] == file])
    print(suma)

    suma = 0
    for file in list_dev:
         suma = suma + len(df[df['file'] == file])
    print(suma)
    """
    
    #La movida esta de generar todas las combinaciones y sacar la que más se acerque pero va lentísimo
    """
    rango = [2296,2297, 2298, 2299, 2300, 2301, 2302, 2303, 2304, 2305, 2306, 2307, 2308, 2309,2300, 2310, 2311, 2312, 2313, 2314, 2315, 2316]
    for i in range(len(lista_long)):
        if i > 8:
            for var in combinations(lista_long, i):
                False
                #print(var)
                if sum(list(var)) in rango:
                    print(list(var)) 
    """
    
def split_train_test_tlink_2():
    df = pd.read_csv('dataset_link_final_DOS.csv')


    list_test = ['ES100001.xml', 'ES100002.xml', 'ES100030.xml', 'ES100042.xml', 'ES100079.xml', 'ES100143.xml', 'ES100163.xml', 'ES100178.xml', 'ES100214.xml', 'ES100363.xml', 'ES100410.xml', 'ES100412.xml', 'ES100417.xml', 'ES100445.xml', 'ES100513.xml', 'ES100526.xml', 'ES100569.xml', 'ES100594.xml', 'ES100634.xml', 'ES100642.xml', 'ES100686.xml', 'ES100688.xml', 'ES100705.xml', 'ES100713.xml', 'ES100715.xml', 'ES100727.xml', 'ES100737.xml', 'ES100775.xml', 'ES100778.xml', 'ES100803.xml', 'ES100819.xml', 'ES100832.xml', 'ES100840.xml', 'ES100848.xml', 'ES100937.xml', 'ES100947.xml']
    
    list_train = ['ES100686.xml', 'ES100526.xml', 'ES100042.xml', 'ES100727.xml',
    'ES100848.xml', 'ES100445.xml', 'ES100737.xml',
    'ES100642.xml', 'ES100778.xml', 'ES100803.xml',
    'ES100634.xml', 'ES100594.xml', 'ES100569.xml', 'ES100030.xml',
    'ES100178.xml', 'ES100363.xml', 'ES100001.xml', 'ES100410.xml',
    'ES100412.xml', 'ES100002.xml', 'ES100214.xml', 'ES100163.xml',
    'ES100417.xml', 'ES100832.xml', 'ES100715.xml' ]

    list_dev = ['ES100775.xml', 'ES100947.xml',
    'ES100819.xml', 'ES100937.xml', 'ES100513.xml', 'ES100705.xml',
    'ES100840.xml', 'ES100713.xml', 'ES100688.xml', 'ES100079.xml', 'ES100143.xml']

    columnas = ['file','sentence','type','labels']
    create_csv('dataset_link_train_DOS.csv', columnas)
    create_csv('dataset_link_test_DOS.csv', columnas)
    create_csv('dataset_link_dev_DOS.csv', columnas)

    df_filter = df['file'].isin(list_train)
    df_train = df[df_filter]
    df_filter = ~df['file'].isin(list_test)
    df_test = df[df_filter]
    df_filter = df['file'].isin(list_dev)
    df_dev = df[df_filter]
    print(len(df_train))
    print(len(df_dev))
    print(len(df_test))
    print(len(df))

    df_train.to_csv('dataset_link_train_DOS.csv', columns=columnas, index=False)
    df_test.to_csv('dataset_link_test_DOS.csv', columns=columnas, index=False)
    df_dev.to_csv('dataset_link_dev_DOS.csv', columns=columnas, index=False)

    unique_train = df_train['file'].unique()
    #print(unique_train)
    suma = 0
    lista_train = []
    lista_dev = []
    for unique in unique_train:
        #print(unique)
        #print('longitud: ' + str(len(df_train[df_train['file'] == unique])))
        suma = suma + len(df_train[df_train['file'] == unique])
        #print('SUMA: ' + str(suma))
        if suma < 2300:
            lista_train.append(unique)
        if suma > 2300:
            lista_dev.append(unique)

def prueba2():
    nSamples = [4608, 2287, 367, 147, 553, 192, 224]

    weights_ = [1 - (x / sum(nSamples)) for x in nSamples]

    weights = [1 / (x / sum(nSamples)) for x in nSamples]

    weights = [(x / sum(nSamples)) for x in nSamples]
    
    print(weights)

    print(weights_)


    
    


def main():

    """Extract TEXT from the xml data_annotation/spanish/layer1 ('PATH') into a csv ('filename') with the columns ('fields')"""
    #fields = ['file', 'input_clear']
    #filename = 'inputs_clear.csv'
    #create_csv(filename_e3c=filename, fields_e3c=fields)
    #extract_text_to_csv(filename)

    """Extract TIME EXPRESSIONS from the xml data_annotation/spanish/layer1 ('PATH') into a csv ('FILENAME_E3C') with the columns ('FIELDS_E3C')"""
    """
    create_csv(filename_e3c=FILENAME_E3C, fields_e3c=FIELDS_E3C)
    for file in  os.listdir(PATH):
        if file != '.DS_Store':
            extract_timex3(file)
    """
    """Extract EVENTS from the xml data_annotation/spanish/layer1 ('PATH') into a csv (' ') with the columns (' ')"""
    #create_csv(filename_e3c='events.csv', fields_e3c=['file', 'id_event', 'string', 'begin', 'end', 'ALINK', 'TLINK', 'contextualAspect', 'contextualModality', 'degree', 'docTimeRel', 'eventType', 'permanence', 'polarity'])
    #extract_events()
    
    """Extract CLINENTITY from the xml data_annotation/spanish/layer1 ('PATH') into a csv (' ') with the columns (' ')"""
    #extract_clienentity()

    #get_tokens_events()

    #sacar_eventos_total()

    #estadísticas_eventos()

    #get_event_timex_pairs()

    #get_tlink()

    #pairs_tagged()

    #sentence_strings()

    #sentence_strings_con_pair()

    #pairs_tagged_string()

    #clear_sentence_event_timex_tagged()

    #change_tag_column()

    #split_train_test_tlink()

    split_train_test_tlink_2()

    #get_events_timex()

    #train_test()

    #prueba2()

    #resultados_epoch_relaciones()

    #numero_tokens_train_test()
    #heidelTime()
    #transform_heidel()
    #print(sys.path)
    

if __name__ == "__main__":
    main()



#------PRUEBAS------#
"""
def pruebas():

    PATH = '/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation/Spanish/layer1/ES100688.xml'
    df = pd.read_xml(PATH)
    input_id = df.loc[df['id'] == 1]
    input_id = input_id['sofa']
    input_id = int(input_id.values[0])
    print(input_id)

    input_ = df.loc[df['id'] == input_id]
    input_ = input_['sofaString']
    if input_.values[0] == None:
        input_clear = input_.values[1]#.replace("\n\t", "  ")
    else: 
        input_clear = input_.values[0]#.replace("\n\t", "  ")

    print("TEXTO:" + str(input_clear))
"""
#------ESTAS LÍNEAS VALEN SI SE EJECUTA EN PYTHON2.X------#
#clear_input = clear_input.replace("ñ", "\xc3\xb1")
#clear_input = clear_input.decode("utf-8")
#clear_input = unidecode.unidecode(clear_input)

#------SUSTITUYE LOS SALTOS DE LÍNEA SI SE COPIA EL TEXTO DEL XML A MANO. EL &#13;&#10; REPRESENTA \n\t-----#
#input="Presentamos el caso de una mujer de 70 años, con antecedentes de hipertensión arterial, hernia de hiato, estreñimiento e histerectomía que consultó por síndrome miccional irritativo desde hacía 8 meses, consistente en disuria y polaquiuria intensas con urgencias miccionales ocasionales sin otra sintomatología urológica añadida. En los últimos 6 meses había presentado 3 episodios de infección del tracto urinario bajo con urocultivos positivos a E. coli tratados por su médico de cabecera.&#13;&#10;El estudio inicial incluyó bioquímica sanguínea que fue normal, orina y estudio de sedimento de orina que mostraron intensa leucocituria, urocultivo que fue de nuevo positivo a E.coli y una citología urinaria por micción espontánea cuyo resultado fue células uroteliales sin atipias y abundantes leucocitos polimorfonucleares neutrófilos. Se prescribió tratamiento con antibioteparia y anticolinérgico (tolterodina).&#13;&#10;A los 3 meses la paciente fue revisada en consulta externa, persistiendo la sintomatología basada en disuria y polaquiuria, si bien había mejorado bastante de las urgencias con el anticolinérgico, e incluso días antes dela revisión había tenido nuevo episodio de infección urinaria.&#13;&#10;Ante la escasa respuesta encontrada, se inició un estudio más avanzado, solicitando urografía intravenosa para descartar tumor urotelial del tracto urinario superior, la cual fue rigurosamente normal, y ecografía urológica que también fue normal, por lo que se realizó cistoscopia en consulta, hallando lesiones nodulares, sobreelevadas, de aspecto sólido, discretamente enrojecidas, con áreas adyacentes de edema, localizadas en trígono y parte inferior de ambas caras laterales. Debido a este hallazgo, a pesar de que la paciente no tenía factores de riesgo para TBC y la urografía fue rigurosamente normal, se realizó baciloscopia en orina y cultivo Lowenstein-Jensen de 6 muestras de la primera orina de la mañana en días consecutivos, ya que las lesiones vesicales macroscópicamente podrían tratarse de tuberculomas, siendo estos estudios negativos para bacilo de Koch, por lo que se realizó resección endoscópica de las lesiones descritas bajo anestesia. El estudio anatomopatológico reveló ulceración de la mucosa con importante infiltrado inflamatorio crónico y congestión vascular, así como la presencia de células plasmáticas y linfocitos constituyendo folículos linfoides, los cuales están divididos en una zona central donde abundan linfoblastos e inmunoblastos, llamado centro germinativo claro, y una zona periférica formada por células maduras (linfocitos y células plasmáticas) dando lugar a los linfocitos del manto o corona radiada, como también se les denomina.&#13;&#10;&#13;&#10;A la paciente se le indicó medidas higiénico-dietéticas y profilaxis antibiótica mantenida ciclo largo a dosis única diaria nocturna 3 meses y posteriormente días alternos durante 6 meses con ciprofloxacino, vitamina A dosis única diaria 6 meses, prednisona 30mg durante 45 días y posteriormente en días alternos durante otros 45 días hasta su suspensión definitiva, y por último protección digestiva con omeprazol. La paciente experimentó clara mejoría con desaparición progresiva de la clínica, sobre todo a partir del tercer mes de tratamiento.&#13;&#10;Actualmente (al año de finalización del tratamiento), se encuentra asintomática con cistoscopia de control normal y urocultivos negativos."
#clear_input = input.replace("&#13;&#10;", "  ")

#a = "Presentamos el caso de una mujer de 70 años, con antecedentes de hipertensión arterial, hernia de hiato, estreñimiento e histerectomía que consultó por síndrome miccional irritativo desde hacía 8 meses, consistente en disuria y polaquiuria intensas con urgencias miccionales ocasionales sin otra sintomatología urológica añadida. En los últimos 6 meses había presentado 3 episodios de infección del tracto urinario bajo con urocultivos positivos a E. coli tratados por su médico de cabecera.&#13;&#10;El estudio inicial incluyó bioquímica sanguínea que fue normal, orina y estudio de sedimento de orina que mostraron intensa leucocituria, urocultivo que fue de nuevo positivo a E.coli y una citología urinaria por micción espontánea cuyo resultado fue células uroteliales sin atipias y abundantes leucocitos polimorfonucleares neutrófilos. Se prescribió tratamiento con antibioteparia y anticolinérgico (tolterodina).&#13;&#10;A los 3 meses la paciente fue revisada en consulta externa, persistiendo la sintomatología basada en disuria y polaquiuria, si bien había mejorado bastante de las urgencias con el anticolinérgico, e incluso días antes dela revisión había tenido nuevo episodio de infección urinaria.&#13;&#10;Ante la escasa respuesta encontrada, se inició un estudio más avanzado, solicitando urografía intravenosa para descartar tumor urotelial del tracto urinario superior, la cual fue rigurosamente normal, y ecografía urológica que también fue normal, por lo que se realizó cistoscopia en consulta, hallando lesiones nodulares, sobreelevadas, de aspecto sólido, discretamente enrojecidas, con áreas adyacentes de edema, localizadas en trígono y parte inferior de ambas caras laterales. Debido a este hallazgo, a pesar de que la paciente no tenía factores de riesgo para TBC y la urografía fue rigurosamente normal, se realizó baciloscopia en orina y cultivo Lowenstein-Jensen de 6 muestras de la primera orina de la mañana en días consecutivos, ya que las lesiones vesicales macroscópicamente podrían tratarse de tuberculomas, siendo estos estudios negativos para bacilo de Koch, por lo que se realizó resección endoscópica de las lesiones descritas bajo anestesia. El estudio anatomopatológico reveló ulceración de la mucosa con importante infiltrado inflamatorio crónico y congestión vascular, así como la presencia de células plasmáticas y linfocitos constituyendo folículos linfoides, los cuales están divididos en una zona central donde abundan linfoblastos e inmunoblastos, llamado centro germinativo claro, y una zona periférica formada por células maduras (linfocitos y células plasmáticas) dando lugar a los linfocitos del manto o corona radiada, como también se les denomina.&#13;&#10;&#13;&#10;A la paciente se le indicó medidas higiénico-dietéticas y profilaxis antibiótica mantenida ciclo largo a dosis única diaria nocturna 3 meses y posteriormente días alternos durante 6 meses con ciprofloxacino, vitamina A dosis única diaria 6 meses, prednisona 30mg durante 45 días y posteriormente en días alternos durante otros 45 días hasta su suspensión definitiva, y por último protección digestiva con omeprazol. La paciente experimentó clara mejoría con desaparición progresiva de la clínica, sobre todo a partir del tercer mes de tratamiento.&#13;&#10;Actualmente (al año de finalización del tratamiento), se encuentra asintomática con cistoscopia de control normal y urocultivos negativos."
#clear_a = a.replace("&#13;&#10;", " ") #QUITA LOS SALTOS DE LÍNA EN EL FORMATO EN EL QUE APARECEN EN EL XML
#clear_a = ' '.join(clear_a.split())
#clear_a = unidecode.unidecode(clear_a)
#b = "Presentamos el caso de una mujer de 70 años, con antecedentes de hipertensión arterial, hernia de hiato, estreñimiento e histerectomía que consultó por síndrome miccional irritativo desde hacía 8 meses, consistente en disuria y polaquiuria intensas con urgencias miccionales ocasionales sin otra sintomatología urológica añadida. En los últimos 6 meses había presentado 3 episodios de infección del tracto urinario bajo con urocultivos positivos a E. coli tratados por su médico de cabecera. El estudio inicial incluyó bioquímica sanguínea que fue normal, orina y estudio de sedimento de orina que mostraron intensa leucocituria, urocultivo que fue de nuevo positivo a E.coli y una citología urinaria por micción espontánea cuyo resultado fue células uroteliales sin atipias y abundantes leucocitos polimorfonucleares neutrófilos. Se prescribió tratamiento con antibioteparia y anticolinérgico (tolterodina). A los 3 meses la paciente fue revisada en consulta externa, persistiendo la sintomatología basada en disuria y polaquiuria, si bien había mejorado bastante de las urgencias con el anticolinérgico, e incluso días antes dela revisión había tenido nuevo episodio de infección urinaria. Ante la escasa respuesta encontrada, se inició un estudio más avanzado, solicitando urografía intravenosa para descartar tumor urotelial del tracto urinario superior, la cual fue rigurosamente normal, y ecografía urológica que también fue normal, por lo que se realizó cistoscopia en consulta, hallando lesiones nodulares, sobreelevadas, de aspecto sólido, discretamente enrojecidas, con áreas adyacentes de edema, localizadas en trígono y parte inferior de ambas caras laterales. Debido a este hallazgo, a pesar de que la paciente no tenía factores de riesgo para TBC y la urografía fue rigurosamente normal, se realizó baciloscopia en orina y cultivo Lowenstein-Jensen de 6 muestras de la primera orina de la mañana en días consecutivos, ya que las lesiones vesicales macroscópicamente podrían tratarse de tuberculomas, siendo estos estudios negativos para bacilo de Koch, por lo que se realizó resección endoscópica de las lesiones descritas bajo anestesia. El estudio anatomopatológico reveló ulceración de la mucosa con importante infiltrado inflamatorio crónico y congestión vascular, así como la presencia de células plasmáticas y linfocitos constituyendo folículos linfoides, los cuales están divididos en una zona central donde abundan linfoblastos e inmunoblastos, llamado centro germinativo claro, y una zona periférica formada por células maduras (linfocitos y células plasmáticas) dando lugar a los linfocitos del manto o corona radiada, como también se les denomina. A la paciente se le indicó medidas higiénico-dietéticas y profilaxis antibiótica mantenida ciclo largo a dosis única diaria nocturna 3 meses y posteriormente días alternos durante 6 meses con ciprofloxacino, vitamina A dosis única diaria 6 meses, prednisona 30mg durante 45 días y posteriormente en días alternos durante otros 45 días hasta su suspensión definitiva, y por último protección digestiva con omeprazol. La paciente experimentó clara mejoría con desaparición progresiva de la clínica, sobre todo a partir del tercer mes de tratamiento. Actualmente (al año de finalización del tratamiento), se encuentra asintomática con cistoscopia de control normal y urocultivos negativos."

#------COMPUTA LA DIFERENCIA ENTRE DOS STRINGS-----#
#diff = dl.context_diff(clear_a, b)
#for diff in dl.context_diff(clear_a, b):
#    print(diff)