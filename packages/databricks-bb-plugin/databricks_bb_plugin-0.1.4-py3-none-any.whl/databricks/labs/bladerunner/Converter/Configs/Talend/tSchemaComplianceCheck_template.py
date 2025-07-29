
fields = [%FIELDS%]
field_types = [%FIELD_TYPES%]
field_nullables = [%FIELD_NULLABLES%]

structure_fields = []
for index in range(len(fields)):
    structure_fields.append(StructField(f'"{fields[index]}"', field_types[index], nullable=field_nullables[index]))

# Define the schema
target_schema = StructType(structure_fields)

df = %SRC_NODE_NAME%

# Initialize error columns
for col_name in target_schema.fieldNames():
    df = df.withColumn(f"{col_name}_error", lit(None).cast(StringType()))

# Validate schema
validation_errors = []

for field in target_schema.fields:
    col_name = field.name
    col_type = field.dataType
    is_nullable = field.nullable

    # Check data type
    type_error_col = f"{col_name}_error"
    df = df.withColumn(
        type_error_col,
        when(
            ~col(col_name).cast(col_type).isNotNull() & col(col_name).isNotNull(),
            "Type Mismatch"
        ).otherwise(col(type_error_col))
    )

    # Check nullability
    if not is_nullable:
        df = df.withColumn(
            type_error_col,
            when(col(col_name).isNull(), "Null Value").otherwise(col(type_error_col))
        )

    validation_errors.append(type_error_col)

# Aggregate errors
df = df.withColumn(
    "errorMessage",
    when(lit(True), lit(None)).cast(StringType())
)
for error_col in validation_errors:
    df = df.withColumn(
        "errorMessage",
        when(col(error_col).isNotNull(), col(error_col)).otherwise(col("errorMessage"))
    )

# Separate valid and invalid rows
%NODE_NAME% = df.filter("errorMessage IS NULL")
invalid_df = df.filter("errorMessage IS NOT NULL")