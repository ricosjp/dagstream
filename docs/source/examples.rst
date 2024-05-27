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
      return 10

   def funcB(val_from_A: int):
      print(f"funcB, received {val_from_A} from A")

   def funcC(val_from_A: int):
      print(f"funcC, received {val_from_A} from A")
      return 20

   def funcD(val_from_C: int):
      print(f"funcD, received {val_from_C} from C")

   def funcE():
      print("funcE")

   def funcF():
      print("funcF")


   stream = dagstream.DagStream()
   # convert to functional nodes
   A, B, C, D, E, F = stream.emplace(funcA, funcB, funcC, funcD, funcE, funcF)

   # define relationship betweeen functional nodes
   
   # A executes before B and C
   # output of A passed to B and C
   A.precede(B, C, pipe=True) 
   
   # E executes after B, C and D
   E.succeed(B, C, D)

   # D executes after C
   # D receives output of C
   D.succeed(C, pipe=True)

   F.succeed(E)


Execute Dag
^^^^^^^^^^^^

After definition of relationship between functional nodes, execute all.

.. code:: python
   
   from dagstream.executor import StreamExecutor

   # construct functional dag
   functional_dag = stream.construct()
   executor = StreamExecutor(functional_dag)
   executor.run()


In console, following items are shown.

.. code:: bash

   funcA
   funcB, received 10 from A
   funcC, received 10 from A
   funcD, received 20 from C
   funcE
   funcF

When executing all functions in parallel, Use StreamParallelExecutor.


.. code:: python

   from dagstream.executor import StreamParallelExecutor

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
    drawer.output(functional_dag, "workspace/extract.mmd")


In console, following items are shown.

.. code:: bash

   funcA
   funcB, received 10 from A
   funcC, received 10 from A
   funcD, received 20 from C

Drawing by mermaid, sub-dag graph is shown below.

.. mermaid:: mmds/extract.mmd

