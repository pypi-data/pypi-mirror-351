.. _tutorial:

A step by step tutorial for a real experimental case study
==========================================================

.. todo::

    This text here is just a draft.

You do not need to be a DB manager to known how powerful a relational database can be and how helpful it can be in your every data task. MAFw will allow you to obtain the best from it, without having to master a course in SQL and similar topics.

To explain you better, let us follow a real case, that will be presented in more details in this section.

You want to test the linearity in the response of an position sensitive detector when exposed to an x-ray beam. For this reason, you collect, let us say 5 images each of them with 100 x 100 pixels at 5 different exposure times. When you finished your experimental campaign you have already 25 images to be analysed. But now, you want to play with x-ray tube parameters, and you repeat the same experiment as before with 4 different high voltage settings (you are 100 images) and for each high voltage you try with 4 different tube currents (400 images in total). And you can easily go ahead like this for many parameters.

All images will have to undergo some common analytical steps, for example conversion to a :link:`pandas` dataframe, then you want to aggregate the 100 x 100 pixel signals in some statistical quantities (average and standard deviation, for example) and finally you want to produce plots showing the effect of each parameter.

So far you have seen how you can use the MAFw framework to build the processors:

    * one to do the dataframe conversion,
    * another one for the aggregation and
    * a final one for the plotting.

But with 400 images it is very easy to get confused and the possibility to make a mistake is just around the corner. For sure you do not want to include the list of all 400 images in a steering file. Let us ask the database to do this for us!

The database to support I/O operations
--------------------------------------

To the list of the processors listed in the previous section, we would suggest to add a first one, to *import* your experimental results in the database. MAFw is providing you with a general import processors and a power full filename parser, that you will get familiar with in the :ref:`tutorial <tutorial>` section.

This processor will not move the files anywhere, but if the filename where encoded with a logic, the parser will create an entry in a database table for each of them properly assigning all the parameters, like the exposure time, the high voltage and the tube current. It is important to add a field with the full filename and one for the hash

