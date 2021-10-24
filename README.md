# CS511_MP_TEAM1

Make sure modules such as mongoDB and mysql.connector are installed, if not install them using pip.

First set up the databases.

To set up the Mongodb database, run **python insert_mongoDB.py**

To set up the MySQL database, run **mysql_table_creation.sql** in MySQL Workbench or an equivalent. Make sure there is a database called *team1* first, otherwise create one. Then run **python mysql_data.py**

To set up the Neo4j database, create a new Project in Neo4j Desktop. Set the password for the DBMS to *123456*. Go to plugins and install APOC.

Then, click "..." -> Open Folder -> Configuration, create a new file in the config folder called **apoc.conf** and add the following 2 lines:
```
apoc.import.file.enabled=true
apoc.import.file.use_neo4j_config=true
```
Afterwards, restart the database. After the database restarts, click "..." -> Open Folder -> Import, add the **sample_data.json** file to the import folder.

Finally, run **python Neo4j_data.py**.

*NOTE:* Keep the Neo4j database running in the background or most Neo4j features will not work.

To run the dashboard, run **python app.py**, then open http://localhost:8050/ or equivalently: http://127.0.0.1:8050/
