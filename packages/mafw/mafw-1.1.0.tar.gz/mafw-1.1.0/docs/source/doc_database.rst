.. include:: substitutions.rst

.. _database:

Database: your new buddy!
=========================

As a scientist you are used to work with many software tools and often you need to write your own programs because the ones available do not really match your needs. Databases are not so common among scientists, we do not really understand why, but nevertheless their strength is beyond question.

The demonstration of the power and usefulness of a database assisted analysis framework will become clear and evident during our :ref:`tutorial <tutorial>` where we will build a small analytical experiment from scratch one step at the time.

For the time being, let us concentrate a bit on the technical aspect without delving too deeply into the specifics.

Database: one name, many implementations
----------------------------------------

Database is really a generic term and, from a technical point of view, one should try to be more specific and define better what kind of database we are talking about. We are not just referring to the brand or the producing software house: there are indeed different database architectures, but the one best suited for our application is the **relational database**, where each entity can be related directly to one or more other entities. You can read about relational databases on `wikipedia <https://en.wikipedia.org/wiki/Relational_database>`_ for example, and if you find it too complicated, have a look at `this shorter and easier version <https://cloud.google.com/learn/what-is-a-relational-database>`_.

The software market is full of relational databases, from the very common :link:`MySQL` to the very famous :link:`ORACLE`, passing through the open source :link:`PostgreSQL` to finish with :link:`SQLite` the simplest and most used database in the world. As you may have guessed from their names, they are all sharing the same query language (*SQL*: structured query language), making it rather simple to have an abstract interface, that is to say a layer in between the user and the actual database that allows your code to work in the same way irrespectively of the specific implementation.

Peewee: a simple and small ORM
------------------------------

Of course there are also lots of different abstract interfaces, some more performing than the others. We have selected:link:`peewee`, because it is lightweight, easy to understand and to use, and it works with several different implementations.

:link:`peewee` is a ORM (promised this is the last acronym for this page!), it is to say an object relational mappers, or in simpler words a smart way to connect the tables in your database with python classes in your code. Have a look at this interesting `article <https://www.fullstackpython.com/object-relational-mappers-orms.html>`_ for a more detailed explanation.

:link:`peewee` offers at least three different backends: SQLite, MySQL and PostgreSQL. If the size of your project is small to medium and the analysis is mainly performed on a single computer, then we recommend SQLite: the entire database will be living in a single file on your disc, eliminating the need for IT experts to set up a database server.
If you are aiming for a much bigger project with distributed computing power, then the other two choices are probably equally good and your local IT helpdesk may suggest you what is best for your configuration and the available IT infrastructure. As you see, MAFw is always offering you a tailored solution!

Now, take a short break from this page, move to the :link:`peewee` documentation and read the *Quickstart* section before coming back here.

Database drivers
++++++++++++++++

If you have installed MAFw via pip without specifying the `all-db` optional features, then your python environment is
very likely missing the python drivers to connect to MySQL and PostgreSQL. This is not a bug, but more a feature,
because MAFw gives you the freedom to select the database implementation that fits your needs. Sqlite is natively
supported by python, so you do not need to install anything extra, but if you want to use MySQL, PostgreSQL or any
other DB supported by :link:`peewee` than it is your responsibility to install in your environment the proper driver.
`Here <https://docs.peewee-orm.com/en/latest/peewee/database.html#initializing-a-database>`__ you can find a list of DB
driver compatible with :link:`peewee`.

If you want, you can install MAFw adding the `all-db` optional feature and in this way the standard MySQL and
PostgreSQL drivers will also be installed.

One class for each table
------------------------

As mentioned before, the goal of an ORM is to establish a link between a database table and a python class. You can use the class to retrieve existing rows or to add new ones, and as always, you do not need take care of the boring parts, like establishing the connection, creating the table and so on, because this is the task of MAFw and we do it gladly for you!

Let us have a look together to the following example. We want a processor that lists recursively all files starting from a given directory and adds the filenames and the file hash digests to a table in the database.

Let us start with some imports

.. literalinclude:: ../../src/mafw/examples/db_processors.py
    :linenos:
    :start-at: import datetime
    :end-at: from mafw.tools.file_tools import file_checksum
    :emphasize-lines: 4, 8

The crucial one is at line 8, where we import :class:`~mafw.db.db_model.MAFwBaseModel` that is the base model for all the tables we want to handle with MAFw. Your tables **must inherit** from that one, if you want the |processor| to take care of handling the link between the class and the table in the database.
At line 4, we import some classes from peewee, that will define the columns in our model class and consequently in our DB table.

Now let us create the model class for our table of files.

.. literalinclude:: ../../src/mafw/examples/db_processors.py
    :name: file_first
    :linenos:
    :pyobject: File

.. note::
    A much better implementation of a similar class will be given :ref:`later on <mafw_fields>` demonstrating the power of custom defined fields.

As you can see the class definition is extremely simple. We define a class attribute for each of the columns we want to have in the table and we can choose the field type from a long list of `available ones <http://docs.peewee-orm.com/en/latest/peewee/models.html#fields>`_ or we can even easily implement our owns. The role of a field is to adapt the type of the column from the native python type to the native database type and vice versa.

Our table will have just four columns, but you can have as many as you like. We will have one text field with the full filename, another text containing the hexadecimal hashlib digest of the file, the creation date for which we will use a datetime field, and finally a file_size field of integer type. We will be using the filename column as a primary key, because there cannot be two files with the same filename. On the contrary, there might be two identical files having the same hash but different filenames. According to many good database experts, using a not numeric primary key is not a good practice, but for our small example it is very practical.

If you do not specify any primary key, the ORM will add an additional number auto-incrementing column for this purpose. If you want to specify multiple primary keys, `this <http://docs.peewee-orm.com/en/latest/peewee/models.html#composite-key>`_ is what you should do. If you want to create a model without a primary key, `here <http://docs.peewee-orm.com/en/latest/peewee/models.html#models-without-a-primary-key>`_ is what you need to do.

The ORM will define the actual name of the table in the database and the column names. You do not need to worry about this!

.. admonition:: What is the name of my table?

    We have created a Model class so far, that is the link between a python object and a database table. But what is the name of the table in the database? And the name of the columns?

    All those information belong to the so called model metadata and are stored in a inner class of the :class:`~mafw.db.db_model.MAFwBaseModel`. :link:`Peewee` uses a standard way to name tables and columns and as long as your are happy with this you do not have to worry about.

    In general, MAFw is following this convention: model classes are written with CamelCase, while database tables are in snake_case. In other words, if you have a model class named **RawData** this will be linked to a database table named **raw_data**.

    If you want to customize this naming convention, you can assign a specific name to a field as `explained here <http://docs.peewee-orm.com/en/latest/peewee/models.html#field-initialization-arguments>`_ and for the table name take a look at `this page <http://docs.peewee-orm.com/en/latest/peewee/models.html#model-options-and-table-metadata>`_

And now comes the processor that will be doing the real work, it is to say, filling the File table.

.. literalinclude:: ../../src/mafw/examples/db_processors.py
    :linenos:
    :pyobject: FillFileTableProcessor
    :emphasize-lines: 1, 30, 65-66

The first thing to notice is at line 1, where we used the decorator :func:`~mafw.decorators.database_required`. The use of this decorator is actually not compulsory, its goal is to raise an exception if the user tries to execute the processor without having a properly initialized database.

At line 30, in the `start` method we ask the database to create the table corresponding to our :class:`~mafw.examples.db_processors.File` model. If the table already exists, then nothing will happen.

In the `process` method we will store all the information we have collected from the files into a list and we interact with the database only in the `finish` method. At line 65, we use a context manager to create an `atomic <https://en.wikipedia.org/wiki/Atomicity_(database_systems)>`_ transaction and then, at line 66, we insert in the :class:`~mafw.examples.db_processors.File` all our entries and in case a row with the same primary key exists, then it is replaced.

We could have used several different insert approaches, here below are few examples:

.. code-block:: python

    # create an instance of File with all fields initialized
    new_file = File(filename=str(self.item),
                  digest=file_checksum(self.item),
                  file_size=self.item.stat().st_size,
                  creation_date=datetime.datetime.fromtimestamp(self.item.stat().st_mtime))
    new_file.save() # new_file is now stored in the database

    # create an instance of File and add the fields later
    new_file = File()
    new_file.filename = str(self.item)
    new_file.digest = file_checksum(self.item)
    new_file.file_size = self.item.stat().st_size
    new_file.creation_data = datetime.datetime.fromtimestamp(self.item.stat().st_mtime)
    new_file.save()

    # create and insert directly
    new_file = File.create(filename=str(self.item),
                  digest=file_checksum(self.item),
                  file_size=self.item.stat().st_size,
                  creation_date=datetime.datetime.fromtimestamp(self.item.stat().st_mtime))

To choice of approach to follow depends on various factor. Keep in mind that :link:`peewee` operates by default in `auto commit mode <http://docs.peewee-orm.com/en/latest/peewee/database.html#autocommit-mode>`_, meaning that for each database interaction, it creates a transaction to do the operation and it closes afterwards.

To be more performant from the database point of view, especially when you have several operations that can be grouped together, you can create an `atomic transaction <http://docs.peewee-orm.com/en/latest/peewee/querying.html#atomic-updates>`_ where the ORM will open one transaction only to perform all the required operations.

What we have done in the `finish` method is actually known as an `upsert <http://docs.peewee-orm.com/en/latest/peewee/querying.html#upsert>`_. It means that we will be inserting new items or updating them if they exist already.

Ready, go!
----------

We have prepared the code, now we can try to run it. We can do it directly from a script

.. code-block:: python

    if __name__ == '__main__':
        database_conf = default_conf['sqlite']
        database_conf['URL'] = db_scheme['sqlite'] + str( Path.cwd() / Path('test.db'))

        db_proc = FillFileTableProcessor(root_folder =r'C:\Users\bulghao\Documents\autorad-analysis\EdgeTrimming',
                                         database_conf=database_conf)

        db_proc.execute()

or in a more elegant way we can use the mafw app to run, but first we need to generate the proper steering file.

.. tab-set::

    .. tab-item:: Console

        .. code-block:: doscon
            :name: gen_db_steering

            c:\> mafw steering db-processor.toml
            A generic steering file has been saved in db-processor.toml.
            Open it in your favourite text editor, change the processors_to_run list and save it.

            To execute it launch: mafw run db-processor.toml.

    .. tab-item:: TOML

        .. code-block:: toml
            :name: db-processor.toml
            :linenos:
            :emphasize-lines: 11-12, 14-18

            # MAFw steering file generated on 2024-11-24 22:13:38.248423

            # uncomment the line below and insert the processors you want to run from the available processor list
            processors_to_run = ["FillFileTableProcessor"]

            # customise the name of the analysis
            analysis_name = "mafw analysis"
            analysis_description = "Using the DB"
            available_processors = ["AccumulatorProcessor", "GaussAdder", "ModifyLoopProcessor", "FillFileTableProcessor", "PrimeFinder"]

            [DBConfiguration]
            URL = "sqlite:///file-db.db" # Change the protocol depending on the DB type. Update this file to the path of your DB.

            [DBConfiguration.pragmas] # Leave these default values, unless you know what you are doing!
            journal_mode = "wal"
            cache_size = -64000
            foreign_keys = 1
            synchronous = 0

            [FillFileTableProcessor] # Processor to fill a table with the content of a directory
            root_folder = 'C:\Users\bulghao\PycharmProjects\mafw' # The root folder for the file listing

            [UserInterface] # Specify UI options
            interface = "rich" # Default "rich", backup "console"


If you look at the steering file, you will notice that there is a ``DBConfiguration`` section, where we define the most important variable, it is to say the DB URL. This is not only specifying where the database can be found, but also the actual implementation of the database. In this case, it will be a sqlite database located in the file ``file-db.db`` inside the current directory.

There is also an additional sub table, named pragmas, containing advanced options for the sqlite DB. Unless you really know what you are doing, otherwise, you should leave them as they are.

In the following :ref:`other_db`, we will cover the case you want to use another DB implementation different from SQLite.

In the ``FillFileTableProcessor`` you can find the standard configuration of its processor parameters.

Now we are really ready to run our first DB processor and with a bit of luck, you should get your DB created and filled.

.. admonition:: How to check the content of a DB?

    There are several tools serving this purpose. One of those is :link:`dbeaver` that works with all kind of databases offering an open source community version that you can download and install.

.. _other_db:

Configuring other types of databases
++++++++++++++++++++++++++++++++++++

In the previous example, we have seen how to configure a simple SQLite database. For this database, you just need to
indicate in the URL field the path on the local disc where the database file is stored.

SQLite does not require any user name nor password and there are no other fields to be provided. Nevertheless, it is
worth adding the previously mentioned pragmas section to assure the best functionality of peewee.

In the case of MySQL and PostgreSQL, the URL should point to the server where the database is running. This could be
the localhost but also any other network destination. Along with the server destination, you need also to specify the
port, the database name, the user name and the password to establish the connection.

Of course, it is not a good idea to write your database password as plain text in a steering file that might be
shared among colleagues or even worse included in a Git repository. To avoid this security issue, it is recommended
to follow some other authentication approach.

Both MySQL and PostgreSQL offers the possibility to store the password in a separate file, that, at least in linux,
should have a very limited access right. Have a look at the exemplary steering files with the corresponding password
files here below.

.. tab-set::

    .. tab-item:: SQLite

        .. code-block:: toml

            [DBConfiguration]
            URL = "sqlite:///file-db.db" # change the filename to the absolute path of the db

            [DBConfiguration.pragmas] # Leave these default values, unless you know what you are doing!
            journal_mode = "wal"
            cache_size = -64000
            foreign_keys = 1
            synchronous = 0

    .. tab-item:: PostgreSQL

        .. code-block:: toml

            [DBConfiguration]
            # Update the database server and the database name to reflect your configuration
            URL = "postgresql://database-server:5432/database-name"

            # change it to your username
            user = 'username'

            # if you want, you can leave the pragmas section from the SQLite default configuration because it
            # want be used.


        Instruction on how to create a PostgreSQL password file are provided `here <https://www.postgresql.org/docs/current/libpq-pgpass.html>`__. This is an example:

        .. code-block:: unixconfig

            database-server:5432:database-name:username:password

    .. tab-item:: MySQL

        .. code-block:: toml

            [DBConfiguration]
            # Update the database server and the database name to reflect your configuration
            URL = "mysql://database-server:3306/database-name"

            # update to specify your username
            user = 'username'

            # update to specify the password file
            read_default_file = '~/.my.cnf'

            # if you want, you can leave the pragmas section from the SQLite default configuration because it
            # want be used.


        Instruction on how to create a MySQL password file are provided `here <https://dev.mysql.com/doc/refman/8.4/en/password-security-user.html>`__. This is an example:

        .. code-block:: ini

            [client]
            user=username
            password=password
            host=database-server


.. _triggers:

Triggers: when the database works on its own
--------------------------------------------

In the next paragraphs we will spend a few minutes understanding the roles of Triggers. Those are database entities performing some actions in response of specific events. You can have, for example, a trigger that is inserting a row in TableB whenever a row is inserted in TableA. If you are not really familiar with triggers, this is a `brief introduction <https://www.sqlite.org/lang_createtrigger.html>`_.

Triggers are very handy for many applications, and in our :ref:`tutorial <tutorial>` we will see an interesting case, but they tend to struggle with ORM in general. In fact, no ORM system is natively supporting triggers. The reason is very simple. In an ORM, the application (the python code, if you wish) is the main actor and the database is just playing the role of the passive buddy. From the point of view of an ORM based application, if you want to have a trigger, then just write the needed lines of python code to have the actions performed in the other tables. It makes totally sense, you have only one active player and it simplifies the debugging because if something is going wrong, it can only be a fault of the application.

The standard implementation of trigger-like functions with ORM is to use `signals <https://docs.peewee-orm.com/en/latest/peewee/playhouse.html#signals>`_, where you can have callbacks called before and after high level ORM APIs calls to the underlying database. Signals are good, but they are not free from disadvantages: at a first glance, they look like a neat solution, but as soon as the number of callbacks is growing, it may become difficult to follow a linear path in the application debugging. Second, if you do a change in the database from another application, like the :link:`dbeaver` browser, then none of your codified triggers will be executed. Moreover in the case of :link:`Peewee`, signals work only on Model instances, so all bulk inserts and updates are excluded.

Having triggers in the database would assure that irrespectively of the source of the change, they will always be executed, but as mentioned above, the user will have to be more careful in the debug because also the database is now playing an active role.

We let you decide what is the best solution. If you want to follow the pure ORM approach, then all models inheriting from :class:`~mafw.db.db_model.MAFwBaseModel` have the possibility to use signals. If you want to have triggers, you can also do so. An example for both approaches is shown here below.

The signal approach
+++++++++++++++++++

As mentioned above, the signal approach is the favourite one if you plan to make all changes to the database only via your python code. If you are considering making changes also from other applications, then you should better use the trigger approach.

Another limitation is that only model instances emit signals. Everytime you use a `classmethod` of a Model, then no signals will be emitted.

The signal dispatching pattern functionality is achieved by linking the signal emitted by a sender in some specific circumstances to a handler that is receiving this signal and performing some additional operations (not necessarily database operations).

Every model class has five different signals:

    1. **pre_save**: emitted just before that a model instance is saved;
    2. **post_save**: emitted just after the saving of a model instance in the DB;
    3. **pre_delete**: emitted just before deleting a model instance in the DB;
    4. **post_delete**: emitted just after deleting a model instance from the DB;
    5. **pre_init**: emitted just after the init method of the class is invoked. Note that the *pre* is actually a *post* in the case of init.

Let us try to understand how this works with an example taken from our test library.

.. literalinclude:: ../../tests/test_db.py
    :linenos:
    :pyobject: test_signals
    :name: test_signals
    :caption: A test with signal
    :emphasize-lines: 12-29,43,54

We created two tables linked via a foreign key. The goal is that everytime we fill in a row in ``MyTable``, a row is also added to TargetTable with the same id but where the value of another_float_num is just half of the original float_num. The example is stupid, but it is good enough for our demonstration.

The signal part is coded in the lines from 12 to 29 (mainly doc strings). We use the ``post_save`` decorator to connect MyTable to the ``post_save_of_my_table`` function where an insert in the TargetTable will be made.

The code is rather simple to follow. Just to be sure, we empty the two tables, then we create an instance of the MyTable model, to set the integer and the float_num column. When we save the new row, the post_save signal of MyTable is emitted and the handler is reacting by creating an entry in the TargetTable as well. In fact the number of rows of both tables are equal to 1.

What happens later is to demonstrate the weak point of signals. At line 55, we insert several rows via a ``insert_many``. It must be noted that the insert_many is a classmethod applied directly to the model class. The consequence is that the signal handler will not be invoked and no extra rows will be added to the TargetTable.

The trigger approach
++++++++++++++++++++

In order to use a trigger you need to create it. This is an entity that lives in the database, so you would need the database itself to create it.

MAFw is providing a :class:`~mafw.db.trigger.Trigger` class that helps you in creating the required SQL query that needed to be issued in order to create the trigger. Once it is created it will operate continuously.

If you have a look at the `CREATE TRIGGER SQL command <https://www.sqlite.org/lang_createtrigger.html>`_ you will see that it starts with the definition of when the trigger is entering into play (BEFORE/AFTER) and which operation (INSERT/DELETE/UPDATE) of which table. Then there is a section enclosed by the BEGIN and END keywords, where you can have as many SQL queries as you like.

The same structure is reproduced in the :class:`~mafw.db.trigger.Trigger` class. In the constructor, we will pass the arguments related to the configuration of the trigger itself. Then you can add as many SQL statement as you wish.

.. tab-set::

    .. tab-item:: Python

        .. code-block:: python
            :linenos:
            :name: trigger_python
            :caption: python Trigger class

            from mafw.db.db_model import Trigger

            new_trigger = Trigger('trigger_after_update', (TriggerWhen.After,
                    TriggerAction.Update), 'my_table', safe=False, for_each_row=False)
            new_trigger.add_sql('INSERT INTO another_table (col1, col2) VALUES (1, 2)')
            new_trigger.add_sql('INSERT INTO third_table (col1, col2) VALUES (2, 3)'))
            new_trigger.create()

    .. tab-item:: SQL

        .. code-block:: SQL
            :linenos:
            :name: trigger_sql
            :caption: emitted SQL

            CREATE TRIGGER trigger_after_update
            AFTER UPDATE  ON my_table

            BEGIN
                INSERT INTO another_table (col1, col2) VALUES (1, 2);
                INSERT INTO third_table (col1, col2) VALUES (2, 3);
            END;

Now let us have a look at how you can use this, following one of our test benches.

Standalone triggers
^^^^^^^^^^^^^^^^^^^

.. code-block:: python
    :linenos:
    :emphasize-lines: 20-22
    :name: test_manually_created_trigger
    :caption: A test Trigger created manually

    def test_manually_created_trigger():
        class MyTable(MAFwBaseModel):
            id_ = AutoField(primary_key=True)
            integer = IntegerField()
            float_num = FloatField()

        class TargetTable(MAFwBaseModel):
            id_ = ForeignKeyField(MyTable, on_delete='cascade', primary_key=True, backref='half')
            half_float_num = FloatField()

        database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
        database.connect()
        database_proxy.initialize(database)
        database.create_tables([MyTable, TargetTable], safe=True)

        MyTable.delete().execute()
        TargetTable.delete().execute()

        # manually create a trigger
        trig = Trigger('mytable_after_insert', (TriggerWhen.After, TriggerAction.Insert), MyTable, safe=True)
        trig.add_sql('INSERT INTO target_table (id__id, half_float_num) VALUES (NEW.id_, NEW.float_num / 2)')
        database.execute_sql(trig.create())

        # add some data for testing to the first table
        data = []
        for i in range(100):
            data.append(dict(integer=random.randint(i, 10 * i), float_num=random.gauss(i, 2 * i)))
        MyTable.insert_many(data).execute()

        # check that the target table got the right entries
        for row in MyTable.select(MyTable.float_num, TargetTable.half_float_num).join(TargetTable).namedtuples():
            assert row.float_num == 2 * row.half_float_num

        assert MyTable.select().count() == TargetTable.select().count()


In lines 20 - 22, we create a trigger and we ask the database to execute the generated SQL statement.

We insert 100 rows using the insert many class method and the trigger is doing its job in the background filling the other table. We can check that the values in the two tables are matching our expectations.

The drawback of this approach is that you may have triggers created all around your code, making your code a bit messy.

Model embedded triggers
^^^^^^^^^^^^^^^^^^^^^^^

An alternative approach is to define the trigger within the Model class, allowing it to be created simultaneously with model table. This is demonstrated in the code example below.

.. code-block:: python
    :linenos:
    :name: test_automatically_created_trigger
    :caption: A test Trigger created within the Model
    :emphasize-lines: 8-13,22

    # the trigger is directly defined in the class.
    class MyTable(MAFwBaseModel):
        id_ = AutoField(primary_key=True)
        integer = IntegerField()
        float_num = FloatField()

        @classmethod
        def triggers(cls):
            return [
                Trigger('mytable_after_insert', (TriggerWhen.After, TriggerAction.Insert), cls, safe=True).add_sql(
                    'INSERT INTO target_table (id__id, half_float_num) VALUES (NEW.id_, NEW.float_num / 2)'
                )
            ]

    class TargetTable(MAFwBaseModel):
        id_ = ForeignKeyField(MyTable, on_delete='cascade', primary_key=True, backref='half')
        half_float_num = FloatField()

    database: Database = SqliteDatabase(':memory:', pragmas=default_conf['sqlite']['pragmas'])
    database.connect()
    database_proxy.initialize(database)
    database.create_tables([MyTable, TargetTable], safe=True)

This approach is much cleaner. The Trigger is stored directly in the Model (lines 8 - 13). In the specific case, the triggers method returned one trigger only, but you can return as many as you like. When the tables are created (line 22), all the triggers will also be created.

In the example above, you have written the SQL statement directly, but nobody is preventing you to use :link:`peewee` queries for this purpose. See below, how exactly the same trigger might be re-written, using an insert statement:

.. code-block:: python
    :linenos:
    :name: test_automatically_created_trigger_with_peewee_query
    :caption: A test Trigger created within the Model using an Insert statement
    :emphasize-lines: 9, 13-14

    class MyTable(MAFwBaseModel):
        id_ = AutoField(primary_key=True)
        integer = IntegerField()
        float_num = FloatField()

        @classmethod
        def triggers(cls):
            trigger = Trigger('mytable_after_insert', (TriggerWhen.After, TriggerAction.Insert), cls, safe=True)
            sql = TargetTable.insert(id_=SQL('NEW.id_'), half_float_num=SQL('NEW.float_num/2'))
            trigger.add_sql(sql)
            return [trigger]

        class Meta:
            depends_on = [TargetTable]

The key point here is at line 9, where the actual insert statement is generated by :link:`peewee` (just for your information, you have generated the statement, but you have not *execute it*) and added to the existing trigger.

In the last two highlighted lines, we are overloading the Meta class, specifying that MyTable, depends on TargetTable, so that when the create_tables is issued, they are built in the right order. This is not necessary if you follow the previous approach because the trigger will be very likely executed only after that the tables have been created.

.. warning::

    Even though starting from MAFw release v1.1.0, triggers are now properly generated for the three main :ref:`database backends <trigger_on_different_dbs>`, its use has been deeply tested only with SQLite. For this reason, we (MAFw developers) encourage the user community to work also with other DBs and, in case, submit bugs or feature request.


Disabling triggers
^^^^^^^^^^^^^^^^^^

Not all database implementations provide the same option to temporarily disable one or more triggers. In order to cope with this limitation, MAFw is providing a general solution that is always working independently of the concrete implementation of the database.

The standard SQL trigger definition allows to have one or more WHEN clauses [#]_, meaning that the firing of a trigger script might be limited to the case in which some other external conditions are met.

In order to achieve that, we use one of our :ref:`standard tables <std_tables>`, that are automatically created in every MAFw database.

This is the TriggerStatus table as you can see it in the snippet below:

.. literalinclude:: ../../src/mafw/db/std_tables.py
    :dedent:
    :pyobject: TriggerStatus
    :name: TriggerStatus
    :caption: TriggerStatus model


You can use the ``trigger_type`` column to specify a generic family of triggers (DELETE/INSERT/UPDATE) or the name of a specific trigger. By default a trigger is active (status = 1), but you can easily disable it by changing its status to 0.

To use this functionality, the Trigger definition should include a WHEN clause as described in this modified model definition.

.. code-block:: python
    :name: MyTableTriggerWhen
    :caption: Trigger definition with when conditions.

    class MyTable(MAFwBaseModel):
        id_ = AutoField(primary_key=True)
        integer = IntegerField()
        float_num = FloatField()

        @classmethod
        def triggers(cls):
            return [
                Trigger('mytable_after_insert', (TriggerWhen.After, TriggerAction.Insert), cls, safe=True)
                .add_sql('INSERT INTO target_table (id__id, half_float_num) VALUES (NEW.id_, NEW.float_num / 2)')
                .add_when('1 == (SELECT status FROM trigger_status WHERE trigger_type == "INSERT")')
            ]

.. _trigger_on_different_dbs:

Triggers on different databases
+++++++++++++++++++++++++++++++

We have seen that Peewee provides an abstract interface that allows interaction with various SQL databases
like :link:`MySQL`, :link:`PostgreSQL`, and :link:`SQLite`.

This abstraction simplifies database operations by enabling the same codebase to work across different
database backends, thanks to the common SQL language they all support. However, while these databases share SQL as
their query language, they differ in how they handle certain features, such as triggers. Each database has its own
peculiarities and syntax for defining and managing triggers, which can lead to inconsistencies when using a single
approach across all databases.

To address this challenge, the MAFw introduced the :class:`.TriggerDialect` abstract class and three specific
implementations for the main databases. Relying on the use of the TriggerDialect class, a syntactically correct SQL
statement for the creation or removal of triggers is generated. But, MAFw cannot read the mind of the user (yet!) and
given the very different behaviour of the databases, the operation of the triggers will be different.

Have a look at the table below for an illustrative comparison on how triggers are handled by the different databases.

.. list-table::
    :width: 100%
    :widths: 15 28 28 28
    :header-rows: 1
    :stub-columns: 1
    :class: wrap-table

    * - Feature
      - MySQL
      - PostgreSQL
      - SQLite
    * - Trigger Event
      -  - INSERT
         - UPDATE
         - DELETE
      -  - INSERT
         - UPDATE
         - DELETE
         - TRUNCATE
      -  - INSERT
         - UPDATE
         - DELETE
    * - Trigger Time
      - - BEFORE
        - AFTER
      - - BEFORE
        - AFTER
        - INSTEAD OF
      - - BEFORE
        - AFTER
        - INSTEAD OF
    * - Activation
      - Row-level only
      - Row-level and statement-level
      - Row-level and statement-level
    * - Implementation
      - BEGIN-END block with SQL statements
        (supports non-standard SQL like SET statements)
      - Functions written in PL/pgSQL, PL/Perl, PL/Python, etc.
      - BEGIN-END block with SQL  statements
    * - Trigger Per Event
      - Multiple triggers allowed ordered by creation time
      - Multiple triggers allowed ordered alphabetically by default, can be specified
      - Multiple triggers allowed but unspecified execution order
    * - Privileges required
      - TRIGGER privilege on the table and SUPER or SYSTEM_VARIABLES_ADMIN for DEFINER
      - CREATE TRIGGER privilege on schema and TRIGGER privilege on table
      - No specific privilege model
    * - Foreign Key Cascading
      - Cascaded foreign key actions do not activate triggers
      - Triggers are activated by cascaded foreign key actions
      - Triggers are activated by cascaded foreign key actions
    * - Disabled/Enabled Trigger
      - Yes, using ALTER TABLE ... DISABLE/ENABLE TRIGGER
      - Yes, using ALTER TABLE ... DISABLE/ENABLE TRIGGER
      - No direct mechanism to disable

PostgreSQL offers the most comprehensive trigger functionality, with built-in support for both row-level and
statement-level triggers, INSTEAD OF triggers for views, and the widest range of programming languages for
implementation. Its trigger functions can be written in any supported procedural language, providing considerable
flexibility.

MySQL implements triggers using SQL statements within BEGIN-END blocks and only supports row-level
triggers. It allows non-standard SQL statements like SET within trigger bodies, making it somewhat more flexible for
certain operations. A critical limitation is that MySQL triggers are not activated by cascaded foreign key actions,
unlike the other databases. This is a strong limiting factor and the user should consider it when designing the
database model to store their data. In this case, it might be convenient to not rely at all on the cascading
operations, but to have dedicated triggers for this purpose.

SQLite provides more trigger capabilities than it might initially appear. While its
implementation is simpler than PostgreSQL's, it supports both row-level and statement-level triggers (statement-level
being the default if FOR EACH ROW is not specified). Like PostgreSQL, SQLite triggers are activated by cascaded
foreign key actions, which creates an important behavioral difference compared to MySQL.

When designing database applications that may need to work across different database systems, these implementation
differences can lead to subtle bugs, especially around foreign key cascading behavior. MySQL applications that rely
on triggers not firing during cascaded operations might behave differently when migrated to PostgreSQL or SQLite.
Similarly, applications that depend on statement-level triggers will need to be redesigned when moving from
PostgreSQL or SQLite to MySQL.

All so said, even though MAFw provides a way to handle triggers creation and removal in the same way across all the
databases, the user who wants to move from one DB implementation to the other should carefully review the content of
the trigger body to ensure that the resulting behavior is what is expected.

.. _std_tables:

Standard tables
---------------

In the previous section, we discussed a workaround implemented by MAFw to address the limitations of database backends that cannot temporarily disable trigger execution. This is achieved querying a table where the status of a specific trigger or a family of triggers can be toggled from active to inactive and vice-versa.

This :class:`~mafw.db.std_tables.TriggerStatus` model is one of the so-called MAFw standard tables, it is to say models that will be silently created by the execution of a |processor|. In other words, as soon as you connect to a database using the MAFw infrastructure, all those tables will be created so that all processors can benefit from them.

Along with the TriggerStatus, there are two other relevant standard tables: the :class:`~mafw.db.std_tables.OrphanFile` and the :class:`~mafw.db.std_tables.PlotterOutput`.


    :class:`~mafw.db.std_tables.OrphanFile`: the house of files without a row

        This table can be profitably used in conjunction with Triggers. The user can define a trigger fired when a row in a table is deleted. The trigger will then insert all file references contained in the deleted row into the OrphanFile model.

        The next time a processor (it does not matter which one) having access to the database is executed, it will query the full list of files from the :class:`~mafw.db.std_tables.OrphanFile` and remove them.

        This procedure is needed to avoid having files on your disc without a reference in the database. It is kind of a complementary cleaning up with respect to :func:`another function <mafw.tools.file_tools.remove_widow_db_rows>` you will discover in a moment.

        Additional details about this function are provided directly in the :func:`API <mafw.processor.Processor._remove_orphan_files>`.

    :class:`~mafw.db.std_tables.PlotterOutput`: where all figures go.

        :class:`Plotters <mafw.processor_library.plotter.GenericPlotter>` are special |processor| subclasses with the goal of generating a graphical representation of some data you have produced in a previous step.

        The output of a plotter is in many cases one or more figure files and instead of having to define a specific table to store just one line, MAFw is providing a common table for all plotters where they can store the reference to their output files linked to the plotter name.

        It is very useful because it allows the user to skip the execution of a plotter if its output file already exists on disc.

        Triggers are again very relevant, because when a change is made in the data used to generate a plotter output, then the corresponding rows in this table should also be removed, in order to force the regeneration of the output figures with the updated data.


The role of those tables is to support the functionality of the general infrastructure and not of a single processor. If your processor needs a specific table, then it is its responsibility to create it. If all your processors need to have access to certain tables, then you may consider having them added to the standard tables.

In this case, you can follow the same plugin approach you used for sharing your processors.

First, you need to create the model classes, possibly inheriting from :class:`~mafw.db.std_tables.StandardTable` and then you need to export it in the plugin.py module.

Here below is an example:

.. tab-set::

    .. tab-item:: my_std_tables.py

        .. code-block:: python
            :name: my_std_tables.py

            from peewee import AutoField, TextField
            from mafw.db.std_tables import StandardTable

            class AnotherExtraTable(StandardTable):
                main_id = AutoField(primary_key=True)
                interesting_field = TextField()

                @classmethod
                def init(cls)
                    # implement here some optional initialisation code.
                    # it will be performed everytime the connection to the database is opened from MAFw.
                    pass

    .. tab-item:: plugins.py

        .. code-block:: python
            :name: plugins.py

            import mafw
            import my_package.my_std_table

            @mafw.mafw_hookimpl
            def register_standard_tables() -> list:
                return [my_package.my_std_table.AnotherExtraTable]

    .. tab-item:: pyproject.toml

        .. code-block:: toml
            :name: pyproject.toml

            # your standard pyproject goes here
            # be sure to add this entry point
            [project.entry-points.'mafw']
            my_package = 'my_package.plugins'

.. note::

    Keep in mind, that your extra standard tables will be added only when your processor will be executed by the :ref:`mafw executable <doc_runner>`, that means that if you write your own main script to execute a processor or a processor list, this will not load the plugin imported tables.

.. _mafw_fields:

Custom fields
-------------

We have seen in a previous section that there are plenty of field types for you to build up your model classes and that it is also possible to add additional `ones <http://docs.peewee-orm.com/en/latest/peewee/models.html#fields>`_. We have made a few for you that are very useful from the point of view of MAFw. The full list is available :mod:`here <mafw.db.fields>`.

The role of the database in MAFw is to support the input / output operation. You do not need to worry about specifying filenames or paths. Simply instruct the database to retrieve a list of items, and it will automatically provide the various processors with the necessary file paths for analysis.

With this in mind, we have created a :class:`~mafw.db.fields.FileNameField`, that is the evolution of a text field accepting a Path object as a python type and converting it into a string for database storage. On top of :class:`~mafw.db.fields.FileNameField`, we have made :class:`~mafw.db.fields.FileNameListField` that can contain a list of filenames. This second one is more appropriate when your processor is generating a group of files as output. The filenames are stored in the database as a ';' separated string, and they are seen by the python application as a list of Path objects.

Similarly, we have also a :class:`~mafw.db.fields.FileChecksumField` to store the string of hexadecimal characters corresponding to the checksum of a file (or a list of files). From the python side, you can assign either the checksum directly, as generated for example by :func:`~mafw.tools.file_tools.file_checksum` or the path to the file, and the field will calculate the checksum automatically.

The :class:`~mafw.db.fields.FileNameField` and :class:`~mafw.db.fields.FileNameListField` accept an additional argument in their constructor, called ``checksum_field``. If you set it to the name of a :class:`~mafw.db.fields.FileChecksumField` in the same table, then you do not even have to set the value of the checksum field because this will be automatically calculated when the row is saved.

With these custom fields in mind, our initial definition of a :ref:`File table <file_first>`, can be re-factored as follows:

.. code-block:: python
    :name: file_second
    :linenos:

    from peewee import AutoField

    from mafw.db.db_model import MAFwBaseModel
    from mafw.db.fields import FileNameField, FileChecksumField

    class File(MAFwBaseModel):
        file_id = AutoField(primary_key=True, help_text='The primary key')
        file_name = FileNameField(checksum_field='file_digest', help_text='The full filename')
        file_digest = FileChecksumField(help_text='The hex digest of the file')

Pay attention at the definition of the file_name field. The FileNameField constructor takes an optional parameter ``checksum_field`` that is actually pointing to the variable of the FileChecksumField.

You can use the two custom fields as normal, for example you can do:

.. code-block:: python
    :linenos:
    :emphasize-lines: 5,6

    new_file = File()
    # you can assign a Path object.
    new_file.file_name = Path('/path/to/some/file')
    # the real checksum will be calculated automatically.
    # this next line is totally optional, you can leave it out and it will work in the same way.
    new_file.file_digest = Path('/path/to/some/file')

The super power of these two custom fields is that you can remove useless rows from the database, just issuing one command.

Removing widow rows
+++++++++++++++++++
Due to its I/O support, the database content should always remain aligned with the files on your disc. If you have a row in your database pointing to a missing file, this may cause troubles, because sooner or later, you will try to access this missing file causing an application crash.

In MAFw nomenclature, those rows are called *widows*, following a similar concept in `typesetting <https://en.wikipedia.org/wiki/Widows_and_orphans>`_, because they are a fully valid database entry, but their data counter part on disc disappeared.

To avoid any problem with widow rows, MAFw is supplying a :func:`function <mafw.tools.file_tools.remove_widow_db_rows>` that the processor can invoke in the start method on the Model classes used as input:

.. code-block:: python

    class MyProcessor(Processor):

        def start():
            super().start()
            remove_widow_db_rows(InputData)

The :func:`~mafw.tools.file_tools.remove_widow_db_rows` will check that all the :class:`~mafw.db.fields.FileNameField` fields in the table are pointing to existing files on disc. If not, then the row is removed from the database.

The function is not automatically called by any of the Processor super methods. It is up to the user to decide if and when to use it. Its recommended use is in the overload of the :meth:`~.Processor.start` method or as a first action in the :meth:`~.Processor.get_items` in the case of a *for loop* workflow, so that you are sure to re-generate the rows that have been removed.

Pruning orphan files
++++++++++++++++++++
The opposite situation is when you have a file on disc that is not linked to an entry in the database anymore. This situation could be even more perilous than the previous one and may occur more frequently than you realize. The consequences of this mismatch can be severe, imagine that during the *testing / development phase* of your |processor| you generate an output figure saved on disc. You then realize that the plot is wrong and you fix the bug and update the DB, but for some reasons you have forgotten to delete the figure file from the disc. Afterwards, while looking for the processor output, you find this file and believe it is a valid result and you use it for your publication.  In order to prevent this to happen, you just have to follow some simple rules, and then the reliable machinery of MAFw will do the rest.

The key point is to use a specific trigger in every table that has a file name field. This trigger has to react before any delete query on such a table and inserting all FileNameFields or FileNameListFields in the OrphanFile table. You will see an example of such a trigger in the next paragraphs. This standard tables will be queried by the next processor being executed and during the start super method, all files in the Orphan table will be removed from the disc.

Let us try to understand this better with a step-by-step example. For simplicity, we have removed the import statements from the code snippet, but it should not be too difficult to understand the code anyway.

We begin with the declaration of our input model:

.. literalinclude:: ../../tests/test_db.py
    :dedent:
    :pyobject: test_full_orphan
    :name: FileWithTrigger
    :caption: File model definition with trigger
    :start-at: class File(MAFwBaseModel):
    :end-at: depends_on = [OrphanFile]

Here you see the trigger definition: it is a before delete type and when triggered it is adding the filename field to the OrphanFile table. It is important to notice that this trigger has a when condition and will only be executed when the trigger type DELETE_FILES is enabled. This is necessary for the pruning mechanism to work, just copy this line in your trigger definition.

And now let us define some fake processors. First we import some files into our model, then we remove some rows from the file table and finally other two processors, doing nothing but useful to demonstrate the effect of the orphan removal.

.. literalinclude:: ../../tests/test_db.py
    :dedent:
    :pyobject: test_full_orphan
    :name: ProcessorDefinition
    :caption: Some example processors
    :start-after: # processor definition
    :end-before: # end of processor definition

The **FileImporter** [#]_ is very simple, it reads all dat files in a directory and loads them in the File model along with their checksum. Just to be sure we empty the File model in the start and in the finish we check that the number of rows in File is the same as the number of files in the folder.

The **RowRemover** is getting an integer number of rows to be removed. Even though the File model is already created, it is a good practice to repeat the statement again in the start method. Then we select some random rows from File and we delete them. At this point, we have created some orphan files on disc without related rows in the DB.
Finally (in the finish method), we verify that the number of remaining rows in the database aligns with our expectations. Additionally, we ensure that the trigger functioned correctly, resulting in the appropriate rows being added to the OrphanFile model.

The **OrphanProtector** does even less than the others. But if you look carefully, you will see that along with the :func:`~mafw.decorators.database_required` there is also the :func:`~mafw.decorators.orphan_protector` decorator. This will prevent the processor to perform the check on the OrphanFile model and deleting the unrelated files.
In the start method, we record the number of orphan files in the OrphanFile model and we confirm that they are still there in the finish. Since the actual removal of the orphan files happens in the processor start method, we need to count the number of orphans before calling the super start.

The **LazyProcessor** is responsible to check that there are no rows left in the OrphanFile, meaning that the removal was successful.

And now let us put everything together and run it.

.. literalinclude:: ../../tests/test_db.py
    :dedent:
    :pyobject: test_full_orphan
    :name: execution
    :caption: ProcessorList execution
    :start-at: db_conf = default_conf['sqlite']
    :end-at: assert lazy.processor_exit_status == ProcessorExitStatus.Successful

In practice, the only thing you have to take care of is to add a dedicated trigger to each of your tables having at least a file field and then the rest will be automatically performed by MAFw.

.. _verify_checksum:

Keeping the entries updated
+++++++++++++++++++++++++++
One aspect is that the file exists; another is that the file content remains unchanged. You may have replaced an input file with a newer one and the database will not know it. If your processors are only executed on items for which there is still no output generated, then this replaced file may go unnoticed causing issues to your analysis.

For this reason, we are strongly recommending to always add a checksum field for each file field in your table. Calculating a checksum is just a matter of a split second on modern CPU while the time for the debugging your analysis code is for sure longer.

The function :func:`~mafw.tools.file_tools.verify_checksum` takes a Model as argument and will verify that all checksums are still valid. In other words, for each FileNameField (or FileNameListField) with a link to a checksum field in the table, the function will compare the actual digest with the stored one. If it is different, then the DB row will be removed.

Also this function is not automatically called by any processor super methods. It is ultimately the user's responsibility to decide whether to proceed, bearing in mind that working with long tables and large files may result in delays in processor execution.

The implementation is very similar to the previous one, just change the function name. Keep in mind that the :func:`~mafw.tools.file_tools.verify_checksum` will implicitly check for the existence of files and warn you if some items are missing, so you can avoid the :func:`~mafw.tools.file_tools.remove_widow_db_rows`, if you perform the checksum verification.

.. code-block:: python

    class MyProcessor(Processor):

        def start():
            super().start()
            verify_checksum(InputData)



.. _filters:

Filters: let us do only what is needed to be done!
--------------------------------------------------

As mentioned already several times, the main role of the database is to support the processor execution in providing the input items and in storing the output products. Not everything can be efficiently stored in a database, for example large chunk of binary data are better saved to the disc, in this case, the database will know the path where these data are stored.

One advantage of the database is that you can apply selection rules and you do not have to process the whole dataset if you do not need it. To help you in this, MAFw is offering you a ready to use solution, the :class:`~mafw.db.db_filter.Filter` class. This is an object that you can configure via the steering file allowing you to run the processors only over the items passing the criteria you set.

How to configure a filter
+++++++++++++++++++++++++

In a steering file, there is a table for each processor where you can set the configurable active and passive parameters. To this table, you can add a sub-table named Filter, containing other tables, one for each input Model. This is how it will look like:

.. code-block:: toml

    [GlobalFilter]
    new_only = true

    [MyProcessor]
    param1 = 15

    [MyProcessor.Filter.InputTable1]
    resolution_value = 25

    [MyProcessor.Filter.InputTable2]
    sample_name = 'sample_1'

In the example above, MyProcessor has two \*.Filter.\* tables, one for InputTable1 and one for InputTable2. When the steering file will be parsed, the processor constructor will automatically generate two filters: for InputerTable1 it will put a condition that the resolution field must be 25 and for InputTable2, the sample_name column should be 'sample_1'. If MyProcessor is using other tables for generating the input items, you could add them in the same way.

There is also an additional table named **GlobalFilter** where you can specify conditions that will be applied by default to all processors being executed. If the same field is specified in both the GlobalFilter and the Processor/Model specific one, the one in the Processor/Model will overrule the global one.

For the global filter, we can specify a magic boolean keyword ``new_only == true`` [#]_. This will allow to implement a different input sequence considering only items for which an output does not exist.

How to use a filter
+++++++++++++++++++
Let us put in practice what we have seen so far. The filter native playground is in the implementation of the :meth:`~mafw.processor.Processor.get_items` method.

Let us assume that our |processor|, named AdvProcessor, is using three models to obtain the item lists. Everything is nicely described in the `ERD <https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model>`_ below. The three models are interconnected via foreign key relations. There is a fourth model, that is where the output data will be saved.

.. figure:: /_static/images/db/advanced_db-ERD.png
    :width: 600
    :align: center
    :alt: Model ERD

    The ERD of the AdvProcessor.

The real core of our database is the image table, where our data are first introduced, the other two on the right, are kind of helper tables storing references to the samples and to the resolution of our images. The processed_image table is where the output of our AdvProcessor will be stored.

To realize this database with our ORM we need to code the corresponding model classes as follows:

.. literalinclude:: ../../tests/test_filter.py
    :linenos:
    :dedent:
    :pyobject: advanced_models
    :start-at: class Sample(MAFwBaseModel):
    :end-at: value = FloatField(default=0)
    :emphasize-lines: 13-18, 21-29

By now, you should be an expert in ORM and everything there should be absolutely clear, otherwise, take your chance now to go back to the previous sections or to the :link:`peewee` documentation to find an explanation. Note how the Image class is making use of our :class:`~mafw.db.fields.FileNameField` and :class:`~mafw.db.fields.FileChecksumField`. We added also a bit of help text to each field, in order to make even more evident what they are. For each foreign key field, we have specified a backref field, so that you could get access to the related models. Pay attention also at the highlighted lines, where we define foreign key fields to other tables. :link:`Peewee` follows Django style `references <https://stackoverflow.com/a/79272223/561243>`_, so actually the field object is named with the noun of the object you are referring to. This will allow the following:

.. code-block:: python

    image.sample # Resolve the related object returning a Sample instance, it costs an additional query
    image.sample_id # Return the corresponding Sample's id number


The primary source of input is the Image; however, you may wish to process only images that meet specific criteria, such as belonging to a particular sample or being captured at a certain resolution. Unfortunately, this information is not explicitly included in the Image model. Only the resolution_id and the sample_id are included in the image table: those primary keys are excellent for a computer, but for a human being it is better to use sample names and resolution values. The solution is to use a `join query <https://www.w3schools.com/sql/sql_join.asp>`_ in order to have all fields available and then we will be able to apply the configurable filters from the TOML steering file to limit the selection to what we want. We have three input models, so we may have up to three filters defined in the configuration file, along with the GlobalFilter. The processor, during its construction, will build the filters with the configuration information and store them in the processor :class:`filter register <mafw.db.db_filter.FilterRegister>`.

Let us have a look at a possible implementation of the :meth:`~mafw.processor.Processor.get_items` for our advanced processor.

.. tab-set::

    .. tab-item:: python

        .. code-block:: python
            :linenos:
            :name: get_items
            :emphasize-lines: 16, 21, 33-39

            def get_items(self):

                # first of all, let us be sure that the tables exist
                # the order is irrelevant, the ORM will find the best creation strategy.
                # if the table already exists, nothing will happen.
                self.database.create_tables([Sample, Resolution, Image, ProcessedImage])

                # if you want to remove widow rows from the output table or verify the checksum do it now!
                remove_widow_rows([Image, ProcessedImage])

                # bind all input table filters
                # this will establish a physical connection between the filter and
                # the corresponding ORM model.
                # the order of the model in the list is irrelevant.
                # list all input models.
                self.filter_register.bind_all([Sample, Resolution, Image])

                # let us get a list of all already processed items.
                # since the item in the output table are stored using the same primary key,
                # this will simplify the discrimination between new and already processed items.
                existing_entries = ProcessedImage.select(ProcessedImage.image_id).execute()

                # did we select new_only in the global filter?
                # if yes, prepare an additional condition in which we specify that the
                # Image.image_id should not be among the image_id of the ProcessedImage.
                # if no, then just accept everything.
                if self.filter_register.new_only:
                    existing = ~Image.image_id.in_([i.image_id for i in existing_entries])
                else:
                    existing = True

                # finally let us make the query.
                query = (Image.select(Image, Sample, Resolution)
                             .join(Sample, on=(Image.sample_id == Sample.sample_id), attr='s')
                             .switch(Image)
                             .join(Resolution, on=(Image.resolution_id == Resolution.resolution_id), attr='r')
                             .where(self.filter_register.filter_all())
                             .where(existing)
                         )
                return query

    .. tab-item:: TOML

        .. code-block:: toml
            :linenos:
            :name: configuration_1

            [GlobalFilter]
            new_only = true

            [AdvProcessor.Filter.Sample]
            sample_name = 'Sample_0000[123]'

            [AdvProcessor.Filter.Resolution]
            resolution_value = 50

            [AdvProcessor.Filter.Image]
            filename = '\*file_0[12345]0\*'

The comments in the code make it rather self explanatory, but let us have a look together at the key points.

    - At line 16, we are binding the filters in the filter register with the model classes. The filter register contains all the filters that were found in the  configuration file, and since their presence in the steering file is optional, you may have decided not to include all model specific filters. In such a case, the :meth:`~mafw.db.db_filter.FilterRegister` will create an empty filter for the missing models using the global filter as default values.

    - At line 21, we query the output table to get the list of already existing output. Since the input and output images are sharing the same primary key, this will make the identification of new items very easy. If the DB structure was not built in this way, you will have to work out a solution to find which are the new items.

    - The list of items is finally retrieved in the lines 33 to 39. We select not only from Image, but we join also Sample and Resolution. In the join statement we specify the target Model and the relation to align the two models. Theoretically, if the two models are linked by a foreign key relation, then the ``on`` attribute could be skipped, but we like when everything is clearly stated. We will come back to the ``attr`` in a second.

    - Lines 37 and 38 is where the filter gets into action, exactly in the where clause. First we ask at the ``filter_register`` to generate the filter statement for each of the filters it is holding and then we select according to the existence criteria.

In this specific situation (*just click on the TOML configuration tab to see the filter configuration*), the filter_all condition will be equivalent of writing:

.. code-block:: python

    (Sample.sample_name % 'Sample_0000[123]') &
        (Resolution.resolution_value == 50) &
        (Image.filename % '\*file_0[12345]0\*')

where the `%` operator [#]_ is the `SQL GLOB <https://www.sqlite.org/lang_expr.html#glob>`_.

In the last line, we return the query, that is an iterable object, so actually our looping processor will assign to the :attr:`~mafw.processor.Processor.item` attribute the value of one selected and filtered row after the other. The item will then be a modified version of the Image class. You will be able to access the image table columns directly using the dot notation, and, at the same time, you can access the two joined tables via the two ``attr`` fields, that you have specified in the join statement.

So for example, this will be a valid syntax:

.. code-block:: python

    print(self.item.filename.name) # print the file name (without the path) of the image
    print(self.item.s.sample_name) # print the sample name, look at the .s in between
    print(self.item.r.resolution_value) # print the value of the resolution. look at the .r in between

.. admonition:: Avoiding the N+1 problem

    Since the Image table has foreign key dependency from Sample and Resolution, you could theoretically access the referenced row via the ``backref`` attribute, but this will trigger an additional query every time. The impact of those additional queries can be excessive especially if the tables are large. This is the so-called `N+1 problem in ORM <https://docs.peewee-orm.com/en/latest/peewee/relationships.html#avoiding-the-n-1-problem>`_. On the contrary, if you use the s and r attributes, no additional queries will be performed.

Multi-primary key columns
-------------------------

Special attention is required when you need to have a primary key that is spanning over two or more columns of your model. So far we have seen how we can identify one column in the model as the primary key and now we will see what to do if you want to use more than one column as primary key and, even more important, how you can use this composite primary key as a foreign key in another model.

To describe this topic, we will make use of an example that you can also find in the examples modules of MAFw named :mod:`~mafw.examples.multi_primary`.

Let us start with the model definition.

.. literalinclude:: ../../src/mafw/examples/multi_primary.py
    :linenos:
    :dedent:
    :start-at: class Sample(MAFwBaseModel):
    :end-before: # end of model
    :emphasize-lines: 35-50, 57-58, 53-55, 72-77

As always, one single picture can convey more than a thousand lines of code. Here below the ERDs of Image and of CalibratedImage.

.. figure:: /_static/images/db/multi-erd1.png
    :width: 600
    :align: center
    :alt: Image ERD

    The ERD of the Image Model

.. figure:: /_static/images/db/multi-erd2.png
    :width: 600
    :align: center
    :alt: CalibratedImage ERD

    The ERD of the CalibratedImage Model

In the diagrams, the fields with bold font represent primary keys, also highlighted by the separation line, while the arrow are the standard relation.

As in the examples above, we have images of different samples acquired with different resolutions entering the Image model. We use those lines to make some calculations and we obtain the rows in the ProcessedImage model. These two tables are in 1 to 1 relation and this relation is enforced with a delete cascade, meaning that if we delete an element in the Image model, the corresponding one in the ProcessedImage will also be deleted.

The CalibrationMethod model contains different sets of calibration constants to bring each row from the ProcessedImage model to the CalibratedImage one. It is natural to assume that the ``image_id`` and the ``method_id`` are the best candidates to be a combined primary key.
To achieve this, in the CalibratedImage model, we need to add (line 57-58) an overload of the Meta class, where we specify our ``CompositeKey``. Pay attention to an important detail: the CompositeKey constructor takes the name of the fields and not the name of the columns, that in the case of foreign keys differ of '_id'. Optionally we can also define a primary_key property (line 53-55) to quickly retrieve the values of our keys.

From the application point of view, we want all the processed images to be calibrated with all possible calibration methods, that means we need to make a cross join as described below:

.. literalinclude:: ../../src/mafw/examples/multi_primary.py
    :linenos:
    :dedent:
    :start-after: # make the multi calibration
    :end-at: calibrated_image.save(force_insert=True)


Up to this point we have seen what we have to do to specify a composite primary key, we cannot use the AutoField or the primary_key parameter, but we need to go through the Meta class in the way shown in the example.

The next step is to have another table (ColoredImage in our imaginary case) that is in relation with CalibratedImage. We would need to have again a composite primary key that is also a composite foreign key. :link:`Peewee` does not support composite foreign keys, but we can use the workaround shown at lines 72-77. Along with the CompositeKey definition, we need to add a Constraint as well using the SQL function to convert a string into a valid SQL statement. This time, since we are using low level SQL directives, we have to use the column names (additional '_id') instead of the field name.

And in a similar way we can insert items in the ColoredImage model.

.. literalinclude:: ../../src/mafw/examples/multi_primary.py
    :linenos:
    :dedent:
    :start-after: # fill in the ColoredImage
    :end-at: colored_image.save(force_insert=True)

Now, with all the tables linked to each other, try to delete one from a table, and guess what will happen to all other tables.

This tutorial might be a bit more complex than the examples we have seen so far, but we believed you have appreciated the power of such a relational tool.

Importing an existing DB
------------------------

The last section of this long chapter on database will show you how to deal with an existing DB. It is possible that before you have adopted MAFw for your analysis tasks, you were already employing a relational database to store your dataset and results. So far we have seen how to create tables in a database starting from an object oriented description (a model) in a python library. But what do we have to do if the database already exists? Can we create the classes starting from a database? This process goes under the name of **reflection** and it is the subject of this section.

The reflection of tables in python classes cannot be performed automatically at 100% by definition. A typical case is the use of application specific fields. Consider, for example, the FileNameField that we have discussed earlier. This field corresponds to a Path object when you look at it from the application point of view, but the actual path is saved as a text field in the concrete database implementation. If you now read the metadata of this table from the database point of view, you will see that the field will contain a text variable and thus the reflected class will not have any FileNameField.

Let us try to understand the process looking at the picture below. If we create the model in python, then we can assign special field descriptors to the table columns, but their concrete implementation in the database must be done using types that are available in the database itself. So when we perform the reverse process, we get only a good approximation of the initial definition.

.. figure:: /_static/images/db/reflection-original.png
    :name: reflection-original
    :width: 350
    :align: center
    :alt: Original implementation

    This is the model implementation as you would code it making use of the specific field definitions.

.. figure:: /_static/images/db/database-implementation.png
    :name: database-implementation
    :width: 150
    :align: center
    :alt: Database implementation

    During the actual implementation of the model as a database table, python column definitions will be translated into database types.

.. figure:: /_static/images/db/reflection-reflected.png
    :name: reflection-reflected
    :width: 350
    :align: center
    :alt: Reflected implementation

    The reflection process will translate the database implementation in a generic model implementation, not necessarily including all the specific field definition.

Nevertheless the process is rather efficient and can generate an excellent starting point that we can use to customize the model classes to make them more useful in our application.

From a practical point of view, you just have to open a console and type the command ``mafw db wizard --help`` to get some help on the tool and also read its `documentation <generated/mafw.scripts.mafw_exe.html#mafw-db-wizard>`_. You need to provide the name of the database and how to connect to it, in the case of Sqlite DB, it is enough to provide the filename, and you have to specify the name of the output python file that will contain all the model classes. This module is ready to go, you could theoretically import it into your project and use it, but it is strongly recommended to accurately check that everything is really the way you want it to be.

The reflection process is absolutely safe for your existing database, so it is worth to give it a try!

What's next
-----------

Congratulations! You reached the end of the most difficult chapter in this tutorial. It is difficult because as a scientist you might not be used to deal with databases everyday, but their power is incredible, isn't it?

The next chapter is about the library of advanced processors that MAFw is sharing to simplify your job even further. In particular, we are sure you will like a lot our plotting processors!

.. rubric:: Footnotes

.. [#] MySQL does not directly support adding WHEN conditions to the trigger, but a similar behaviour is obtainable using an IF statement in the trigger SQL body. This adaptation is automatically implemented by the :class:`~.MySQLDialect`.

.. [#] A much better implementation of an Importer could be achieved using a subclass of the :class:`~.Importer`. See, for example, the :class:`~.ImporterExample` class and its :ref:`documentation <importer>`.

.. [#] Remember that in TOML, the two booleans are **NOT** capitalized as in Python. Moreover, you can specify new_only also in Processor/Model but it will not be taken into account unless that model has a column named new_only.

.. [#] The list of all overloaded operator and special method is available in the `peewee doc <https://docs.peewee-orm.com/en/latest/peewee/query_operators.html#query-operators>`_.

