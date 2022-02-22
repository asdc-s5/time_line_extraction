import difflib as dl
from turtle import clear
import unidecode
import pandas as pd
import string
import re
import os


#MIRAR QUÉ FICHEROS SE UTILIZAN PARA LOS TEST Y COGER ESOS#
#COMPLETAR PARA SACAR TODAS LAS EXPRESIONES Y TEXTO DEL XML EN FORMA DE CSV PARA GUARDARLO#
#FICHERO TEXTO EXPRESIONES#
#ESTRUCTURAR EL CÓDIGO CON MAIN Y MÉTODO PARA EXTRAER TEXTO Y EXPRESIONES DEL DATASET Y RESULTADOS DEL HEIDELTIME#

def extraer(path, file):
    path = path + file

    #------EXTRAE LAS EXPRESIONES TEMPORALES DEL XML-----#
    """
    La clase 'timex3Class' puede tomar unos valores determinados por los autores.
    """
    df = pd.read_xml(path)
    df_time = pd.DataFrame(df, columns= ['begin','end','timex3Class'])
    df_time = df_time.loc[df_time['timex3Class'].isin(['DATE', 'TIME', 'DURATION', 'QUANTIFIER', 'SET', 'PREPOSTEXP', 'DOCTIME', 'DOCTIME'])]

    #------EXTRAE EL TEXTO CLÍNICO DEL XML-----#
    """
    Generalmente el id de la fila que contiene el texto tiene id=12, pero no siempre es así. 
    Lo que sí se cumple siempre es que el sofa de todas las filas indica el id de la fila con el texto.
    Por lo que se saca el sofa de la primera fila y se matchea con la fila con id=sofa.
    Por otra parte, en la fila con el texto, el texto no siempre ocupa la posición 0, también puede ser la 1. 
    Para solucionarlo se ejecuta un if por si la posición 0==None
    """
    input_id = df.loc[df['id'] == 1]
    input_id = input_id['sofa']
    input_id = int(input_id.values[0])

    input_ = df.loc[df['id'] == input_id]
    input_ = input_['sofaString']
    if input_.values[0] == None:
        input_clear = input_.values[1]#.replace("\n\t", "  ")
    else: 
        input_clear = input_.values[0]#.replace("\n\t", "  ")

    #------EXTRAE LAS EXPRESIONES TEMPORALES CORRESPONDIENTES AL TEXTO DEL XML-----#
    """
    Teniendo dos listas de pares, una 'begin' y otra 'end' que tienen el caracter inicial y final de cada expresión respecitavamente,
    solo se recorre caracter a caracter cada pareja begin-end y lo guarda en un String 
    """
    output_=[]
    
    for begin, end in zip(df_time['begin'], df_time['end']):
        texp = ""
        begin = int(begin)
        end = int(end)
        while begin <= end:
            texp += input_clear[begin] 
            begin+=1
        output_.append(texp)
    

    #------ELIMINA LOS POSIBLES ESPACIOS FINALES Y SIGNOS DE PUNTUACIÓN DE LAS EXPRESIONES TEMPORALES-----#
    """
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

    #print("FILE:" + str(path))
    #print("EXPRESIONES:" + str(output_clear))
    #print("TEXTO:" + str(input_clear))    

def heidelTime():
    False


def pruebas():
    path = '/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation/Spanish/layer1/ES100688.xml'
    df = pd.read_xml(path)
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
    
    

def main():
    path = '/Users/asdc/Library/CloudStorage/OneDrive-UNED/E3C-Corpus-2.0.0/data_annotation/Spanish/layer1/'
    
    for file in  os.listdir(path):
        extraer(path, file)
    #pruebas()



if __name__ == "__main__":
    main()



#------PRUEBAS------#

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