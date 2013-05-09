import os
import tkinter.filedialog

def askdirectory(**kwargs):
    """
    Encapsulates tkinter.filedialog.askdirectory and adds support for
    initialdir containing accentes characters.
    """
    options = kwargs
    current_directory = os.getcwd()
    if 'initialdir' in options.keys():
        try:
            os.chdir(options['initialdir'])
        except:
            del options['initialdir']
        else:
            options['initialdir'] = '.'
    
    result = tkinter.filedialog.askdirectory(**options)
    try:
        os.chdir(current_directory)
    except:
        pass
    return result
