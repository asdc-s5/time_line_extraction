# time_line_extraction

Here is avaliable the all the code developed in the frame of the TFM 'Information Extraction on Clinical Domain: Temporal Expresiones, Events and Temporal Relations'.

The code is divided into to main frames, the **scripts** used to preprocess the data and the **notebooks** used for training the transformer-based models. Both had been written in Python.
All the code is annotated with descriptions explaining all the methods and the process, in case someone wants to read and check the code. 

The notebooks are the main part of the code, becasuse it can be reused in many ways, the scripts are really specific to the corpus used. 
For reuse the notebooks they just have to been downloaded and executed in a prepared enviorment. All the necessary libraries for the code to work are specified in the notebooks.
It is recommended to export them into some platform like _google colab_ because the models used have are large in size and they need from powerfull hardware to work properlly.

All the datasets extracted from the corpus are also avaliable together with the data obtained from the classifications of the models.
Each model has needed specific dataset with specific format so the project counts with a lot of files with similar information. The necessary documents for each part are specified in the code.

For facilitate the user experience in the reuse of this code here below is a description of each folder´s content:

<ol>
  <li> **BioThyme_RoBERTa_es_Eventos_imagenes**: This folder counts with all the images created from the data obtained in the evaluation process of BioThyme-RoBERTa-es on the _EVENT_ dataset.</li>
  <li> **IxaMed_anotaciones**: This folder counts with all the text annotated by ixamed in it´s original output. </li>
  <li> **MNER_perceptron**: It counts with the IxaMed perceptron used to obtain the annotations on _CLINENTITY_ and _EVENTS_. This counts with the same documents as the original one, but the original one can be found here: http://ixa.ehu.eus/produktuak?language=en</li>
  <li> **documentos_in_out_eventos**: It counts with all the documents generated for the event evaluation process. 
All the documents in the root folder have been used in the process of obtaining the final dataset. It has three folders inside:
        <ol>
        <li>BioThyme_RoBERTa_es: The results of training the model on the _EVENT_ dataset. </li>
        <li>IxaMed: The results of IxaMed on the _EVENT_ dataset. </li>
        <li>Dataset: The dataset used for evaluating the models. </li>
        </ol>
  </li>
  <li> **documentos_in_out_expresiones_temporales**: This folder has all the documents that had been used for the temporal expresion part, together with the HeidelTime folder described further below.</li>
  <li> **documentos_in_out_relaciones_temporales**: This folder contains all the documents related to the temporal relation extraction. All the documents in the root folder have been used to construct the final dataset for this task. This folder contains two more:
         <ol>
        <li>Dataset: Contains both versions of the dataset used for this task, included the train-test-dev split.</li>
        <li>Resultados: Contains the results for the evaluation process, the images and the csv with the model training and test results.</li>
        </ol>
  </li>
  <li> **python_heideltime**: This folder counts with all the necessary for using HeidelTime on Python. We have used the following Python wrapper for HeidelTime: https://github.com/PhilipEHausner/python_heideltime </li>
</ol>






