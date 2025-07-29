import os
import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import logging 
import pickle
from tqdm import tqdm
import tensorflow as tf
import tensorflow_hub as hub
from datetime import datetime
months_num = {   1: 'Janvier',
                 2: 'Février',
                 3: 'Mars',
                 4: 'Avril',
                 5: 'Mai',
                 6: 'Juin',
                 7: 'Juillet',
                 8: 'Août',
                 9: 'Septembre',
                 10: 'Octobre',
                 11: 'Novembre',
                 12: 'Décembre'}
quarter_num = {  1: 'Trimestre 1',
                 2: 'Trimestre 1',
                 3: 'Trimestre 1',
                 4: 'Trimestre 2',
                 5: 'Trimestre 2',
                 6: 'Trimestre 2',
                 7: 'Trimestre 3',
                 8: 'Trimestre 3',
                 9: 'Trimestre 3',
                 10: 'Trimestre 4',
                 11: 'Trimestre 4',
                 12: 'Trimestre 4'}

from lxf.settings import get_logging_level
logger = logging.getLogger('ClassificationTCFinanceAccountigs')
fh = logging.FileHandler('./logs/ClassificationTCFinanceAccountigs.log')
fh.setLevel(get_logging_level())
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(get_logging_level())
logger.addHandler(fh)

memory_limit=2096

physical_devices = tf.config.list_physical_devices("GPU")
if physical_devices:
    cfg = tf.config.get_logical_device_configuration(physical_devices[0])
    if cfg == None :
        try:
            print(f"Limitation de la memoire GPU a :{memory_limit}")        
            tf.config.set_logical_device_configuration(physical_devices[0],
                                [tf.config.LogicalDeviceConfiguration(memory_limit=memory_limit)])
            print("memory setted")  
            # tf.config.set_visible_devices(physical_devices[0])
            # print(f"Device {physical_devices[0]} est marqué visible")                      
        except Exception as ex:
            print(f"Initialisation mémoire GPU impossible:\n{ex}")
else:
    logger.debug("No GPU found")


global embedding_model
embedding_model= "universal-sentence-encoder-large/5"
global embed
print(f"Chargement inital de l'embedding {embedding_model} ...")
embed = hub.load(f"https://tfhub.dev/google/{embedding_model}") 
print(f"Chargement inital de {embedding_model} terminé")

def get_gpu_strategy():
    try:
        physical_devices = tf.config.list_physical_devices("GPU")
        if physical_devices:
            gpu_strategy=tf.distribute.OneDeviceStrategy("/gpu:0")
        else:
            logger.debug("No GPU found")
            gpu_strategy=tf.distribute.OneDeviceStrategy("/cpu:0")
        return gpu_strategy 
    except Exception as e :
        logger.error(f"Exception dans get_mirror_strategy:\n{e}")

def get_input_tensor_from_phrases(phrases,len_phrase_limit:int=50):
    """ 
    Retourne un tenseur de l'embedding de phrases avec une limite de len_phrase_limit mots 
    """
    input=[]
    for feature in tqdm(phrases,desc="Embdedding des écritures"):
        embedded_feature = embed([w for w in feature.split()[:len_phrase_limit]])
        lg=embedded_feature.shape[0]
        paddings = tf.constant([[0, max(len_phrase_limit-lg,0),], [0, 0]])
        embedded_feature_padded= tf.pad(embedded_feature,paddings,"CONSTANT")
        input.append(embedded_feature_padded)
    return tf.convert_to_tensor(input,dtype=np.float32)
        
class TCFinanceAccountingsModel:
    """
    Modèle de prédiction des Services et Catégorie à partir de ligne d'écriture
    """
    
    def train(sefl, excel_model_file:str,model_name="tc_finance_accountings_model" )-> tuple[int,str]:
        """
        Apprentissage du Modèle à partir d'un fichier Excel devant contenir un onglet 'CLASSIFICATION' avec les colonnes suivantes:
        - LIBELLE : le libellé de l'écriture classée
        - SERVICE : Le service pour l'écriture
        - CATEGORIE : La catégorie du SERVICE pour l'écriture
        """
        
        if os.path.isfile(excel_model_file) :
            try:
                model_name = model_name.strip()
                data = pd.read_excel(excel_model_file,"CLASSIFICATION")
                data = data.sample(len(data),random_state=1966)
                labels=data.drop(columns=["LIBELLE"])
                classes = labels["SERVICE"]+"_"+labels["CATEGORIE"]
                X=data["LIBELLE"]
                Y_labels , classes_name = pd.factorize(classes)
                # Thredshold computation : 80 % for training 10% for testing and 10% for validating
                train_threshold = round(len(data)*.8)
                test_threshold = round(len(data)*.1)
                valid_threshold = train_threshold+round(len(data)*.1)                
                # Prepare les données train, validation et test
                # Feature X
                X_raw=get_input_tensor_from_phrases(X)
                x_train, x_test,x_valid = X_raw[:train_threshold], X_raw[train_threshold:][:test_threshold],X_raw[valid_threshold:]
                # Label Y
                y_train,y_test, y_valid = Y_labels[:train_threshold], Y_labels[train_threshold:][:test_threshold],Y_labels[valid_threshold:]
                # Datasets 
                batch_size=20
                train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
                train_dataset = train_dataset.batch(batch_size)
                logging.info(f"Train dataset:\n{train_dataset.element_spec}")
                valid_dataset = tf.data.Dataset.from_tensor_slices((x_valid, y_valid))
                valid_dataset=valid_dataset.batch(batch_size)
                logging.info(f"Valid dataset:\n{valid_dataset.element_spec}")
                test_dataset = tf.data.Dataset.from_tensor_slices((x_test, y_test))
                test_dataset=test_dataset.batch(batch_size)
                logging.info(f"Test dataset:\n{test_dataset.element_spec}")      
                # Création du model 
                gpu_strategy = get_gpu_strategy()
                with gpu_strategy.scope(): 
                    #define tensorboard callback
                    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="logs")                
                    # Create a learning rate scheduler callback
                    lr_base=5E-4
                    epochs =80
                    lr_scheduler = tf.keras.callbacks.LearningRateScheduler(lambda epoch: lr_base * 10**(epoch/epochs))
                    #set seed 
                    tf.random.set_seed(20250)
                    # Definition des couches
                    model = tf.keras.Sequential(name=model_name,layers=[
                        tf.keras.layers.GlobalAveragePooling1D(),
                        tf.keras.layers.Dense(512,activation='relu'),
                        #tf.keras.layers.Dense(512,activation='relu'),
                        tf.keras.layers.Dense(len(classes_name),activation='softmax'),
                    ])      
                    # Compilation du modèle 
                    model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                                optimizer=tf.keras.optimizers.Adam(),
                                metrics=['accuracy'])   
                    #define tensorboard callback
                    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="logs")                    
                    # Entrainer le model 
                    history = model.fit(train_dataset, epochs=epochs,
                                        validation_data=valid_dataset,
                                        callbacks=[tensorboard_callback,lr_scheduler],
                                        verbose=1)            
                    # Evaluation du modèle 
                    test_loss, test_acc = model.evaluate(test_dataset)                            
                    # sauvegarde du modèle 
                    model.summary()                    
                    model_dir="models"
                    if os.path.exists(model_dir) ==False:
                        os.makedirs(model_dir)
                    model_filename=f"{model_dir}/classification/tc_finance/{model_name}_model.keras"
                    model.save(model_filename)
                    # saving the class_names
                    class_filename = f"{model_dir}/classification/tc_finance/{model_name}_classes.pkl"
                    with open(class_filename,"wb") as file :
                        pickle.dump(classes_name,file)
                    return 0, "Modèle entrainé et sauvegardé"
            except Exception as ex : 
                err = f"Une exception est apparue :\n{ex}"
                logger.critical(err)
                return -2, err
                
        else :
            err = f"Le fichier {excel_model_file} n'existe pas "
            logger.error(err)
            return -1, err
        
    def inference_from_xlsx(self,excel_file:str, output_file:str, model_name="tc_finance_accountings") ->tuple[int, str] :
        """
        Effectue une inférence d'un fichier d'entrée en un fichier output
        """
        if os.path.isfile(excel_file) :
            try:
                input_data = pd.read_excel(excel_file,0)
                accountings=input_data["Libellé"]
                X_to_predict = get_input_tensor_from_phrases(accountings)                
                # Chargement du modèle et des classes
                model_name = model_name.strip()
                model_filename=f"models/classification/tc_finance/{model_name}_model.keras"
                saved_model = tf.keras.models.load_model(model_filename)
                # saved_model.summary()
                classes_filename=f"models/classification/tc_finance/{model_name}_classes.pkl"
                with open(classes_filename,"rb") as file:
                    saved_classes_name = pickle.load(file,encoding="utf-8")
                # Charger les données 
                batch_size=20                
                mytest_dataset = tf.data.Dataset.from_tensor_slices(X_to_predict)
                mytest_dataset=mytest_dataset.batch(batch_size)
                # Faire l'inférence 
                predictions = saved_model.predict(mytest_dataset,verbose=0)
                # Récupérer la prédiction
                services_predicted=[]
                categories_predicted = []
                for pred in predictions :
                    y=np.argmax(a=pred)
                    classe=saved_classes_name[y]
                    tmp = classe.split("_")
                    services_predicted.append(tmp[0])
                    categories_predicted.append(tmp[1])                
                # Ajouter les colonnes prédites dans les données
                lg=input_data.columns.get_loc("Libellé")
                input_data.insert(lg,"SERVICE",services_predicted)
                input_data.insert(lg+1,"CATEGORIE",categories_predicted)                
                # Ajouter les colonnes Année, Mois et Trimestre depuis la date d'écriture
                accounting_date=input_data["Écriture"]
                Year=[]
                input_data["Annee"]=[str(datetime.strptime(str(d),"%d/%m/%Y").date().year) if pd.isna(d)==False else "" for d in accounting_date ] 
                input_data["Mois"]=[months_num[datetime.strptime(str(d),"%d/%m/%Y").date().month] if pd.isna(d)==False else "" for d in accounting_date ]
                input_data["Trimestre"]=[quarter_num[datetime.strptime(str(d),"%d/%m/%Y").date().month] if pd.isna(d)==False else "" for d in accounting_date ]                
                # Sauvegarder le résultat dans le fichier output
                with pd.ExcelWriter(output_file)as writer :
                    input_data.to_excel(writer)   
                return 0, "Inférence réussie"             
            except Exception as ex:
                err = f"Exception est apparue : {ex}"
                logger.critical(err)
                return -2, err
        else :
            err = f"Le fichier {excel_file} n'existe pas "
            logger.error(err)
            return -1, err
        