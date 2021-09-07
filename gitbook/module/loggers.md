# Loggers

 _class_ `raymon.RaymonFileLogger`\(_path='/tmp/raymon/'_, _project\_id='default'_, _reset\_file=False_\)[¶](loggers.md#raymon.RaymonFileLogger) `__init__`\(_path='/tmp/raymon/'_, _project\_id='default'_, _reset\_file=False_\)[¶](loggers.md#raymon.RaymonFileLogger.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `setup_datalogger`\(_path_, _reset\_file=False_\)[¶](loggers.md#raymon.RaymonFileLogger.setup_datalogger) `info`\(_trace\_id_, _text_\)[¶](loggers.md#raymon.RaymonFileLogger.info) `log`\(_trace\_id_, _ref_, _data_\)[¶](loggers.md#raymon.RaymonFileLogger.log) `tag`\(_trace\_id_, _tags_\)[¶](loggers.md#raymon.RaymonFileLogger.tag) _class_ `raymon.RaymonAPILogger`\(_url='https://api.raymon.ai/v0'_, _project\_id=None_, _auth\_path=None_, _env=None_\)[¶](loggers.md#raymon.RaymonAPILogger) `__init__`\(_url='https://api.raymon.ai/v0'_, _project\_id=None_, _auth\_path=None_, _env=None_\)[¶](loggers.md#raymon.RaymonAPILogger.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `info`\(_trace\_id_, _text_\)[¶](loggers.md#raymon.RaymonAPILogger.info) `log`\(_trace\_id_, _ref_, _data_\)[¶](loggers.md#raymon.RaymonAPILogger.log) `tag`\(_trace\_id_, _tags_\)[¶](loggers.md#raymon.RaymonAPILogger.tag) _class_ `raymon.loggers.RaymonLoggerBase`\(_project\_id='default'_\)[¶](loggers.md#raymon.loggers.RaymonLoggerBase) `__init__`\(_project\_id='default'_\)[¶](loggers.md#raymon.loggers.RaymonLoggerBase.__init__)

Initialize self. See help\(type\(self\)\) for accurate signature. `to_json_serializable`\(_data_\)[¶](loggers.md#raymon.loggers.RaymonLoggerBase.to_json_serializable)

Makes sure all data is JSON serializable `structure`\(_trace\_id_, _ref_, _data_\)[¶](loggers.md#raymon.loggers.RaymonLoggerBase.structure) `setup_logger`\(_fname=None_, _stdout=True_\)[¶](loggers.md#raymon.loggers.RaymonLoggerBase.setup_logger) _abstract_ `info`\(_trace\_id_, _text_\)[¶](loggers.md#raymon.loggers.RaymonLoggerBase.info) _abstract_ `log`\(_trace\_id_, _ref_, _data_\)[¶](loggers.md#raymon.loggers.RaymonLoggerBase.log) _abstract_ `tag`\(_trace\_id_, _tags_\)[¶](loggers.md#raymon.loggers.RaymonLoggerBase.tag) `parse_tags`\(_tags_\)[¶](loggers.md#raymon.loggers.RaymonLoggerBase.parse_tags)

