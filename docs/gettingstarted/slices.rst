======
Slices
======

Next to tags, slices are another fundamental concept of Raymon. A slice is simply a subset of a dataset. Slicing your (production) data provides valuable, more granular, insights than only looking at the dataset as one whole. A slice is defined by a so called slice string (:code:`slicestr`), which is a combination of filters. Any trace matching all filters in the :code:`slicestr` will be in the slice defined by that :code:`slicestr`. 

A :code:`slicestr` looks as follows:

.. code-block::

    client==bigshot && model_version>=1.0.0

The :code:`slicestr` above efines all data coming from client "bigshot", that has been tagged as processed by a model with version >= 1.0.0.

---------------
Slicing options
---------------

As already stated, a :code:`slicestr` consists out of a combination of multiple tag filters. Raymon currently supports the following tag filter options. 

.. list-table:: Tag filter options
    :widths: 25 50 25
    :header-rows: 1

    * - Tag filter
      - Description
      - Example
    * - :code:`trace(<trace_id>)`
      - Matches all traces with a given :code:`trace_id`. This should only match 1 trace. 
      - :code:`trace()`
    * - :code:`hastag(<tag_name>)`
      - Matches all traces that have a tag with the given name, whatever the value for that tag may be. 
      - :code:`hastag(client)`
    * - :code:`hastype(<tag_type>)`
      - Matches all traces that have a tag with the given type, whatever the name and value for that tag may be. 
      - :code:`hastype(error)`, :code:`hastype(profile-actual)`
    * - :code:`hasgroup(<tag_group>)`
      - Matches all traces that have a tag with the given group, whatever the name, value or type for that tag may be. 
      - :code:`hastype(client)`
    * - :code:`<tag>==<value>)`
      - Matches all traces that have a tag with the given name and a value of that tag equal to the given value. 
      - :code:`client==bigshot`
    * - :code:`<tag>!=<value>)`
      - Matches all traces that have a tag with the given name and a value of that tag not equal to the given value. 
      - :code:`client!=bigshot`
    * - :code:`<tag>>=<value>)`
      - Matches all traces that have a tag with the given name and a value of that tag greater than or equal to the given value. 
      - :code:`outlier_score>=50`, :code:`abs_error>=10`
    * - :code:`<tag><>=<value>)`
      - Matches all traces that have a tag with the given name and a value of that tag smaller than or equal to the given value. 
      - :code:`outlier_score<>=50`, :code:`abs_error<>=10`
    
-------------------
Using slices
-------------------
Slice strings have multiple uses in Raymon. A few examples what slices allow you to do:


- Fetch data in a slice (api)
- Filter data for the dashboard or trace views (web UI)
- Compare 2 slices on the dashboard view (web UI)
- Detect issues (like model accuracy issues) per slice (backend / web UI)

This is further explained in :ref:`UI Walkthrough`.


