# Text-to-SQL LLM Application Performance Testing Plan

## Objective
Evaluate the accuracy and consistency of a Text-to-SQL Large Language Model (LLM) application, focusing on detecting explicit errors (failed query generation) and silent errors (generated SQL queries that do not match user intent).

## Scope
- **Model**: Text-to-SQL LLM application
- **Focus**: Accuracy (correctness of generated SQL queries) and consistency (reproducible results across similar inputs)
- **Error Types**:
  - **Explicit Errors**: Failed query generation (e.g., syntax errors, incomplete queries, or model crashes).
  - **Silent Errors**: Generated queries that are syntactically correct but do not align with user intent (e.g., wrong tables, incorrect conditions, or misinterpreted aggregations).

## Testing Methodology

### 1. Test Environment Setup
- **Database**: Use a standardized relational database (e.g., PostgreSQL) with a diverse schema (multiple tables, relationships, and data types).
- **Dataset**: Create a benchmark dataset with:
  - 500+ natural language queries covering simple (single-table), medium (joins), and complex (aggregations, subqueries) scenarios.
  - Corresponding ground-truth SQL queries validated by SQL experts.
  - Edge cases (ambiguous queries, misspellings, colloquial language, and complex nested intents).
- **Tools**:
  - SQL parser (e.g., sqlparse) to validate syntax.
  - Query execution engine to compare results against ground-truth outputs.
  - Logging system to capture model outputs and errors.
- **Metrics**:
  - **Accuracy**: Percentage of generated queries matching ground-truth SQL (exact match or equivalent result set).
  - **Consistency**: Percentage of identical outputs for repeated queries with minor rephrasing.
  - **Explicit Error Rate**: Percentage of queries failing to generate valid SQL.
  - **Silent Error Rate**: Percentage of syntactically valid queries producing incorrect results.

### 2. Test Scenarios

#### A. Explicit Error Testing
- **Objective**: Identify cases where the model fails to produce valid SQL.
- **Test Cases**:
  - Invalid input queries (e.g., gibberish, incomplete sentences).
  - Complex queries exceeding model context length.
  - Queries with unsupported SQL features (e.g., database-specific functions).
- **Procedure**:
  1. Submit test queries to the model.
  2. Use SQL parser to check for syntax errors.
  3. Log cases where the model returns no output, crashes, or generates malformed SQL.
- **Expected Outcome**:
  - Explicit errors are flagged with clear error messages.
  - Error rate < 5% for standard queries.

#### B. Silent Error Testing
- **Objective**: Detect queries that are syntactically correct but do not fulfill user intent.
- **Test Cases**:
  - Ambiguous queries (e.g., “sales by month” without specifying table or column).
  - Misinterpreted aggregations (e.g., “average sales” interpreted as sum).
  - Incorrect joins (e.g., wrong table or missing join condition).
  - Queries with colloquial or domain-specific terms (e.g., “top customers” meaning highest revenue).
- **Procedure**:
  1. Submit test queries to the model.
  2. Execute generated SQL and ground-truth SQL on the test database.
  3. Compare result sets for equivalence (row count, values, and schema).
  4. Manually review discrepancies to confirm silent errors.
- **Expected Outcome**:
  - Silent error rate < 10% for standard queries.
  - Common silent error patterns (e.g., wrong aggregations) identified for model improvement.

#### C. Accuracy Testing
- **Objective**: Measure how often the model generates correct SQL queries.
- **Test Cases**:
  - Simple queries (e.g., “select all employees”).
  - Medium queries (e.g., “list orders with customer names”).
  - Complex queries (e.g., “find average order value by region for 2024”).
- **Procedure**:
  1. Submit benchmark queries to the model.
  2. Compare generated SQL to ground-truth SQL using exact match and result set equivalence.
  3. Calculate accuracy metrics.
- **Expected Outcome**:
  - Overall accuracy > 85% for benchmark queries.
  - Higher accuracy (> 95%) for simple queries.

#### D. Consistency Testing
- **Objective**: Ensure the model produces consistent outputs for similar inputs.
- **Test Cases**:
  - Rephrased queries (e.g., “show all employees” vs. “list every employee”).
  - Queries with minor variations in wording or punctuation.
- **Procedure**:
  1. Submit pairs of equivalent queries multiple times (e.g., 5 runs per query).
  2. Compare generated SQL outputs for identical structure and results.
  3. Calculate consistency metrics.
- **Expected Outcome**:
  - Consistency > 90% for rephrased queries.

### 3. Test Execution Plan
- **Phase 1: Setup (1 week)**:
  - Prepare database schema and benchmark dataset.
  - Configure testing tools and environment.
- **Phase 2: Testing (2 weeks)**:
  - Run automated tests for explicit and silent errors.
  - Execute accuracy and consistency tests.
  - Log all results and errors.
- **Phase 3: Analysis (1 week)**:
  - Analyze test results to calculate metrics.
  - Identify patterns in errors (e.g., specific query types causing silent errors).
  - Document findings in a report.
- **Phase 4: Reporting (1 day)**:
  - Present results to stakeholders with recommendations for model improvements.

### 4. Evaluation Criteria
- **Success Criteria**:
  - Explicit error rate < 5%.
  - Silent error rate < 10%.
  - Overall accuracy > 85%.
  - Consistency > 90%.
- **Failure Criteria**:
  - Explicit error rate > 10%.
  - Silent error rate > 20%.
  - Accuracy < 70%.
  - Consistency < 80%.

### 5. Risk Mitigation
- **Ambiguous Queries**: Use human reviewers to validate ground-truth SQL for ambiguous cases.
- **Scalability**: Limit initial dataset size to 500 queries, with plans to expand if needed.
- **Tool Limitations**: Ensure SQL parser and execution engine support the target database dialect.
- **Model Variability**: Run consistency tests multiple times to account for non-deterministic model behavior.

### 6. Deliverables
- Test dataset with queries and ground-truth SQL.
- Test execution logs and error reports.
- Performance report summarizing accuracy, consistency, and error rates.
- Recommendations for model improvements based on error patterns.

### 7. Assumptions
- The model supports the target database dialect (e.g., PostgreSQL).
- Ground-truth SQL queries are accurate and cover diverse use cases.
- Testing tools can handle the volume of queries without performance issues.