import difflib as dl
from pickle import FALSE
from turtle import clear
from xml.etree.ElementInclude import FatalIncludeError
import unidecode
import pandas as pd
import string
import re
import os
import csv
import sys

sys.path.insert(0, '/Users/asdc/Proyectos/time_line_extraction/python_heideltime/python_heideltime')

from python_heideltime import Heideltime
from xml.etree import cElementTree as ET

#------GLOBAL VARIABLES-----#
FIELDS_E3C = ['file','string','begin', 'end', 'value', 'timex3Class'] 
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
    dfcols = ['begin', 'end']
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

    df = pd.read_xml(path)
    df_time = pd.DataFrame(df, columns= ['begin','end','timex3Class', 'value'])
    df_time = df_time.loc[df_time['timex3Class'].isin(['DATE', 'TIME', 'DURATION', 'QUANTIFIER', 'SET', 'PREPOSTEXP', 'DOCTIME', 'DOCTIME'])]

    input_clear = extract_text(file)
    output_clear = extract_expresions(df_time, input_clear)

    write_timex_to_csv(file, output_clear, df_time['begin'], df_time['end'], df_time['value'], df_time['timex3Class']) 

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
def write_timex_to_csv(file_dest, file, output_clear, begin, end, value, timex3Class):
    rows = []
    
    #Generates the rows for the csv
    for beg, end_, val, timex3, output in zip(begin, end, value, timex3Class, output_clear):
        row = [str(file), str(output), str(int(beg)), str(int(end_)), str(val), str(timex3)]
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


    
def main():

    """Extract TEXT from the xml data_annotation/spanish/layer1 ('PATH') into a csv ('filename') with the columns ('fields')"""
    #fields = ['file', 'input_clear']
    #filename = 'inputs_clear.csv'
    #create_csv(filename_e3c=filename, fields_e3c=fields)
    #extract_text_to_csv(filename)

    """Extract TIME EXPRESSIONS from the xml data_annotation/spanish/layer1 ('PATH') into a csv ('FILENAME_E3C') with the columns ('FIELDS_E3C')"""

    #create_csv(filename_e3c=FILENAME_E3C, fields_e3c=FIELDS_E3C)
    #for file in  os.listdir(PATH):
    #    extract_timex3(file)

    """Extract EVENTS from the xml data_annotation/spanish/layer1 ('PATH') into a csv (' ') with the columns (' ')"""
    #create_csv(filename_e3c='events.csv', fields_e3c=['file', 'id_event', 'string', 'begin', 'end', 'ALINK', 'TLINK', 'contextualAspect', 'contextualModality', 'degree', 'docTimeRel', 'eventType', 'permanence', 'polarity'])
    #extract_events()
    
    """Extract CLINENTITY from the xml data_annotation/spanish/layer1 ('PATH') into a csv (' ') with the columns (' ')"""
    extract_clienentity()

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