from importlib import resources
import pickle


class LoadPretrainedModels:

    def __init__(self, character_ner_model_name='SatuaNER'):
        """
        <Args>
        - character_ner_model_name: Character NER model name used
            -> Options: <SatuaNER, CRF_1, CRF_2, HMM, SVM>
            -> Default: SatuaNER

        <Output>
        Return specified pretrained models
        """
        self.pretrained_model_path = self.__get_package_pretrained_models_path(
            subfolder=character_ner_model_name)

    def __get_package_pretrained_models_path(self, subfolder):
        """
        Returns the absolute path to a data file located within the package.
        Uses importlib.resources for robust path resolution.
        """
        # Use resources.path to get a context manager that provides the file path
        # 'balistoryanalyzer' is the top-level package name
        # f'data.{subfolder}' specifies the nested package for data
        filename = 'pretrained_best_model.pkl'
        with resources.path(f'balistoryanalyzer.pretrained_models.{subfolder}', filename) as p:
            return str(p)

    def load_model(self):
        pretrained_model = pickle.load(open(self.pretrained_model_path, 'rb'))
        pretrained_m1_model = pretrained_model['optimal_best_fold_model']['model']
        pretrained_m2_model = pretrained_model['optimal_best_all_train_model']
        return pretrained_m1_model, pretrained_m2_model
