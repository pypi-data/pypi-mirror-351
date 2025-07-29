    def %JOB_NAME% (config, spark, audit, exception):
        if config.get_bool("test", False):       
            if config.get_bool("loggable", False):
                audit.write_record(spark, \
                                "process_status", "SUCCESS", \
                                "stage", "%JOB_NAME%", \
                                "log_type", "audit",
                                "status_comment", f"""'{config.get("sql", None)}'""",
                                "row_count", str(_df.count())
                                )
        else:
            if config.get_bool("loggable", False):
                audit.write_record(spark, \
                                "process_status", "In Progress", \
                                "stage", "%JOB_NAME%", \
                                "log_type", "audit",
                                "status_comment", f"""'{config.get("sql", None)}'""",
                                "row_count", str(_df.count())
                                )
            try:


%ALL_STATEMENTS%
        
                if config.get_bool("loggable", False):
                    audit.write_record(spark, \
                                    "process_status", "SUCCESS", \
                                    "stage", "%JOB_NAME%", \
                                    "log_type", "audit",
                                    "status_comment", f"""'{config.get("sql", None)}'""",
                                    "row_count", str(_df.count())
                                    )
            except Exception as ex:
                raise exception.get_uncatch_exception("Joblet %JOB_NAME% has Failed", ex)
