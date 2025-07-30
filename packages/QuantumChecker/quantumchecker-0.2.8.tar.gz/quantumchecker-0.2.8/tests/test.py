from pprint import pprint

from QuantumCheck import HomeworkEvaluator

if __name__ == "__main__":
    evaluator = HomeworkEvaluator()

    primary_api_key = "AIzaSyD0ptgEixhLLjCWjkyxhqDsUzO16ytQq2c"
    question = """####SQL questions:
     **1. NOT NULL Constraint**  
- Create a table named `student` with columns:  
  - `id` (integer, should **not allow NULL values**)  
  - `name` (string, can allow NULL values)  
  - `age` (integer, can allow NULL values)  
- First, create the table without the NOT NULL constraint.  
- Then, use `ALTER TABLE` to apply the NOT NULL constraint to the `id` column.  

---

#### **2. UNIQUE Constraint**  
- Create a table named `product` with the following columns:  
  - `product_id` (integer, should be **unique**)  
  - `product_name` (string, no constraint)  
  - `price` (decimal, no constraint)  
- First, define `product_id` as UNIQUE inside the `CREATE TABLE` statement.  
- Then, drop the unique constraint and add it again using `ALTER TABLE`.  
- Extend the constraint so that the combination of `product_id` and `product_name` must be unique.  

---

#### **3. PRIMARY KEY Constraint**  
- Create a table named `orders` with:  
  - `order_id` (integer, should be the **primary key**)  
  - `customer_name` (string, no constraint)  
  - `order_date` (date, no constraint)  
- First, define the primary key inside the `CREATE TABLE` statement.  
- Then, drop the primary key and add it again using `ALTER TABLE`.  

---

#### **4. FOREIGN KEY Constraint**  
- Create two tables:  
  - `category`:  
    - `category_id` (integer, primary key)  
    - `category_name` (string)  
  - `item`:  
    - `item_id` (integer, primary key)  
    - `item_name` (string)  
    - `category_id` (integer, should be a **foreign key referencing category_id in category table**)  
- First, define the foreign key inside `CREATE TABLE`.  
- Then, drop and add the foreign key using `ALTER TABLE`.  

---

#### **5. CHECK Constraint**  
- Create a table named `account` with:  
  - `account_id` (integer, primary key)  
  - `balance` (decimal, should always be greater than or equal to 0)  
  - `account_type` (string, should only accept values `'Saving'` or `'Checking'`)  
- Use `CHECK` constraints to enforce these rules.  
- First, define the constraints inside `CREATE TABLE`.  
- Then, drop and re-add the `CHECK` constraints using `ALTER TABLE`.  

---

#### **6. DEFAULT Constraint**  
- Create a table named `customer` with:  
  - `customer_id` (integer, primary key)  
  - `name` (string, no constraint)  
  - `city` (string, should have a default value of `'Unknown'`)  
- First, define the default value inside `CREATE TABLE`.  
- Then, drop and re-add the default constraint using `ALTER TABLE`.  

---

#### **7. IDENTITY Column**  
- Create a table named `invoice` with:  
  - `invoice_id` (integer, should **auto-increment starting from 1**)  
  - `amount` (decimal, no constraint)  
- Insert 5 rows into the table without specifying `invoice_id`.  
- Enable and disable `IDENTITY_INSERT`, then manually insert a row with `invoice_id = 100`.  

---

### **8. All at once**  
- Create a `books` table with:  
  - `book_id` (integer, primary key, auto-increment)  
  - `title` (string, **must not be empty**)  
  - `price` (decimal, **must be greater than 0**)  
  - `genre` (string, default should be `'Unknown'`)  
- Insert data and test if all constraints work as expected.  

---

### **9. Scenario: Library Management System**  
You need to design a simple database for a library where books are borrowed by members.  

### **Tables and Columns:**  

1. **Book** (Stores information about books)  
   - `book_id` (Primary Key)  
   - `title` (Text)  
   - `author` (Text)  
   - `published_year` (Integer)  

2. **Member** (Stores information about library members)  
   - `member_id` (Primary Key)  
   - `name` (Text)  
   - `email` (Text)  
   - `phone_number` (Text)  

3. **Loan** (Tracks which members borrow which books)  
   - `loan_id` (Primary Key)  
   - `book_id` (Foreign Key → References `book.book_id`)  
   - `member_id` (Foreign Key → References `member.member_id`)  
   - `loan_date` (Date)  
   - `return_date` (Date, can be NULL if not returned yet)  

### **Tasks:**  
1. **Understand Relationships**  
   - A **member** can borrow multiple **books**.  
   - A **book** can be borrowed by different members at different times.  
   - The **Loan** table connects `Book` and `Member` (Many-to-Many).  

2. **Write SQL Statements**  
   - Create the tables with proper constraints (Primary Key, Foreign Key).  
   - Insert at least 2-3 sample records into each table.  """


python_question = """Python Questions:
1. Decorators and Closures
Q: Write a decorator @memoize that caches the results of a function to optimize recursive calls like Fibonacci. Explain how closures are used in your implementation.

2. Metaclasses
Q: Explain what a metaclass is in Python. Write a custom metaclass that automatically registers every class created with it into a global registry dictionary.

3. Generators and Coroutines
Q: Implement a coroutine that acts as a simple event logger: it receives event messages via .send(), filters out duplicates, and yields only unique events.

4. Context Managers
Q: Create a custom context manager using a class (not contextlib) that measures the execution time of the code block inside the with statement.

5. Threading and Concurrency
Q: Write a thread-safe singleton class in Python that ensures only one instance exists even when accessed from multiple threads concurrently.

6. Metaprogramming — Dynamic Attributes
Q: Override __getattr__ and __setattr__ in a class to log every attribute access and modification, including attributes that do not exist.

7. Data Classes and Immutability
Q: Use Python’s @dataclass to create an immutable data structure representing a 3D vector. Include methods for vector addition, subtraction, and dot product.

8. Asyncio and Event Loop
Q: Write an asyncio program that concurrently fetches multiple URLs using aiohttp, limits the number of concurrent connections to 5, and prints the response status codes.

9. Descriptor Protocol
Q: Implement a descriptor class that enforces type checking on an attribute — for example, it ensures an attribute is always set to an integer.

10. Functional Programming
Q: Use Python’s functools.reduce and operator module to write a one-liner that computes the product of all even numbers in a list.
"""

question_ssis = """
    # SSIS Package: Excel & Flat File Data Integration

This SSIS package integrates data from an Excel file and a Flat File, performs transformations, and loads the data into a SQL Server table. The package includes complexities such as row-specific data extraction, custom delimiters, and the use of variables for dynamic configuration.

---

## 1. **Data Sources**

### 1.1 Excel File

- **Data starts at Row 4**, ignore rows above it.
- **Column names are in Row 5**.

#### Excel Data Sample:

| **ID** | **Name** | **Age** | **D** | **E** |
|--------|----------|---------|-------|-------|
| 1      | Alice    | 30      |       |       |
| 2      | Bob      | 25      |       |       |

---

### 1.2 Flat File

- The flat file contains a **header row** that matches the schema of the Excel file.

#### Flat File Data Sample:

| **ID** | **Name** | **Age** |
|--------|----------|---------|
| 3      | Charlie  | 35      |
| 4      | David    | 28      |

## 2. **SQL Table Configuration**

- Use an **SSIS variable** to store the destination SQL table name.
- **Challenge:**
  - If the table **does not exist**, dynamically create it using an **Execute SQL Task** based on the schema of the source data.
  - Add a **timestamp column** (`LoadDateTime`) to track when each row is processed.

---

## 3. **Transformations**

### 3.1 Derived Column Transformations
- **MonthsForAge**: Create a derived column that calculates the age in months (for example, 36 months for someone 3 years old).
- **SourceType**: Add a derived column indicating the data source (`"Excel"` or `"Flat File"`) for each row. This column will be inserted into the SQL target table.

---

## 4. **Data Integration**

- Use a **Union All** transformation to combine the data from both sources (Excel and Flat File).
  - Ensure proper column alignment and standardization before combining the data.

---

## 5. **Dynamic Configuration**

- Use **SSIS variables** to store the file paths for:
  - The Excel source.
  - The Flat File source.

---

## 6. **Data Validation and Error Logging**

### 6.1 Conditional Split Transformation
- Use a **Conditional Split** transformation to:
  - **Exclude** rows where the age is less than 18 years old.

### 6.2 Logging Failed Rows
- Log all rows that fail validation into a flat file (`ErrorLog.txt`).
- Include the **reason for failure** in the error log (e.g., "Missing Age" or "Age < 18").

---

## 7. **Final SQL Table Schema**

| Column Name      | Description                           |
|------------------|---------------------------------------|
| [All Source Columns] | From Excel/Flat File schema         |
| `MonthsForAge`   | Derived column, age in months        |
| `SourceType`     | `"Excel"` or `"Flat File"`            |
| `LoadDateTime`   | Timestamp when the row was processed  |

---

## 8. **Notes**

- Ensure **correct column mapping** and **data type alignment** across both data sources (Excel and Flat File).
- Use **Precedence Constraints** and **Data Flow Tasks** to ensure proper execution sequence.
- Optionally, use a **Script Task** for enhanced logging or custom validation logic.

---

"""


power_bi_question = """"The question includes keywords like 'Python questions', 'Sql questions', 'Power bi questions', 'SSIS questions' for you to fidure out whether answer is off topic or not"
1. Data Modeling
Q: Explain the difference between star schema and snowflake schema in Power BI. Why is star schema preferred for performance optimization?

2. DAX Calculations
Q: Write a DAX measure to calculate Year-to-Date (YTD) sales, considering a dynamic date selection from a slicer.

3. Relationships
Q: How do you configure many-to-many relationships in Power BI? Provide an example scenario and explain how to model it.

4. Power Query M Language
Q: Using Power Query M language, how would you merge two tables and keep only rows where a key exists in both tables?

5. Row-Level Security (RLS)
Q: How can you implement row-level security in Power BI to restrict data access based on the logged-in user?

6. Performance Optimization
Q: What are some best practices to optimize Power BI report performance, especially with large datasets?

7. Calculated Columns vs Measures
Q: What is the difference between calculated columns and measures in Power BI? When should you use each?

8. Visualizations and Custom Visuals
Q: How do you import and use a custom visual in Power BI? Provide an example of when you might need a custom visual.

9. Time Intelligence
Q: Write a DAX expression to calculate the percentage growth in sales compared to the previous year.

10. Data Refresh
Q: Explain the different types of data refresh options available in Power BI and their use cases (import, DirectQuery, live connection).


"""
backup_keys = [
        "BACKUP_KEY_1",
        "BACKUP_KEY_2",
        "BACKUP_KEY_3",
        "BACKUP_KEY_4",
        "BACKUP_KEY_5",
    ]


pythonbek ="""
    Create a program that takes a float number as input and rounds it to 2 decimal places.
    Write a Python file that asks for three numbers and outputs the largest and smallest.
    Create a program that converts kilometers to meters and centimeters.
    Write a program that takes two numbers and prints out the result of integer division and theremainder.
    Make a program that converts a given Celsius temperature to Fahrenheit.
    Create a program that accepts a number and returns the last digit of that number.
    Create a program that takes a number and checks if it’s even or not.
    String Questions:
    Create a program to ask name and year of birth from user and tell them their age.
    
    Extract car names from this text: txt = 'LMaasleitbtui'
    
    Write a Python program to:
    
    Take a string input from the user.
    Print the length of the string.
    Convert the string to uppercase and lowercase.
    Write a Python program to check if a given string is palindrome or not.
    
    What is a Palindrome String? A string is called a palindrome if the reverse of the string is the same as the original one. Example: “madam”, “racecar”, “12321”.
    
    Write a program that counts the number of vowels and consonants in a given string.
    
    Write a Python program to check if one string contains another.
    
    Ask the user to input a sentence and a word to replace. Replace that word with another word provided by the user.
    Example:
    
    Input sentence: "I love apples."
    Replace: "apples"
    With: "oranges"
    Output: "I love oranges."
    Write a program that asks the user for a string and prints the first and last characters of the string.
    
    Ask the user for a string and print the reversed version of it.
    
    Write a program that asks the user for a sentence and prints the number of words in it.
    
    Write a program to check if a string contains any digits.
    
    Write a program that takes a list of words and joins them into a single string, separated by a character (e.g., - or ,).
    
    Ask the user for a string and remove all spaces from it.
    
    Write a program to ask for two strings and check if they are equal or not.
    
    Ask the user for a sentence and create an acronym from the first letters of each word.
    Example:
    
    Input: "World Health Organization"
    Output: "WHO"
    Write a program that asks the user for a string and a character, then removes all occurrences of that character from the string.
    
    Ask the user for a string and replace all the vowels with a symbol (e.g., *).
    
    Write a program that checks if a string starts with one word and ends with another.
    Example:
    
    Input: "Python is fun!"
    Starts with: "Python"
    Ends with: "fun!"
    Boolean Data Type Questions:
    Write a program that accepts a username and password and checks if both are not empty.
    Create a program that checks if two numbers are equal and outputs a message if they are.
    Write a program that checks if a number is positive and even.
    Write a program that takes three numbers and checks if all of them are different.
    Create a program that accepts two strings and checks if they have the same length.
    Create a program that accepts a number and checks if it’s divisible by both 3 and 5.
    Write a program that checks if the sum of two numbers is greater than 50.8. Create a program that checks if a given number is between 10 and 20 (inclusive)
"""

result = evaluator.evaluate_from_content(
        question_content=pythonbek,
        answer_path="../tests/answer/answer.dtsx",
        api_key=primary_api_key,
        backup_api_keys=backup_keys
    )

pprint(result)





