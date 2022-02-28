import difflib as dl
from turtle import clear
import unidecode
import pandas as pd
import string
import re
import os
import csv

from xml.etree import cElementTree as ET

#------GLOBAL VARIABLES-----#
FIELDS_E3C = ['file','string','begin', 'end', 'value', 'timex3Class'] 
FILENAME_E3C = "time_expresions.csv"
PATH = '/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation/Spanish/layer1/'


#MIRAR QUÉ FICHEROS SE UTILIZAN PARA LOS TEST Y COGER ESOS#
#COMPLETAR PARA SACAR TODAS LAS EXPRESIONES Y TEXTO DEL XML EN FORMA DE CSV PARA GUARDARLO#
#FICHERO TEXTO EXPRESIONES#
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
def extract_events(file):
    path = PATH + file

    dfcols = ['begin', 'end']
    df_event = pd.DataFrame(columns=dfcols)
    root = ET.parse(path)

    rows = root.findall('.//{http:///webanno/custom.ecore}EVENT')
    for row in rows:
        #print(row.attrib['begin'])
        begin = row.attrib['begin']
        end = row.attrib['end']
        print(begin, end)
        df_event = df_event.append(pd.Series([begin, end], index=dfcols), ignore_index=True)
    
    input_clear = extract_text(file)
    output_clear = extract_expresions(df_event, input_clear)
    print(output_clear)
    #Faltaría que escribiera en un csv, pero ya se verá qué hace falta y si hace falta

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

    write_csv(file, output_clear, df_time['begin'], df_time['end'], df_time['value'], df_time['timex3Class']) 



#------WRITE_CSV()-----#
"""
Escribe en un CSV las expresiones y distintos valores relacionados
-output_clear es una lista con todas las expresiones, por lo que hay que separarlas de 1 en 1
y emparejarlas con su begin, end, value y class, como vienen en orden no pasa nada.
"""
#Cambiar begin, end, etc por una lista para poder reutilizarlo
def write_csv(file, output_clear, begin, end, value, timex3Class):
    rows = []
    
    #Generates the rows for the csv
    for beg, end_, val, timex3, output in zip(begin, end, value, timex3Class, output_clear):
        row = [str(file), str(output), str(int(beg)), str(int(end_)), str(val), str(timex3)]
        rows.append(row)
    # writing to csv file 
    with open(FILENAME_E3C, 'a') as csvfile: 
        #creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        #writing the data rows 
        csvwriter.writerows(rows)

#------WRITE_CSV()-----#
"""
Crea un csv según los parametros definidos en las constantes globales
"""
def create_csv():

    with open(FILENAME_E3C, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the FIELDS_E3C 
        csvwriter.writerow(FIELDS_E3C) 



def heidelTime():
    False
    

def main():

    #create_csv()
    #for file in  os.listdir(PATH):
        #extract_timex3(PATH, file)
    extract_events('ES100001.xml')

    

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