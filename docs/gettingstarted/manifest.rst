====================
The project manifest
====================

Coming soon...


.. code-block:: yaml
    :linenos:

    project_id: house_prices
    version: draft
    actions:
    map:
        - name: profile_eval
        mapper_type: profile_eval
        profile: housepricescheap@2.0.0
        inputs:
            output: pricing_prediction # Ref
            actual: actual
    visualize: # On demand
        - name: request_data
        function: pandas2html
        inputs:
            data: request_data 
        params: null
        - name: preprocessed_input
        function: pandas2html
        inputs:
            data: preprocessed_input
        params: null

    reduce:
        - reducer_type: profile_reducer
        name: housepricescheap@2.0.0

    slices:
    - slicestr: "client==Remax && app==v1.0.0"
    - slicestr: "client==Remax && app==v2.0.0"
    - slicestr: "client==KWR"
    - slicestr: "client==Zillow"
    - name: "Client Remax"
        description: "No description available"
        slicestr: "client==Remax"