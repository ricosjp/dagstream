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
