# Use of keystroke dynamics and a keystroke-face fusion system in the real world

This is the repository which features the code used in experiments that were described in the paper titled *Use of keystroke dynamics and a keystroke-face fusion system in the real world*.

## Structure of the repository

Inside this repository, you can find three folders:

### Notebooks

In the notebooks folder, you can find the Jupyter notebook and the compiled NN models and weights used to test the neural network implementation by Nikolai Janakiev, found [in this repository](https://github.com/njanakiev/keystroke-biometrics). It basically simplifies a little bit of the code to test only the best version of the proposed classifier.

### Comparisons

This folder features code for comparing the quality of different detectors (distances) and additional data (such as the dataset etc.).
The data was taken from [this](http://www.cs.cmu.edu/~keystroke/) website. Some classification methods were implemented after the ideas in the Killourhy and Maxion [paper](http://www.cs.cmu.edu/~maxion/pubs/KillourhyMaxion09.pdf) on Keystroke Dynamics.

To help speed up the imiplementation of some classifiers, I used [this project](https://github.com/rehassachdeva/Anomaly-Detection-for-Keystroke-Dynamics/blob/master/KeystrokeDynamics.ipynb) for reference as well, as Rehas Sachdeva has done amazing work implementing the same classifiers mention in the work by Killourhy and Maxion.

To test the neural network performance, I have used some code and the architecure provided in [this](https://github.com/njanakiev/keystroke-biometrics) repository by Nikolay Janakiev and included it in the comparisons folder as mentioned before.

To compare scores for different features and different classifiers, go to the non_deep_classifiers.py file and scroll to the bottom, where you can tweak parameters such as:
- which classifiers to use,
- which features to use,
- how many imposter samples we use for determining the accuracy.

All the code is written in Python version 3 and requires libraries `numpy`, `pandas`, `sklearn` and `scipy` to work.

### Web

The web folder features a simple HTML form with some javascript logic for recording keystroke patterns. The patters get sent to the flask api which
features a classifier class that can compute distances based on keystroke pattern timing vectors sent from the form. 

![Web form](web_form.png?raw=true "Web form")

You can use this form to test a real world example using the tested classification approaches from the `/comparisons` folder.

To play with the parameters in the form, such as the word and the number of repetitions of typing that word, go to form.js and at the top, change the word, allRepetitions and remainingRepetions variables.

To run the code, serve the folder (to get HTML served to the browser) with

```bash
python -m SimpleHttpServer {some port number}
```

and then run the flask API using

```bash
export FLASK_APP=api.py
flask run
```

You might need to install software from the requirements.txt file and set up a virtual environment in order to make the application function correctly. The API code works only with Python version 3, so make you are using that.