.. dagstream documentation master file, created by
   sphinx-quickstart on Wed Jul 19 14:36:38 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

DagStream
=========

DagStream is the Python package in order to manage relationship between functions, 
especially for data-preprocessing process for machine learning applications.


Key Features
------------

- Simple method to define dag relationship
- Quick Visualization by mermaid


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



Relationship between functions are like below.


.. mermaid:: mmds/sample.mmd



License
-------

the Apache License, Version 2.0 (the "License")



.. toctree::
   :maxdepth: 1
   :caption: Contents

   examples
   reference/index.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
