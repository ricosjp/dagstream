.. _example:

Example
========

Definition of Dag
^^^^^^^^^^^^^^^^^

DagStream class convert your functions into dag nodes.

.. code:: python
   
   import dagstream

   def funcA():
      print("funcA")

   def funcB():
      print("funcB")

   def funcC():
      print("funcC")

   def funcD():
      print("funcD")

   def funcE():
      print("funcE")

   def funcF():
      print("funcF")


   stream = dagstream.DagStream()
   # convert to functional nodes
   A, B, C, D, E, F = stream.emplace(funcA, funcB, funcC, funcD, funcE, funcF)

   # define relationship betweeen functional nodes
   A.precede(B, C)  # A executes before B and C
   E.succeed(B, C, D)  # E executes after B, C and D
   D.succeed(C)
   F.succeed(E)



Execute Dag
^^^^^^^^^^^^

After definition of relationship between functional nodes, execute all.

.. code:: python
   
    from dagstream.executes import StreamExecutor

    # construct functional dag
    functional_dag = stream.construct()
    executor = StreamExecutor(functional_dag)
    executor.run()

In console, following items are shown.

.. code:: bash

    funcA
    funcC
    funcB
    funcD
    funcE
    funcF


When executing all functions in parallel, Use StreamParallelExecutor.


.. code:: python
   
    from dagstream.executes import StreamParallelExecutor

    # construct functional dag
    functional_dag = stream.construct()
    # Run in parallel by using 4 processes
    executor = StreamParallelExecutor(functional_dag, n_processes=4)
    executor.run()


Draw mermaid object
^^^^^^^^^^^^^^^^^^^

By using MermaidDrawer, you can output dag structure to text file as mermaid style.

.. code:: python
    
    from dagstream.viewers import MermaidDrawer

    drawer.output(functional_dag, "workspace/sample.mmd")

Content of text file is shown below.


.. literalinclude:: mmds/sample.mmd
    :language: text
    :linenos:

By rendering, 

.. mermaid:: mmds/sample.mmd


Extract sub graph
^^^^^^^^^^^^^^^^^^

It is able to extract sub dag from whole one after defining relationship between functions.

.. code:: python
   
    # construct functional dag
    # Extract minimum sub dag graph which is necessary for executing B and D
    functional_dag = stream.construct(mandatory_nodes=[B, D])

    # execute as same
    executor = StreamExecutor(functional_dag)
    executor.run()

    # output as same
    drawer.output(functional_dag, "workspace/sample.mmd")


In console, following items are shown.

.. code:: bash

    funcA
    funcC
    funcB
    funcD


Drawing by mermaid, sub-dag graph is shown below.

.. mermaid:: mmds/extract.mmd

