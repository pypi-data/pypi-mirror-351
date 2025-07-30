"""
Functions for saving and loading machine learning models
"""
import joblib

def load_model(filename='model.di'):
    """
    Load a machine learning model from a file.
    
    Parameters:
    -----------
    filename : str, default='model.di'
        The path to the file containing the model
        
    Returns:
    --------
    object
        The loaded model
        
    Raises:
    -------
    FileNotFoundError
        If the file does not exist
    """
    return joblib.load(filename)

def save_model(model, filename='model.di'):
    """
    Save a machine learning model to a file.
    
    Parameters:
    -----------
    model : object
        The model to be saved
    filename : str, default='model.di'
        The path to the file where the model will be saved
        
    Returns:
    --------
    str
        The path to the saved model file
    """
    joblib.dump(model, filename)
    return filename

__all__ = ['load_model', 'save_model'] 