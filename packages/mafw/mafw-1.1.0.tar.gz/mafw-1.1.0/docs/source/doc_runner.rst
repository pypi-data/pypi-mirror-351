.. include:: substitutions.rst

.. _doc_runner:

Run your processors from the command line
=========================================

Now that you have a wonderful library of |processors| that are exported as plugins to MAFw, you can benefit from an additional *bonus*, the possibility to execute them without having to code any other line!

When you have installed `MAFw` in your environment, an executable file mafw has been put in your path, so that if you open a console and you activate the python environment, you can run it.

Just try something like this!

.. code-block:: doscon

    (env) C:\>mafw -v
    mafw, version 0.0.5

If you get this message (the version number may vary), you are good to go. Otherwise, check that everything was installed correctly and try again.

This executable is rather powerful and can launch several commands (see the full documentation :mod:`here <mafw.scripts.mafw_exe>`, but for the time we will focus on three.

List the processors
-------------------

Before doing anything else, it is important to check that your processor library has been properly loaded in MAFw. To check that, run the following command from the console.

.. figure:: /_static/images/runner/available-processors.png
    :width: 600
    :align: center
    :alt: The list of available processors.


The output should be a table similar to the one above, containing a list of known processors in the first column, the package where they come from in the second and the module in the third one.

If you have exported your processors correctly the total external processors should be different from zero.

.. _gen_steering:

Prepare a generic steering file
-------------------------------

The next step is to prepare a steering file. We do not want you to open your text editor and start preparing the TOML file from scratch. MAFw can prepare a generic template for you that you have to adapt to your needs before running.

.. code-block:: doscon

    (env) C:\>mafw steering steering-file.toml
    A generic steering file has been saved in steering-file.toml.
    Open it in your favourite text editor, change the processors_to_run list and save it.

    To execute it launch: mafw run steering-file.toml.

This command is generating a generic steering file with a list of all processors available (internal to MAFw and imported from your library) with all their configurable parameters. You can pass the option `--show` to display the generated file on the console, or even more practical the `--open-editor` to open the steering file in your default editor so that you can immediately customize it.

Here below is an example of what you will get. The content may vary, but the ideas are the same.

.. code-block:: toml
    :caption: An example of steering file.
    :linenos:
    :emphasize-lines: 4

    # MAFw steering file generated on 2024-11-21 16:54:22.455297

    # uncomment the line below and insert the processors you want to run from the available processor list
    # processors_to_run = []

    # customise the name of the analysis
    analysis_name = "mafw analysis"
    analysis_description = "Summing up numbers"
    available_processors = ["AccumulatorProcessor", "GaussAdder", "ModifyLoopProcessor"]

    [AccumulatorProcessor] # A processor to calculate the sum of the first n values via a looping approach.
    last_value = 100 # Last value of the series

    [GaussAdder] # A processor to calculate the sum of the first n values via the so called *Gauss formula*.
    last_value = 100 # Last value of the series.

    [ModifyLoopProcessor] # Example processor demonstrating how it is possible to change the looping structure.
    item_to_abort = 65 # Item to abort
    items_to_skip = [12, 16, 25] # List of items to be skipped.
    total_item = 100 # Total item in the loop.

    [UserInterface] # Specify UI options
    interface = "rich" # Default "rich", backup "console"

The TOML file contains some tables and arrays that should be rather easy to understand. There is an important array at line 4 that you need to uncomment and to fill in with the |processors| that you want to run. For all known processors, there is table with all the configurable parameters, you can change them to your wishes. You do not need to remove the configuration information of the processors that you do not intend to use. They will be simply ignored.

If you have commented your |processor| classes properly, the short description will appear next to the table.

You can customize the analysis name and short description to make the execution of the steering file a bit nicer. In the UserInterface section, you can change the way the processor will interact with you. If you are running the steering file on a headless HPC, then you do not need to have any fancy output. If you like to see progress bars and spinners moving, then select rich as your interface.

Run the steering file
---------------------

Here we are, finally! Now we can run our analysis and enjoy the first results.

From the console type the following command:

.. code-block:: doscon

    (env) C:\>mafw run steering-file.toml

and enjoy the thrill of seeing your data being processed. From now on, you have a new buddy helping you with the analysis of your data, giving you more time to generate nice and interesting plots because MAFw will do all the boring stuff for you!

Debugging your processors
-------------------------

When you execute your processors from the command line using `mafw` and something does not work as expected, you may want to debug your processors to fix the problem. Normally you would turn back to your IDE and click on the debug run button to follow your code line by line and see where it fails.

The problem here is that the module where you have coded your processor is not `running`, it just contains the definition of the processor! You would need to create an instance of your processor and to execute it in a standalone way, but then you would have to set the parameters manually. In other words, it is going to be slow and problematic and MAFw wants to alleviate your problems, not to create new ones!

The best way is to run the mafw executable in debug mode from your IDE inserting a breakpoint in your processor code.

In PyCharm, you would create a new python configuration launching a module instead of a script. See the screenshot below.

.. figure:: /_static/images/plugins/pycharm-mafw-exe-configuration.png
    :width: 500
    :align: center
    :alt: Screenshot with pycharm configuration to run mafw

    The PyCharm configuration for running mafw_exe from your plugin module.
    It can be particularly helpful to execute your processor in debug mode.

The three most important points have been highlighted. First of all, you need to select module and not script from the drop down menu indicated by the green arrow. In the text field next to it (yellow in the screenshot), write `mafw.scripts.mafw_exe`. MAFw is installed in the environment where your plugins are living, so PyCharm will complete the module name while writing. In the text field below (orange in the screenshot) write the command line options as you were doing from the console. Optionally, if you want to enjoy the colorful output of the :class:`~mafw.ui.rich_user_interface.RichInterface`, click on the *Modify options* (top blue arrow) and add *Emulate terminal in output console*. The corresponding label will appear in the bottom part as indicated by the blue arrow.


What's next
-----------

You believed we were done? Not really. We have just started, this was just the appetizer! Get ready for the next course, when we will enjoy the power of relational databases!
